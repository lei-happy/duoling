"""
基础模块数据库迁移脚本
为已有的租户数据库执行表结构变更：
  1. biz_department: 新增 dept_type 字段
  2. biz_user: department(VARCHAR) → department_id(BIGINT)，新增 nickname 字段
  3. biz_user: 新增 birthday 字段（出生日期）

用法：
    # 迁移所有租户库
    python scripts/migrate_base_module.py

    # 迁移指定租户库
    python scripts/migrate_base_module.py 1001

生成的 SQL 也可单独在数据库中执行（见脚本末尾注释）。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect
from app.core.config import get_settings


MIGRATION_SQL = [
    # ---- biz_department: 新增 dept_type ----
    """
    ALTER TABLE `biz_department`
    ADD COLUMN `dept_type` VARCHAR(50) NULL COMMENT '部门类型（字典 org_type）'
    AFTER `dept_code`;
    """,

    # ---- biz_user: 新增 nickname ----
    """
    ALTER TABLE `biz_user`
    ADD COLUMN `nickname` VARCHAR(50) NULL COMMENT '昵称'
    AFTER `real_name`;
    """,

    # ---- biz_user: department(VARCHAR) → department_id(BIGINT) ----
    """
    ALTER TABLE `biz_user`
    ADD COLUMN `department_id` BIGINT NULL COMMENT '所属部门ID'
    AFTER `user_type`;
    """,

    # 删除旧的 department 字符串字段
    """
    ALTER TABLE `biz_user`
    DROP COLUMN `department`;
    """,
]


def column_exists(engine, table_name: str, column_name: str) -> bool:
    """检查表中是否已存在指定列"""
    inspector = sa_inspect(engine)
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def seed_dict_data(engine, db_name: str):
    """为租户库补充缺失的字典种子数据"""
    from sqlalchemy.orm import Session

    dict_defs = [
        ("sex", "性别", 0, [
            ("男", "男", 0),
            ("女", "女", 10),
        ]),
        ("organization_type", "机构类型", 10, [
            ("总部", "headquarters", 0),
            ("分公司", "branch", 10),
            ("部门", "department", 20),
            ("车队", "fleet", 30),
        ]),
    ]

    with Session(engine) as session:
        for dict_code, dict_name, sort_order, items in dict_defs:
            existing = session.execute(
                text("SELECT id FROM biz_dict WHERE dict_code = :code AND is_deleted = 0"),
                {"code": dict_code},
            ).fetchone()

            if existing:
                print(f"  [SKIP] 字典 {dict_code} 已存在")
                continue

            session.execute(
                text(
                    "INSERT INTO biz_dict (dict_code, dict_name, sort_order, status, created_at, updated_at, is_deleted) "
                    "VALUES (:code, :name, :sort, 1, NOW(), NOW(), 0)"
                ),
                {"code": dict_code, "name": dict_name, "sort": sort_order},
            )
            dict_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            for item_name, item_value, item_sort in items:
                session.execute(
                    text(
                        "INSERT INTO biz_dict_item (dict_id, dict_code, item_name, item_value, sort_order, status, created_at, updated_at, is_deleted) "
                        "VALUES (:did, :code, :name, :val, :sort, 1, NOW(), NOW(), 0)"
                    ),
                    {"did": dict_id, "code": dict_code, "name": item_name, "val": item_value, "sort": item_sort},
                )

            session.commit()
            print(f"  [OK] 字典 {dict_code} ({dict_name}) 已创建，含 {len(items)} 项")


def migrate_database(engine, db_name: str):
    """对单个数据库执行迁移"""
    print(f"\n{'='*50}")
    print(f"迁移数据库: {db_name}")
    print(f"{'='*50}")

    with engine.connect() as conn:
        # 1. biz_department: dept_type
        if not column_exists(engine, "biz_department", "dept_type"):
            conn.execute(text(MIGRATION_SQL[0]))
            conn.commit()
            print("[OK] biz_department: 新增 dept_type 列")
        else:
            print("[SKIP] biz_department.dept_type 已存在")

        # 2. biz_user: nickname
        if not column_exists(engine, "biz_user", "nickname"):
            conn.execute(text(MIGRATION_SQL[1]))
            conn.commit()
            print("[OK] biz_user: 新增 nickname 列")
        else:
            print("[SKIP] biz_user.nickname 已存在")

        # 3. biz_user: department_id (替换 department)
        if not column_exists(engine, "biz_user", "department_id"):
            conn.execute(text(MIGRATION_SQL[2]))
            conn.commit()
            print("[OK] biz_user: 新增 department_id 列")
        else:
            print("[SKIP] biz_user.department_id 已存在")

        # 4. 删除旧 department 列
        if column_exists(engine, "biz_user", "department"):
            conn.execute(text(MIGRATION_SQL[3]))
            conn.commit()
            print("[OK] biz_user: 已删除旧 department 列")
        else:
            print("[SKIP] biz_user.department 列已不存在")

        # 5. biz_user: birthday
        if not column_exists(engine, "biz_user", "birthday"):
            conn.execute(
                text(
                    """
                    ALTER TABLE `biz_user`
                    ADD COLUMN `birthday` DATE NULL COMMENT '出生日期'
                    AFTER `gender`;
                    """
                )
            )
            conn.commit()
            print("[OK] biz_user: 新增 birthday 列")
        else:
            print("[SKIP] biz_user.birthday 已存在")

    # 6. 补充字典种子数据
    print("\n---- 字典种子数据 ----")
    seed_dict_data(engine, db_name)


def get_all_tenant_codes():
    """从平台库查询所有租户编码"""
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


# ============================================================
# 如需手动在 MySQL 中执行，请使用以下 SQL：
# ============================================================
#
# -- 1. biz_department 新增部门类型字段
# ALTER TABLE `biz_department`
# ADD COLUMN `dept_type` VARCHAR(50) NULL COMMENT '部门类型（字典 org_type）'
# AFTER `dept_code`;
#
# -- 2. biz_user 新增昵称字段
# ALTER TABLE `biz_user`
# ADD COLUMN `nickname` VARCHAR(50) NULL COMMENT '昵称'
# AFTER `real_name`;
#
# -- 3. biz_user 新增部门ID字段（替代旧的 department 字符串字段）
# ALTER TABLE `biz_user`
# ADD COLUMN `department_id` BIGINT NULL COMMENT '所属部门ID'
# AFTER `user_type`;
#
# -- 4. biz_user 删除旧的 department 字符串字段
# ALTER TABLE `biz_user`
# DROP COLUMN `department`;
#
# -- 5. biz_user 出生日期
# ALTER TABLE `biz_user`
# ADD COLUMN `birthday` DATE NULL COMMENT '出生日期'
# AFTER `gender`;
