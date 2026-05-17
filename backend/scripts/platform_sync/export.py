"""
export — 从 dev console 平台库拉取菜单/版本/功能/版本-功能映射，写入仓库快照

用法（开发者在 dev 环境改完 console 后执行）：
    python -m scripts.platform_sync export

流程：
    1. 加载 envs/.env.dev
    2. 登录 Console API
    3. 依次调用 5 个 exporter 拿数据
    4. 校验闭包/唯一性/引用完整性
    5. 写入 snapshots/*.json 与 _meta.json
    6. 打印与上次快照的差异，提示 git commit

设计理念：零参数。生产环境是「被同步」的，不应反向作为快照源；
若极端场景需要从 prod 拉一份基线（如灾难恢复），用 `--env prod` 显式
指定（默认仍是 dev）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPT = Path(__file__).resolve()
_BACKEND = _SCRIPT.parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from scripts.platform_sync.config import load_config, ConfigError, REPO_ROOT
from scripts.platform_sync.http_client import ConsoleClient, ConsoleApiError
from scripts.platform_sync.exporters import EXPORTERS
from scripts.platform_sync.validators import validate_snapshots
from scripts.platform_sync.snapshot_io import (
    read_json,
    write_json,
    write_meta,
    make_meta,
    META_FILENAME,
)
from scripts.platform_sync.diff_utils import (
    diff_list,
    diff_version_feature,
    format_summary,
    format_detail,
    current_user,
    KEY_FUNCS,
)


def _print_diff(new_data: Dict[str, Any], snapshot_dir: Path) -> bool:
    """与上次快照对比，输出统计与详情；返回是否有变化"""
    print("\n========== 快照变化对比 ==========")
    any_change = False
    for key in EXPORTERS.keys():
        _, filename = EXPORTERS[key]
        old = read_json(snapshot_dir / filename)
        new = new_data.get(key)

        if old is None:
            print(f"  [N] {key}: 首次生成（无上次快照）")
            any_change = True
            continue

        if key == "version_feature":
            d = diff_version_feature(new or {}, old or {})
        else:
            d = diff_list(new or [], old or [], KEY_FUNCS[key])

        print(format_summary(key, d))
        if not d.is_empty:
            any_change = True
            for line in format_detail(key, d):
                print(line)

    if not any_change:
        print("  >>> 与上次快照完全一致，本次 export 不会改动文件")
    print("==================================\n")
    return any_change


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 dev console 平台库拉取元数据并写入仓库快照"
    )
    parser.add_argument(
        "--env",
        default="dev",
        choices=["dev", "prod"],
        help="拉取源环境（默认 dev；从 prod 拉取仅供灾难恢复基线场景）",
    )
    parser.add_argument(
        "--check-frontend",
        action="store_true",
        help=(
            "校验 client_menu / platform_menu 中每条 component 字段在前端 views 下"
            "都能找到对应 .vue 文件；任一缺失视为致命错误。"
        ),
    )
    args = parser.parse_args()

    try:
        cfg = load_config(args.env)
    except ConfigError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    if cfg.env == "prod":
        print(
            "[WARN] 你正在从 prod 拉取快照。\n"
            "  正常发版流程是从 dev 导出快照、由 prod 同步消费；\n"
            "  仅在灾难恢复或重建快照基线场景才应该从 prod 反向拉。\n"
        )

    print(f">>> 拉取源: env={cfg.env}  api={cfg.api_base}  account={cfg.admin_phone}")

    # ---- 拉取 ----
    new_data: Dict[str, Any] = {}
    try:
        with ConsoleClient(cfg) as client:
            for key, (exporter, filename) in EXPORTERS.items():
                print(f"  - 拉取 {key} ({filename}) ...", end="", flush=True)
                data = exporter(client)
                count = len(data) if hasattr(data, "__len__") else "?"
                print(f" 共 {count} 条")
                new_data[key] = data
    except ConsoleApiError as e:
        print(f"\n[ERROR] Console 接口错误: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"\n[ERROR] 拉取失败: {e!r}", file=sys.stderr)
        return 3

    # ---- 校验 ----
    frontend_dirs = None
    if args.check_frontend:
        frontend_dirs = {
            "client_menu": REPO_ROOT / "frontend" / "client" / "src" / "views",
            "platform_menu": REPO_ROOT / "frontend" / "console" / "src" / "views",
        }
    report = validate_snapshots(new_data, frontend_dirs=frontend_dirs)
    print("\n" + report.format())
    if not report.ok:
        print("\n[ERROR] 校验未通过，已中止写盘", file=sys.stderr)
        return 4

    # ---- 与上次快照对比 ----
    _print_diff(new_data, cfg.snapshot_dir)

    # ---- 写盘 ----
    cfg.snapshot_dir.mkdir(parents=True, exist_ok=True)
    for key, (_, filename) in EXPORTERS.items():
        out_path = cfg.snapshot_dir / filename
        write_json(out_path, new_data[key])
        print(f"  [OK] 写入 {out_path.relative_to(REPO_ROOT)}")

    meta = make_meta(
        env=cfg.env,
        api_base=cfg.api_base,
        repo_root=REPO_ROOT,
        exported_by=current_user(),
    )
    write_meta(cfg.snapshot_dir, meta)
    print(f"  [OK] 写入元数据 {(cfg.snapshot_dir / META_FILENAME).relative_to(REPO_ROOT)}")
    print(
        "\n>>> export 完成。请 git diff 检查变更：\n"
        "      git add backend/scripts/platform_sync/snapshots/\n"
        "      git commit -m 'snapshot: ...'\n"
        "      git push"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
