"""
为已有租户补建社会运力池模块的 5 张表：

    biz_social_capacity            主表（核心信息 + 双状态 + 评级预留）
    biz_social_capacity_driver     司机详情（1:1）
    biz_social_capacity_vehicle    车辆详情（1:1，含轻挂集成）
    biz_social_capacity_account    结算账户（1:N，默认账户互斥）
    biz_social_capacity_audit      审核/状态流水（1:N）

适用场景：
    - 平台已存在租户（db_initialized=1）需要启用 capacity_social_list 功能时；
    - 通常应通过激活 product_feature_code=capacity_social_list 自动建表，
      但如果租户已存在历史数据且没有走"版本激活"流程，可用本脚本一次性补建。

设计要点：
    - 幂等：表已存在则跳过；不会 DROP/ALTER 现有表；
    - 仅 CREATE TABLE：使用 SQLAlchemy metadata.create_all 按 ORM 当前定义建表；
    - 默认遍历所有 db_initialized=1 的非删除租户，可指定单个租户；
    - 失败租户单独打印，不影响其他租户继续处理。

用法：
    cd backend

    # 全量已初始化租户
    python scripts/fix/fix_social_capacity_tables.py

    # 指定单个租户
    python scripts/fix/fix_social_capacity_tables.py <tenant_code>

    # 仅查看会处理哪些租户与会建哪些表，不实际建表
    python scripts/fix/fix_social_capacity_tables.py --dry-run
    python scripts/fix/fix_social_capacity_tables.py <tenant_code> --dry-run
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, inspect as sa_inspect, text  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import TenantBase  # noqa: E402

# 显式导入 5 个模型，确保 TenantBase.metadata 中已注册对应表
from app.modules.client.models.capacity.social_capacity import (  # noqa: F401,E402
    SocialCapacity,
    SocialCapacityAccount,
    SocialCapacityAudit,
    SocialCapacityDriver,
    SocialCapacityVehicle,
)

SOCIAL_CAPACITY_TABLES = [
    "biz_social_capacity",
    "biz_social_capacity_driver",
    "biz_social_capacity_vehicle",
    "biz_social_capacity_account",
    "biz_social_capacity_audit",
]


def get_all_tenant_codes(settings) -> list[str]:
    """从平台库获取所有 db_initialized=1 且未软删的租户编码。"""
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT tenant_code FROM sys_tenant "
                    "WHERE is_deleted = 0 AND db_initialized = 1 "
                    "ORDER BY id"
                )
            )
            return [row[0] for row in result]
    finally:
        engine.dispose()


def fix_social_capacity_tables(tenant_code: str, settings, *, dry_run: bool = False) -> None:
    """为单个租户补建社会运力 5 张表，已存在则跳过。"""
    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)

    try:
        inspector = sa_inspect(engine)
        existing_tables = set(inspector.get_table_names())

        missing = [name for name in SOCIAL_CAPACITY_TABLES if name not in existing_tables]
        present = [name for name in SOCIAL_CAPACITY_TABLES if name in existing_tables]

        if not missing:
            print(f"  [{tenant_code}] 5 张社会运力表均已存在，跳过")
            return

        # 注册到 metadata 的表对象（防止某些表未被导入）
        tables_to_create = []
        for name in missing:
            table = TenantBase.metadata.tables.get(name)
            if table is None:
                print(f"  [{tenant_code}] [WARN] 模型未注册到 metadata：{name}，跳过该表")
                continue
            tables_to_create.append(table)

        if not tables_to_create:
            print(f"  [{tenant_code}] 缺失但模型未注册，无可建表")
            return

        if present:
            print(f"  [{tenant_code}] 已存在: {present}")
        names_to_create = [t.name for t in tables_to_create]
        if dry_run:
            print(f"  [{tenant_code}] [DRY-RUN] 将补建: {names_to_create}")
            return

        TenantBase.metadata.create_all(engine, tables=tables_to_create)
        print(f"  [{tenant_code}] 已补建: {names_to_create}")
    finally:
        engine.dispose()


def main() -> int:
    args = [a for a in sys.argv[1:] if a]
    dry_run = False
    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    settings = get_settings()

    if args:
        codes = [args[0]]
        print(f"指定租户: {codes[0]}")
    else:
        codes = get_all_tenant_codes(settings)
        if not codes:
            print("未找到已初始化的租户库（db_initialized=1）")
            return 0
        print(f"找到 {len(codes)} 个已初始化的租户库: {codes}")

    if dry_run:
        print("[DRY-RUN] 仅展示，不会实际建表\n")

    success = 0
    failed: list[tuple[str, str]] = []
    for code in codes:
        try:
            fix_social_capacity_tables(code, settings, dry_run=dry_run)
            success += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [{code}] 失败: {exc}")
            failed.append((code, str(exc)))

    print(
        f"\n完成！共处理 {len(codes)} 个租户库，成功 {success}，失败 {len(failed)}"
    )
    if failed:
        print("失败明细：")
        for code, err in failed:
            print(f"  - {code}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
