"""
同步租户端字典数据到所有已激活租户（upsert 模式）

DICT_DEFS 是租户字典的唯一真实来源（Single Source of Truth）：
- dict_code 不存在的字典：新增字典 + 全部默认项
- dict_code 已存在的字典：跳过（用户可能已自行增删项）

新模块涉及字典时，在 DICT_DEFS 中新增定义即可，
部署时通过 deploy.sh db-sync 自动同步到所有租户。

用法：
    python scripts/seed/seed_client_dicts.py
    python scripts/seed/seed_client_dicts.py 1001 1010   # 仅同步指定租户编码（不依赖平台库筛选条件）

说明：仅执行「列类型迁移」不会新增数据字典；新字典（如 self_capacity_driver_type / 自有驾驶员类型）
须在代码合并 DICT_DEFS 后执行本脚本，才会写入各租户库 biz_dict。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings

# ============================================================
# 字典定义（唯一真实来源）
# 格式: (dict_code, dict_name, sort_order, [
#     (item_name, item_value, sort_order),
#     ...
# ])
# ============================================================
DICT_DEFS = [
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
    ("vehicle_type", "车辆类型", 20, [
        ("重型货车", "heavy_truck", 0),
        ("中型货车", "medium_truck", 10),
        ("轻型货车", "light_truck", 20),
        ("微型货车", "mini_truck", 30),
        ("挂车", "trailer", 40),
    ]),
    # 挂车子类（与 mock_tenant_trailers.DEFAULT_TRAILER_TYPES 的 item_value 一致）
    ("trailer_type", "挂车类型", 22, [
        ("平板挂车", "flatbed", 0),
        ("厢式挂车", "van", 10),
        ("骨架挂车", "skeleton", 20),
        ("低平板挂车", "lowbed", 30),
        ("罐式挂车", "tank", 40),
        ("集装箱挂车", "container", 50),
    ]),
    ("self_capacity_driver_type", "自有驾驶员类型", 24, [
        ("自有", "own", 0),
        ("外协", "outsourced", 10),
        ("临时", "temporary", 20),
    ]),
]


def upsert_dicts_for_tenant(tenant_code: str, engine) -> int:
    """
    向指定租户库 upsert 字典数据，返回新增字典数量。
    已存在的 dict_code 不会修改（用户可能已自定义选项）。
    """
    created = 0
    with Session(engine) as session:
        for dict_code, dict_name, sort_order, items in DICT_DEFS:
            existing = session.execute(
                text(
                    "SELECT id FROM biz_dict "
                    "WHERE dict_code = :code AND is_deleted = 0"
                ),
                {"code": dict_code},
            ).scalar_one_or_none()

            if existing is not None:
                continue

            session.execute(
                text(
                    "INSERT INTO biz_dict "
                    "(dict_code, dict_name, sort_order, status, is_deleted) "
                    "VALUES (:code, :name, :sort, 1, 0)"
                ),
                {"code": dict_code, "name": dict_name, "sort": sort_order},
            )
            dict_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            for item_name, item_value, item_sort in items:
                session.execute(
                    text(
                        "INSERT INTO biz_dict_item "
                        "(dict_id, dict_code, item_name, item_value, "
                        "sort_order, status, is_deleted) "
                        "VALUES (:did, :code, :iname, :ival, :isort, 1, 0)"
                    ),
                    {
                        "did": dict_id,
                        "code": dict_code,
                        "iname": item_name,
                        "ival": item_value,
                        "isort": item_sort,
                    },
                )

            created += 1

        session.commit()

    return created


def main():
    """遍历所有已激活租户，upsert 字典数据。"""
    settings = get_settings()

    if len(sys.argv) > 1:
        tenant_codes = [c.strip() for c in sys.argv[1:] if c.strip()]
        print(f"[INFO] 使用命令行指定租户: {tenant_codes}")
    else:
        platform_engine = create_engine(settings.platform_db_url_sync)
        with Session(platform_engine) as session:
            rows = session.execute(
                text(
                    "SELECT tenant_code FROM sys_tenant "
                    "WHERE is_deleted = 0 AND status = 1 AND db_initialized = 1"
                )
            ).fetchall()
        tenant_codes = [r[0] for r in rows]
        platform_engine.dispose()

    if not tenant_codes:
        print("[INFO] 无租户可同步，跳过（可传租户编码：python scripts/seed/seed_client_dicts.py 1001）")
        return

    print(f"[INFO] 将同步 {len(tenant_codes)} 个租户库")

    for code in tenant_codes:
        tenant_engine = create_engine(settings.tenant_db_url_sync(code))
        try:
            created = upsert_dicts_for_tenant(code, tenant_engine)
            if created:
                print(f"  [{code}] 新增 {created} 个字典")
            else:
                print(f"  [{code}] 字典已完整，无需新增")
        except Exception as e:
            print(f"  [{code}] 失败: {e}")
        finally:
            tenant_engine.dispose()

    print("[OK] 租户字典同步完成")


if __name__ == "__main__":
    main()
