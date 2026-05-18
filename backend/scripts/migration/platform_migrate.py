"""平台库（zt_platform）智能 alembic 入口

为什么要这一层包装？
  * 直接 `alembic upgrade head` 在「老库纳管」场景会失败：
    - 库里已有业务表（sys_user / sys_tenant 等）
    - alembic_version 表却不存在 → alembic 认为要从 baseline 开始建表
    - baseline 的 metadata.create_all 虽然幂等（IF NOT EXISTS），
      但仍可能遇到 charset/comment/索引差异
  * 因此首次纳管老库应当 `alembic stamp head` 把版本号刻上去，绕开重建。

策略：
  ┌─────────────────────────────────┬──────────────────────┐
  │ 平台库情况                      │ 行为                 │
  ├─────────────────────────────────┼──────────────────────┤
  │ alembic_version 表存在          │ alembic upgrade head │
  │ 不存在 + 库里有 sys_user 表     │ alembic stamp head   │
  │ 不存在 + 库为空                 │ alembic upgrade head │
  └─────────────────────────────────┴──────────────────────┘

用法：
  python -m scripts.migration.platform_migrate           # 智能模式（默认）
  python -m scripts.migration.platform_migrate --upgrade # 强制 upgrade head
  python -m scripts.migration.platform_migrate --stamp   # 强制 stamp head
  python -m scripts.migration.platform_migrate --status  # 仅打印当前版本

由 deploy.sh 在 sync_platform_schema 阶段自动调用。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

from scripts.migration._paths import (
    ALEMBIC_INI,
    BACKEND_DIR,
    ensure_backend_on_syspath,
)

ensure_backend_on_syspath()

# 「老库判定」用的关键业务表清单：任一存在即视为老库
LEGACY_INDICATOR_TABLES = ["sys_user", "sys_tenant"]


def _alembic_cfg():
    """构造 alembic Config，强制使用绝对 script_location，避免名字冲突。

    注意：本仓库 alembic 版本目录就叫 `backend/alembic/`，而 alembic 又是
    已安装的 Python 包；如果切到 backend 当 cwd 再 import，`alembic.config`
    会优先解析到本地目录而非站点包。改用绝对路径 + 程序化 API 规避之。
    """
    from alembic.config import Config
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(ALEMBIC_INI.parent / "migrations"))
    return cfg


def _alembic(args: List[str]) -> int:
    from alembic import command
    cfg = _alembic_cfg()
    sub = args[0]
    rest = args[1:]
    print(f"[INFO] $ alembic {' '.join(args)}")
    try:
        if sub == "current":
            command.current(cfg)
        elif sub == "upgrade":
            command.upgrade(cfg, rest[0] if rest else "head")
        elif sub == "stamp":
            command.stamp(cfg, rest[0] if rest else "head")
        elif sub == "history":
            command.history(cfg)
        elif sub == "heads":
            command.heads(cfg)
        else:
            print(f"[ERROR] 不支持的 alembic 子命令: {sub}", file=sys.stderr)
            return 2
        return 0
    except Exception as e:
        print(f"[ERROR] alembic {sub} 失败：{type(e).__name__}: {e}",
              file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def _has_alembic_version(engine) -> bool:
    from sqlalchemy import inspect
    return "alembic_version" in inspect(engine).get_table_names()


def _has_legacy_tables(engine) -> bool:
    from sqlalchemy import inspect
    existing = set(inspect(engine).get_table_names())
    return any(t in existing for t in LEGACY_INDICATOR_TABLES)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="平台库 alembic 智能入口（auto = stamp 老库 / upgrade 新库）",
    )
    parser.add_argument("--upgrade", action="store_true",
                        help="强制 alembic upgrade head（跳过自动检测）")
    parser.add_argument("--stamp", action="store_true",
                        help="强制 alembic stamp head（仅记录版本号，不执行 DDL）")
    parser.add_argument("--status", action="store_true",
                        help="仅打印当前 alembic current 版本")
    args = parser.parse_args()

    if args.status:
        return _alembic(["current"])
    if args.stamp and args.upgrade:
        print("[ERROR] --stamp 与 --upgrade 互斥", file=sys.stderr)
        return 2
    if args.upgrade:
        return _alembic(["upgrade", "head"])
    if args.stamp:
        return _alembic(["stamp", "head"])

    # ---- auto 模式 ----
    from sqlalchemy import create_engine
    from app.core.config import get_settings

    settings = get_settings()
    url = settings.platform_db_url_sync
    print(f"[INFO] 检测平台库：{settings.platform_database_name}")
    try:
        engine = create_engine(url, pool_pre_ping=True)
        engine.connect().close()
    except Exception as e:
        print(f"[ERROR] 连接平台库失败：{type(e).__name__}: {e}", file=sys.stderr)
        return 2

    has_av = _has_alembic_version(engine)
    has_legacy = _has_legacy_tables(engine)
    engine.dispose()

    print(f"[INFO] alembic_version 表存在：{has_av}；老库特征表存在：{has_legacy}")

    if has_av:
        print("[INFO] 平台库已被 alembic 纳管，执行 upgrade head")
        return _alembic(["upgrade", "head"])
    if has_legacy:
        print("[INFO] 老库首次纳管，执行 stamp head（不重建已有表）")
        rc = _alembic(["stamp", "head"])
        if rc != 0:
            return rc
        # stamp 成功后再 upgrade，保险起见把后续真实 versioned 迁移也跑一次
        # （此时 head 已经是最新，等价于 no-op，但能让命令行始终以 upgrade 收尾）
        return _alembic(["upgrade", "head"])
    print("[INFO] 全新平台库，执行 upgrade head 重建所有表")
    return _alembic(["upgrade", "head"])


if __name__ == "__main__":
    sys.exit(main())
