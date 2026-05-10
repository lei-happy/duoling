# -*- coding: utf-8 -*-
"""为租户库 biz_vehicle、biz_trailer 增加 plate_category 字段（幂等）

用法：
  python3 scripts/fix/migrate_plate_category.py
  python3 scripts/fix/migrate_plate_category.py <tenant_code>
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect

from app.core.config import get_settings

DEFAULT_CATEGORY = "YELLOW"


def column_exists(engine, table_name: str, column_name: str) -> bool:
    inspector = sa_inspect(engine)
    if table_name not in inspector.get_table_names():
        return False
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_database(engine, db_name: str) -> None:
    print(f"\n{'=' * 50}\n迁移数据库: {db_name}\n{'=' * 50}")

    with engine.connect() as conn:
        # biz_vehicle
        if not column_exists(engine, "biz_vehicle", "plate_category"):
            conn.execute(
                text(
                    """
                    ALTER TABLE `biz_vehicle`
                    ADD COLUMN `plate_category` VARCHAR(20) NOT NULL
                    DEFAULT 'YELLOW'
                    COMMENT '车牌类型 BLUE/YELLOW/NEW_ENERGY'
                    AFTER `plate_number`;
                    """
                )
            )
            conn.commit()
            print("[OK] biz_vehicle: 新增 plate_category")
        else:
            print("[SKIP] biz_vehicle.plate_category 已存在")

        # biz_trailer
        if not column_exists(engine, "biz_trailer", "plate_category"):
            conn.execute(
                text(
                    """
                    ALTER TABLE `biz_trailer`
                    ADD COLUMN `plate_category` VARCHAR(20) NOT NULL
                    DEFAULT 'YELLOW'
                    COMMENT '车牌类型 BLUE/YELLOW/NEW_ENERGY'
                    AFTER `plate_number`;
                    """
                )
            )
            conn.commit()
            print("[OK] biz_trailer: 新增 plate_category")
        else:
            print("[SKIP] biz_trailer.plate_category 已存在")

        conn.execute(
            text(
                "UPDATE biz_vehicle SET plate_category = :d WHERE plate_category IS NULL OR plate_category = ''"
            ),
            {"d": DEFAULT_CATEGORY},
        )
        conn.execute(
            text(
                "UPDATE biz_trailer SET plate_category = :d WHERE plate_category IS NULL OR plate_category = ''"
            ),
            {"d": DEFAULT_CATEGORY},
        )
        conn.commit()


def get_all_tenant_codes():
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT tenant_code FROM sys_tenant WHERE is_deleted = 0")
        )
        codes = [row[0] for row in result]
    engine.dispose()
    return codes


def main():
    settings = get_settings()

    if len(sys.argv) > 1:
        tenant_codes = [sys.argv[1]]
    else:
        tenant_codes = get_all_tenant_codes()
        if not tenant_codes:
            print("未找到任何租户，请先创建租户")
            return

    print(f"即将迁移 {len(tenant_codes)} 个租户数据库: {tenant_codes}")

    for code in tenant_codes:
        db_name = f"{settings.TENANT_DB_PREFIX}{code}"
        url = settings.tenant_db_url_sync(code)
        engine = create_engine(url)
        try:
            migrate_database(engine, db_name)
        except Exception as e:
            print(f"[ERROR] {db_name} 迁移失败: {e}")
        finally:
            engine.dispose()

    print(f"\n迁移完成！共处理 {len(tenant_codes)} 个租户库")


if __name__ == "__main__":
    main()
