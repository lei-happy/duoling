"""
sync — 把仓库快照应用到目标环境（通常是 prod）

用法：
    python -m scripts.platform_sync sync                # 默认 --env prod，交互式
    python -m scripts.platform_sync sync --yes          # 自动确认，CI 用
    python -m scripts.platform_sync sync --plan         # 只打印差异（不询问、不写库）
    python -m scripts.platform_sync sync --env dev      # 极少用，验证场景

流程（apply 模式）：
    1. 加载 envs/.env.prod
    2. 通过 console API 拉取目标环境当前数据
    3. 与仓库 snapshots/*.json 逐项对比
    4. 打印变更摘要 + 详情
    5. 若 0 差异 → 提示"无须同步"，退出 0
    6. 若有差异 → 询问 (y/N)
    7. 用户输入 y → 顺序执行 4 个 seed 脚本：
         python scripts/seed/seed_product_versions.py            # 产品版本
         python scripts/seed/seed_product_features.py            # 功能模块 + 版本-功能关联
         python scripts/seed/seed_client_menus.py --app-type client   --force-all
         python scripts/seed/seed_client_menus.py --app-type platform --force-all
    8. 应用后再拉取一次目标环境，确认 0 差异

退出码（约定）：
    0  : 无差异 / 应用成功 / 用户取消
    1  : 应用后自检仍有差异
    2  : 配置错误（缺 .env / 缺快照 / 参数错误）
    3  : 拉取目标环境失败（API/网络/凭证）
    4  : seed 脚本执行失败
    10 : --plan 模式下检测到差异，需要 apply（供 deploy 脚本判断）
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPT = Path(__file__).resolve()
_BACKEND = _SCRIPT.parents[2]  # backend/
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from scripts.platform_sync.config import load_config, ConfigError, REPO_ROOT
from scripts.platform_sync.http_client import ConsoleClient, ConsoleApiError
from scripts.platform_sync.exporters import EXPORTERS
from scripts.platform_sync.snapshot_io import read_json
from scripts.platform_sync.validators import validate_snapshots
from scripts.platform_sync.diff_utils import (
    active_snapshot_rows,
    diff_list,
    diff_version_feature,
    format_summary,
    format_detail,
    KEY_FUNCS,
)


def _ensure_snapshots_exist(snapshot_dir: Path) -> bool:
    """确保仓库内 5 个快照文件齐全。否则提示并退出"""
    missing: List[str] = []
    for key, (_, filename) in EXPORTERS.items():
        if not (snapshot_dir / filename).is_file():
            missing.append(filename)
    if missing:
        print(
            f"[ERROR] 仓库内缺少快照文件: {missing}\n"
            f"  说明：本命令需要 dev 端先运行 export 生成事实源。\n"
            f"  请联系开发者先在 dev 跑：\n"
            f"      cd backend && python -m scripts.platform_sync export\n"
            f"  并 git push 后再执行 sync。",
            file=sys.stderr,
        )
        return False
    return True


def _fetch_live(client: ConsoleClient) -> Dict[str, Any]:
    """从目标环境拉取 5 个数据集"""
    out: Dict[str, Any] = {}
    for key, (exporter, _) in EXPORTERS.items():
        print(f"  - 读取 {key} ...", end="", flush=True)
        out[key] = exporter(client)
        print(" OK")
    return out


def _compare(
    snapshot_dir: Path, live: Dict[str, Any]
) -> Dict[str, Any]:
    """快照 vs 目标环境，返回每项的 diff 对象"""
    diffs: Dict[str, Any] = {}
    for key, (_, filename) in EXPORTERS.items():
        repo = read_json(snapshot_dir / filename)
        if key == "version_feature":
            d = diff_version_feature(repo or {}, live.get(key) or {})
        else:
            repo_rows = repo or []
            live_rows = live.get(key) or []
            if isinstance(repo_rows, list):
                dropped = [
                    r for r in repo_rows if int(r.get("is_deleted") or 0) != 0
                ]
                if dropped:
                    names = ", ".join(
                        str(
                            r.get("menu_code")
                            or r.get("feature_code")
                            or r.get("menu_name")
                            or "?"
                        )
                        for r in dropped[:10]
                    )
                    extra = " ..." if len(dropped) > 10 else ""
                    print(
                        f"[WARN] {key} 快照含 {len(dropped)} 条 is_deleted=1 记录，"
                        f"对比时已忽略: {names}{extra}\n"
                        f"       请从 snapshots/{filename} 删除这些墓碑"
                        f"（export 不会写出已删菜单）。"
                    )
                repo_rows = active_snapshot_rows(repo_rows)
            if isinstance(live_rows, list):
                live_rows = active_snapshot_rows(live_rows)
            d = diff_list(repo_rows, live_rows, KEY_FUNCS[key])
        diffs[key] = d
    return diffs


def _print_diffs(
    diffs: Dict[str, Any], detail: bool = True, max_each: int = 30
) -> int:
    """打印摘要 + 详情，返回总变更数"""
    total = 0
    print("\n========== 即将应用以下变更到目标环境 ==========")
    for key, d in diffs.items():
        print(format_summary(key, d))
        total += d.total
    if total > 0 and detail:
        print("\n----- 详情 -----")
        for key, d in diffs.items():
            for line in format_detail(key, d, max_each=max_each):
                print(line)
    print("================================================\n")
    return total


def _ask_confirm(env: str, total: int) -> bool:
    """交互式确认；返回是否继续"""
    if not sys.stdin.isatty() and os.environ.get("PLATFORM_SYNC_YES") != "1":
        print(
            "[ERROR] 非交互终端运行 sync，需设置环境变量 PLATFORM_SYNC_YES=1 才能跳过确认。"
            f"\n  本次涉及变更 {total} 项，为安全起见已中止。",
            file=sys.stderr,
        )
        return False
    if os.environ.get("PLATFORM_SYNC_YES") == "1":
        print(f"[INFO] 检测到 PLATFORM_SYNC_YES=1，自动确认（变更 {total} 项）")
        return True
    prompt = f"确认把以上变更应用到 {env}？(y/N): "
    try:
        ans = input(prompt).strip().lower()
    except EOFError:
        ans = ""
    return ans in ("y", "yes")


def _run_seed(script_relpath: str, args: List[str]) -> int:
    """以 backend/ 为 cwd 执行 seed 脚本，透传输出"""
    cmd = [sys.executable, script_relpath, *args]
    print(f"\n[RUN] {' '.join(cmd)}  (cwd=backend)")
    proc = subprocess.run(cmd, cwd=str(_BACKEND))
    return proc.returncode


def _prefix_client_menu_fix() -> bool:
    """
    在执行 client menu seed 之前自动跑一次 fix_client_menu_v2，
    清理"已软删的非 client 记录占用 client 快照 ID"这类冲突。

    设计原因：
      - client 菜单 ID 在产品迭代中会持续增长（v2.0 新增了 260+、运营调度 430+ 等）；
      - 部分新 ID 在生产 DB 上已被历史 platform/console 菜单占用、且已软删；
      - 这类冲突如果不清理，seed_client_menus.py 会以 INSERT 主键冲突中止；
      - 该脚本已升级为"基于 client_menu.json 快照自动扫描"，幂等可重复执行；
      - 在 seed 之前自动跑一次，使部署流程具备自愈能力。

    任何修复失败只打 WARN，不直接拒绝后续 seed（保留人工兜底的可见性）。
    """
    print("\n[FIX] 预清理 client 菜单 ID 冲突 (fix_client_menu_v2 --auto-scan)")
    try:
        from scripts.fix.fix_client_menu_v2 import run_fix  # 延迟导入
    except Exception as e:  # pragma: no cover
        print(f"  [WARN] 无法导入 fix_client_menu_v2: {e!r}，跳过预清理")
        return True
    try:
        run_fix(dry_run=False, soft_delete_orphans=False, auto_scan=True)
    except Exception as e:  # pragma: no cover
        print(f"  [WARN] fix_client_menu_v2 执行失败: {e!r}，将继续后续 seed")
        return True
    return True


def _prefix_platform_menu_fix() -> bool:
    """platform 菜单 seed 前清理跨 app_type 的 ID 冲突（幂等）。"""
    print("\n[FIX] 预清理 platform 菜单 ID 冲突 (fix_platform_menu_id_conflicts)")
    try:
        from scripts.fix.fix_platform_menu_id_conflicts import run_fix
    except Exception as e:  # pragma: no cover
        print(f"  [WARN] 无法导入 fix_platform_menu_id_conflicts: {e!r}，跳过预清理")
        return True
    try:
        run_fix(dry_run=False)
    except Exception as e:  # pragma: no cover
        print(f"  [WARN] fix_platform_menu_id_conflicts 执行失败: {e!r}，将继续后续 seed")
    return True


def _apply(snapshot_dir: Path) -> bool:
    """
    顺序执行 seed 脚本；任何一个失败立刻终止。

    顺序设计原因：
      0. fix_client_menu_v2：先清理已知/扫描出的 client ID 冲突（幂等，无冲突即 noop）
      1. product_versions：先建版本（lite/standard/pro），后续 version_feature 需要这些版本
      2. product_features：写 feature + version_feature 关联（依赖版本已存在）
      3. client_menus：客户端菜单（依赖 feature_code 已存在）
      4. platform_menus：Console 后台菜单（独立，最后跑）
    """
    _prefix_client_menu_fix()

    steps = [
        ("scripts/seed/seed_product_versions.py", []),
        ("scripts/seed/seed_product_features.py", []),
        ("scripts/seed/seed_client_menus.py", ["--app-type", "client", "--force-all"]),
    ]
    for script, args in steps:
        rc = _run_seed(script, args)
        if rc != 0:
            label = f"{script} {' '.join(args)}".strip()
            print(
                f"[ERROR] {label} 退出码 {rc}，已中止。\n"
                f"  目标库可能处于半同步状态：前面已成功的 seed 已 commit；\n"
                f"  请检查日志后排查具体失败原因，修好之后重跑 sync 即可（幂等）。",
                file=sys.stderr,
            )
            return False

    _prefix_platform_menu_fix()

    rc = _run_seed(
        "scripts/seed/seed_client_menus.py",
        ["--app-type", "platform", "--force-all"],
    )
    if rc != 0:
        label = "scripts/seed/seed_client_menus.py --app-type platform --force-all"
        print(
            f"[ERROR] {label} 退出码 {rc}，已中止。\n"
            f"  目标库可能处于半同步状态：前面已成功的 seed 已 commit；\n"
            f"  请检查日志后排查具体失败原因，修好之后重跑 sync 即可（幂等）。",
            file=sys.stderr,
        )
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="把仓库快照应用到目标环境（默认 prod）"
    )
    parser.add_argument(
        "--env",
        default="prod",
        choices=["dev", "prod"],
        help="同步目标环境（默认 prod）",
    )
    parser.add_argument(
        "--show-detail",
        action="store_true",
        default=True,
        help="打印每项变更详情（默认开）",
    )
    parser.add_argument(
        "--no-detail",
        dest="show_detail",
        action="store_false",
        help="只打印摘要，不展开每条变更",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="跳过交互确认（CI 环境用，等同设置 PLATFORM_SYNC_YES=1）",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help=(
            "只读模式：只打印目标环境与仓库快照的差异，不询问、不写库。"
            "退出码 0=无差异 / 10=有差异 / 2=配置错误 / 3=拉取失败。"
            "适合自动化部署脚本先 plan、再决定是否 apply。"
        ),
    )
    parser.add_argument(
        "--check-frontend",
        action="store_true",
        help=(
            "在比对/写库前先离线校验快照里的 component 字段是否在前端 views 下存在。"
            "任一缺失视为致命错误，立刻中止。"
        ),
    )
    args = parser.parse_args()

    if args.yes and args.plan:
        print("[ERROR] --plan 与 --yes 互斥（plan 不会写库）", file=sys.stderr)
        return 2

    if args.yes:
        os.environ["PLATFORM_SYNC_YES"] = "1"

    # ---- 加载目标环境配置 ----
    try:
        cfg = load_config(args.env)
    except ConfigError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    # ---- 检查快照齐全 ----
    if not _ensure_snapshots_exist(cfg.snapshot_dir):
        return 2

    # ---- 可选：前端组件存在性离线校验 ----
    if args.check_frontend:
        snapshots: Dict[str, Any] = {}
        for key, (_, filename) in EXPORTERS.items():
            snapshots[key] = read_json(cfg.snapshot_dir / filename)
        report = validate_snapshots(
            snapshots,
            frontend_dirs={
                "client_menu": REPO_ROOT / "frontend" / "client" / "src" / "views",
                "platform_menu": REPO_ROOT / "frontend" / "console" / "src" / "views",
            },
        )
        print(report.format())
        if not report.ok:
            print(
                "\n[ERROR] 快照与前端工程不一致，已中止 sync。"
                "请修复 component 路径或补齐 .vue 文件后重试。",
                file=sys.stderr,
            )
            return 4

    print(f">>> 同步目标: env={cfg.env}  api={cfg.api_base}")

    # ---- 拉取目标环境数据 ----
    try:
        with ConsoleClient(cfg) as client:
            live = _fetch_live(client)
    except ConsoleApiError as e:
        print(f"\n[ERROR] Console 接口错误: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"\n[ERROR] 拉取目标环境失败: {e!r}", file=sys.stderr)
        return 3

    # ---- 对比 ----
    diffs = _compare(cfg.snapshot_dir, live)
    total = _print_diffs(diffs, detail=args.show_detail)
    if total == 0:
        print("[OK] 目标环境与仓库快照完全一致，无须同步。")
        return 0

    # ---- plan 模式：只读、按差异状态返回特殊退出码，不进入交互/写库 ----
    if args.plan:
        print(f"[PLAN] 检测到 {total} 项差异，--plan 模式不会写库。")
        print("       如需应用，去掉 --plan 或加 --yes 重新执行。")
        return 10

    # ---- 交互确认 ----
    if not _ask_confirm(args.env, total):
        print("[CANCEL] 已取消，未对目标环境做任何修改。")
        return 0

    # ---- 执行 seed 脚本 ----
    if not _apply(cfg.snapshot_dir):
        return 4

    # ---- 应用后自检 ----
    print("\n>>> 应用完成，重新拉取目标环境进行自检 ...")
    try:
        with ConsoleClient(cfg) as client:
            after = _fetch_live(client)
    except Exception as e:
        print(f"[WARN] 自检拉取失败（不影响应用结果）: {e!r}", file=sys.stderr)
        print("[OK] seed 脚本已执行完毕，请手动通过 console 或 SQL 验证。")
        return 0

    after_diffs = _compare(cfg.snapshot_dir, after)
    remaining = sum(d.total for d in after_diffs.values())
    if remaining == 0:
        print("\n[OK] 目标环境与仓库快照完全一致，sync 成功。")
        return 0

    print(
        f"\n[WARN] 应用后仍有 {remaining} 项差异（详情见下），可能原因：\n"
        f"  1) seed 脚本默认 preserve-ui 模式保留了某些 UI 字段\n"
        f"  2) 数据库存在快照里没有的脏记录（如孤立菜单），需手工清理\n"
        f"  3) 某条 feature 引用了不存在的版本，已被 seed 跳过"
    )
    _print_diffs(after_diffs, detail=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
