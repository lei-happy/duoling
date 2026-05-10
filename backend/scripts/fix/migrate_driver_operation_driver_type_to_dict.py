# -*- coding: utf-8 -*-
"""将租户库 biz_driver_operation.driver_type 从整型枚举改为字典 dictDataCode（VARCHAR）

历史值映射（与 seed_client_dicts.py 中 self_capacity_driver_type 默认项一致）：
  1 -> own
  2 -> outsourced
  3 -> temporary

若列已是 VARCHAR，则仅尝试把字面量 '1'/'2'/'3' 更新为上述 code（幂等）。

用法：
  cd backend && python scripts/fix/migrate_driver_operation_driver_type_to_dict.py
  python scripts/fix/migrate_driver_operation_driver_type_to_dict.py <tenant_code>

列迁移完成后，请在 backend 目录执行字典种子（否则「数据字典」中不会出现自有驾驶员类型）：
  python scripts/seed/seed_client_dicts.py
  python scripts/seed/seed_client_dicts.py <tenant_code> [<tenant_code> ...]
"""

import osy
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from typing import Optional

from sqlalchemy import create_engine, text, inspect as sa_inspect  # noqa: E402

from app.core.config import get_settings  # noqa: E402


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


def _column_type_name(engine, table: str, column: str) -> Optional[str]:
    inspector = sa_inspect(engine)
    if table not in inspector.get_table_names():
        return None
    for c in inspector.get_columns(table):
        if c["name"] == column:
            return str(c["type"])
    return None


def migrate_database(engine, db_name: str) -> None:
    print(f"\n{'=' * 50}\n迁移数据库: {db_name}\n{'=' * 50}")

    typ = _column_type_name(engine, "biz_driver_operation", "driver_type")
    if typ is None:
        print("[SKIP] 表 biz_driver_operation 或列 driver_type 不存在")
        return

    typ_lower = typ.lower()
    with engine.connect() as conn:
        if "varchar" in typ_lower or "char" in typ_lower or "text" in typ_lower:
            conn.execute(
                text(
                    """
                    UPDATE biz_driver_operation
                    SET driver_type = CASE driver_type
                        WHEN '1' THEN 'own'
                        WHEN '2' THEN 'outsourced'
                        WHEN '3' THEN 'temporary'
                        ELSE driver_type
                    END
                    WHERE driver_type IN ('1', '2', '3')
                    """
                )
            )
            conn.commit()
            print("[OK] driver_type 已为字符串列：已更新遗留字面量 1/2/3")
            return

        # 数值列：通过临时列迁移
        r = conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'biz_driver_operation' "
                "AND COLUMN_NAME = 'driver_type_str'"
            )
        )
        if (r.scalar() or 0) > 0:
            print("[SKIP] 已存在 driver_type_str，跳过（上次可能中断，请人工检查）")
            return

        conn.execute(
            text(
                """
                ALTER TABLE `biz_driver_operation`
                ADD COLUMN `driver_type_str` VARCHAR(50) NULL
                COMMENT '自有驾驶员类型 dictDataCode（迁移临时列）'
                AFTER `department_id`
                """
            )
        )
        conn.commit()
        print("[OK] 已添加临时列 driver_type_str")

        conn.execute(
            text(
                """
                UPDATE `biz_driver_operation`
                SET `driver_type_str` = CASE `driver_type`
                    WHEN 1 THEN 'own'
                    WHEN 2 THEN 'outsourced'
                    WHEN 3 THEN 'temporary'
                    ELSE NULL
                END
                """
            )
        )
        conn.commit()
        print("[OK] 已拷贝并映射数值到 driver_type_str")

        conn.execute(text("ALTER TABLE `biz_driver_operation` DROP COLUMN `driver_type`"))
        conn.commit()
        print("[OK] 已删除旧列 driver_type")

        conn.execute(
            text(
                """
                ALTER TABLE `biz_driver_operation`
                CHANGE COLUMN `driver_type_str` `driver_type` VARCHAR(50) NULL
                COMMENT '自有驾驶员类型（数据字典 dictDataCode）'
                """
            )
        )
        conn.commit()
        print("[OK] 已将 driver_type_str 重命名为 driver_type (VARCHAR)")


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
