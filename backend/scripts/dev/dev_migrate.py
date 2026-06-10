"""开发环境一键迁移脚本（审批中心 + 组织负责人）

按正确顺序应用本地 dev 环境的全部数据库变更与种子，覆盖：
  - 平台库结构（alembic）
  - 产品功能清单（含 required_tables，决定租户库要建哪些 biz_* 表）
  - 租户库结构：
      Phase 1   按 feature.required_tables 自动建表（审批中心 7 张 biz_approval_*）
      Phase 1.5 reconcile 自动补可空列（biz_social_capacity.approval_instance_id /
                biz_department.leader_user_id 即便没迁移文件也会被补上）
      Phase 2   versioned migrations（20260610_001/002/003 加列，由 runner 自动发现）
  - 租户业务种子：审批中心默认流程模板（草稿态）

⚠ 顺序很关键：
  seed_product_features 必须在 runner 之前跑，否则 runner 读不到
  sys_product_feature.required_tables，审批中心的新表不会被创建。

用法（在 backend/ 目录下）：
    python -m scripts.dev.dev_migrate              # 全部租户
    python -m scripts.dev.dev_migrate --tenant 1001
    python -m scripts.dev.dev_migrate --dry-run    # 仅租户库 runner 走 dry-run，其余跳过写库步骤
    python -m scripts.dev.dev_migrate --skip-platform   # 跳过平台库 alembic（无平台结构变更时）

注意：本脚本仅用于开发环境。生产请走 deploy/deploy.sh 的标准流程。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# backend/ 根目录（scripts/dev/dev_migrate.py 向上两级）
BACKEND_DIR = Path(__file__).resolve().parents[2]


def _run(title: str, cmd: list[str]) -> None:
    print("\n" + "=" * 70)
    print(f">>> {title}")
    print(f"    $ {' '.join(cmd)}")
    print("=" * 70)
    result = subprocess.run(cmd, cwd=str(BACKEND_DIR))
    if result.returncode != 0:
        print(f"\n[FAIL] 步骤「{title}」返回码 {result.returncode}，中止后续步骤。")
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="开发环境一键迁移（审批中心 + 组织负责人）")
    parser.add_argument("--tenant", default=None, help="只处理指定 tenant_code")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="租户库 runner 走 dry-run（只看计划不写库）；同时跳过种子写库",
    )
    parser.add_argument(
        "--skip-platform",
        action="store_true",
        help="跳过平台库 alembic 迁移（无平台结构变更时可用）",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="跳过种子（产品功能清单 / 默认审批模板）",
    )
    args = parser.parse_args()

    py = sys.executable

    # 1) 平台库结构（alembic）
    if not args.skip_platform:
        _run("平台库 alembic 迁移", [py, "-m", "scripts.migration.platform_migrate"])

    # 2) 产品功能清单（含 required_tables）—— 必须在 runner 之前
    if not args.skip_seed and not args.dry_run:
        _run(
            "同步产品功能清单（含审批中心 required_tables）",
            [py, "-m", "scripts.seed.seed_product_features"],
        )

    # 3) 租户库结构（建表 + 补列 + versioned migrations）
    runner_cmd = [py, "-m", "scripts.migration.runner"]
    if args.tenant:
        runner_cmd += ["--tenant", args.tenant]
    if args.dry_run:
        runner_cmd += ["--dry-run"]
    _run("租户库 schema 迁移（Phase1 建表 / 1.5 补列 / 2 versioned）", runner_cmd)

    # 4) 租户业务种子：审批中心默认流程模板（草稿态）
    if not args.skip_seed and not args.dry_run:
        seed_flows = [py, str(BACKEND_DIR / "scripts" / "seed" / "seed_approval_flows.py")]
        if args.tenant:
            seed_flows.append(args.tenant)
        _run("下发审批中心默认流程模板（草稿）", seed_flows)

    print("\n" + "=" * 70)
    if args.dry_run:
        print("[OK] dry-run 完成（未写库）。确认计划无误后去掉 --dry-run 正式执行。")
    else:
        print("[OK] 开发环境迁移完成：审批中心表/列 + 组织负责人列 + 默认模板均已就位。")
        print("    提醒：默认审批模板为草稿态，需到「审批流程配置」补齐审批人并发布后，")
        print("    社会运力准入审核才会改走审批引擎；未发布前仍走旧单级直审。")
    print("=" * 70)


if __name__ == "__main__":
    main()
