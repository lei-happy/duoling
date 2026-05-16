"""
为已有租户开通「运输任务单」模块所需的表与列：

  1. 创建 biz_task / biz_task_segment / biz_task_waybill_item /
     biz_task_finance_doc / biz_task_finance_item 五张表（若缺失）
  2. 在 biz_waybill_cargo 上补 allocated_quantity / cargo_version 两个字段

判定原则：
  - 只处理已开通了 biz_task 或 biz_task_finance 功能（即 standard/pro 版）的租户；
  - 完全幂等：表/列已存在则跳过，不报错；
  - 不写入任何业务数据，只做 schema 升级。

用法：
    python scripts/fix/fix_task_module_tables.py              # 处理所有已开通的租户
    python scripts/fix/fix_task_module_tables.py 1001         # 只处理 tenant_code=1001
"""

from __future__ import annotations

import sys
import os
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect
from app.core.config import get_settings
from app.core.database import TenantBase, DatabaseManager

# 确保所有模型已注册到 metadata
from app.modules.client.models import *  # noqa: F401, F403

TASK_TABLE_NAMES = [
    "biz_task",
    "biz_task_segment",
    "biz_task_waybill_item",
    "biz_task_finance_doc",
    "biz_task_finance_item",
]


def list_target_tenants(settings, only_code: Optional[str] = None) -> List[str]:
    """返回所有需要补表的租户编码（已开通 biz_task / biz_task_finance 功能）。"""
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)
    with engine.connect() as conn:
        rows = conn.execute(text(
            """
            SELECT DISTINCT t.tenant_code
            FROM sys_tenant t
            JOIN sys_tenant_product tp ON tp.tenant_id = t.id
              AND tp.is_deleted = 0 AND tp.status = 1
            JOIN sys_product_version v ON v.id = tp.version_id
              AND v.is_deleted = 0 AND v.status = 1
            JOIN sys_version_feature vf ON vf.version_id = v.id
              AND vf.is_deleted = 0 AND vf.status = 1
            JOIN sys_product_feature pf ON pf.id = vf.feature_id
              AND pf.is_deleted = 0 AND pf.status = 1
            WHERE t.is_deleted = 0 AND t.db_initialized = 1
              AND pf.feature_code IN ('biz_task', 'biz_task_finance')
            """
        )).fetchall()
    engine.dispose()
    codes = sorted({r[0] for r in rows})
    if only_code:
        return [c for c in codes if c == only_code]
    return codes


def upgrade_tenant(tenant_code: str, settings) -> None:
    db_name = settings.tenant_database_name(tenant_code)
    print(f"\n{'='*60}\n租户 {tenant_code} ({db_name})\n{'='*60}")
    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)

    insp = sa_inspect(engine)
    existing_tables = set(insp.get_table_names())

    # 1) 补建缺失的 biz_task* 表
    tables_to_create_names = [t for t in TASK_TABLE_NAMES if t not in existing_tables]
    if tables_to_create_names:
        tables_objs = DatabaseManager.get_tables_by_names(tables_to_create_names)
        TenantBase.metadata.create_all(engine, tables=tables_objs)
        print(f"  已补建表: {tables_to_create_names}")
    else:
        print("  biz_task* 表全部已存在，跳过补建")

    # 2) 在 biz_waybill_cargo 上补 allocated_quantity / cargo_version
    if "biz_waybill_cargo" in existing_tables:
        cols = {c["name"] for c in insp.get_columns("biz_waybill_cargo")}
        with engine.begin() as conn:
            if "allocated_quantity" not in cols:
                conn.execute(text(
                    "ALTER TABLE biz_waybill_cargo "
                    "ADD COLUMN allocated_quantity INT NOT NULL DEFAULT 0 "
                    "COMMENT '已分配到任务单的台数（应用层维护，约束 allocated<=quantity）'"
                ))
                print("  已在 biz_waybill_cargo 添加 allocated_quantity 列")
            else:
                print("  biz_waybill_cargo.allocated_quantity 已存在")
            if "cargo_version" not in cols:
                conn.execute(text(
                    "ALTER TABLE biz_waybill_cargo "
                    "ADD COLUMN cargo_version INT NOT NULL DEFAULT 1 "
                    "COMMENT '明细版本号'"
                ))
                print("  已在 biz_waybill_cargo 添加 cargo_version 列")
            else:
                print("  biz_waybill_cargo.cargo_version 已存在")
    else:
        print("  租户库无 biz_waybill_cargo 表，跳过列升级")

    engine.dispose()


def main():
    only_code = sys.argv[1] if len(sys.argv) > 1 else None
    settings = get_settings()
    tenants = list_target_tenants(settings, only_code=only_code)
    if not tenants:
        print("[INFO] 没有符合条件的租户需要升级")
        return
    print(f"[INFO] 待升级租户: {tenants}")
    for tc in tenants:
        try:
            upgrade_tenant(tc, settings)
        except Exception as ex:
            print(f"[ERROR] 升级租户 {tc} 失败: {ex}")
    print("\n[OK] 全部完成")


if __name__ == "__main__":
    main()
