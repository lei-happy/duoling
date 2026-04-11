"""
修复已有租户数据库：补建缺失的 core 层表 + 插入种子数据

用法：
    python scripts/fix_tenant_tables.py [tenant_code]

不传 tenant_code 则修复所有已初始化的租户库。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect
from app.core.config import get_settings
from app.core.database import TenantBase, DatabaseManager
from app.common.utils import hash_password

# 确保所有模型已导入
from app.modules.client.models import *  # noqa: F401, F403


def get_all_tenant_codes(settings) -> list:
    """从平台库获取所有 db_initialized=1 的租户编码"""
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tenant_code FROM sys_tenant "
            "WHERE is_deleted = 0 AND db_initialized = 1"
        ))
        codes = [row[0] for row in result]
    engine.dispose()
    return codes


def fix_tenant_database(tenant_code: str, settings):
    """修复单个租户库"""
    db_name = f"{settings.TENANT_DB_PREFIX}{tenant_code}"
    if hasattr(settings, "tenant_database_name"):
        db_name = settings.tenant_database_name(tenant_code)

    print(f"\n{'='*60}")
    print(f"修复租户库: {db_name} (tenant_code={tenant_code})")
    print(f"{'='*60}")

    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)

    # 1. 检查已有表
    inspector = sa_inspect(engine)
    existing_tables = set(inspector.get_table_names())
    print(f"已有表: {sorted(existing_tables)}")

    # 2. 补建 core 层缺失的表
    core_tables = DatabaseManager.get_tables_by_tier("core")
    missing_core = [t for t in core_tables if t.name not in existing_tables]
    if missing_core:
        TenantBase.metadata.create_all(engine, tables=missing_core)
        print(f"已补建 core 层表: {[t.name for t in missing_core]}")
    else:
        print("core 层表完整，无需补建")

    # 3. 插入种子数据（仅在空表时插入）
    with engine.connect() as conn:
        _seed_roles(conn, existing_tables)
        _seed_departments(conn, existing_tables)
        _seed_admin_user(conn, tenant_code, existing_tables)
        _sync_regions(conn, tenant_code, settings)
        _sync_vehicle_basicdata(conn, settings)
        conn.commit()

    engine.dispose()
    print(f"租户 {tenant_code} 修复完成")


def _seed_roles(conn, existing_tables):
    """插入默认角色（如果表为空）"""
    result = conn.execute(text("SELECT COUNT(*) FROM biz_role"))
    if result.scalar() > 0:
        print("  biz_role 已有数据，跳过")
        return
    conn.execute(text(
        "INSERT INTO biz_role (role_code, role_name, sort_order, status, is_deleted) VALUES "
        "('admin', '管理员', 0, 1, 0), "
        "('operator', '操作员', 10, 1, 0), "
        "('driver', '驾驶员', 20, 1, 0)"
    ))
    print("  已插入默认角色")


def _seed_departments(conn, existing_tables):
    """插入默认部门（如果表为空）"""
    if "biz_department" not in existing_tables:
        return
    result = conn.execute(text("SELECT COUNT(*) FROM biz_department"))
    if result.scalar() > 0:
        print("  biz_department 已有数据，跳过")
        return
    conn.execute(text(
        "INSERT INTO biz_department (parent_id, dept_name, dept_code, sort_order, status, is_deleted) VALUES "
        "(0, '总公司', 'HQ', 0, 1, 0)"
    ))
    result = conn.execute(text("SELECT id FROM biz_department WHERE dept_code = 'HQ'"))
    hq_id = result.scalar()
    conn.execute(text(
        f"INSERT INTO biz_department (parent_id, dept_name, dept_code, sort_order, status, is_deleted) VALUES "
        f"({hq_id}, '运营部', 'OP', 0, 1, 0), "
        f"({hq_id}, '车队部', 'FL', 10, 1, 0), "
        f"({hq_id}, '财务部', 'FI', 20, 1, 0)"
    ))
    print("  已插入默认部门")


def _seed_admin_user(conn, tenant_code, existing_tables):
    """确保管理员用户和角色关联存在"""
    result = conn.execute(text("SELECT COUNT(*) FROM biz_user"))
    if result.scalar() > 0:
        print("  biz_user 已有数据，跳过管理员创建")
        return
    hashed = hash_password("123456")
    conn.execute(text(
        "INSERT INTO biz_user (username, password, real_name, user_type, department, status, is_deleted) VALUES "
        f"('admin_{tenant_code}', '{hashed}', '管理员', 1, '总公司', 1, 0)"
    ))

    if "biz_user_role" in existing_tables or "biz_user_role" in {
        t.name for t in DatabaseManager.get_tables_by_tier("core")
    }:
        result = conn.execute(text("SELECT id FROM biz_user WHERE username = :u"),
                              {"u": f"admin_{tenant_code}"})
        user_id = result.scalar()
        result = conn.execute(text("SELECT id FROM biz_role WHERE role_code = 'admin'"))
        role_id = result.scalar()
        if user_id and role_id:
            conn.execute(text(
                f"INSERT INTO biz_user_role (user_id, role_id) VALUES ({user_id}, {role_id})"
            ))
    print("  已创建管理员用户及角色关联")


def _sync_regions(conn, tenant_code, settings):
    """同步地区数据（自动发现 sys_regions 列结构）"""
    try:
        inspector = sa_inspect(conn)
        if "biz_region" not in inspector.get_table_names():
            print("  biz_region 表不存在，跳过地区同步")
            return
    except Exception:
        print("  无法检查 biz_region，跳过地区同步")
        return

    result = conn.execute(text("SELECT COUNT(*) FROM biz_region"))
    if result.scalar() > 0:
        print("  biz_region 已有数据，跳过")
        return

    platform_db = settings.platform_database_name

    # 发现 sys_regions 列结构
    cols_result = conn.execute(text(
        f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        f"WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'sys_regions' "
        f"ORDER BY ORDINAL_POSITION"
    ), {"db": platform_db})
    source_cols = [row[0] for row in cols_result]
    print(f"  sys_regions 列: {source_cols}")

    col_candidates = {
        "code": ["code", "region_code", "area_code"],
        "name": ["name", "region_name", "area_name"],
        "parent_code": ["parent_code", "parent_id", "pid", "pcode"],
        "level": ["level", "region_level", "deep", "depth", "type"],
        "sort_order": ["sort_order", "sort", "order_num"],
        "status": ["status"],
    }

    mapping = {}
    for target, candidates in col_candidates.items():
        for c in candidates:
            if c in source_cols:
                mapping[target] = c
                break

    if "code" not in mapping or "name" not in mapping:
        print(f"  ⚠ sys_regions 列名无法映射: 源列={source_cols}, 已匹配={mapping}")
        return

    target_cols = list(mapping.keys())
    source_exprs = []
    for t in target_cols:
        src_col = mapping[t]
        if t in ("code", "parent_code"):
            source_exprs.append(f"CAST(`{src_col}` AS CHAR)")
        else:
            source_exprs.append(f"`{src_col}`")

    for col, default in [("parent_code", "NULL"), ("level", "1"), ("sort_order", "0"), ("status", "1")]:
        if col not in mapping:
            target_cols.append(col)
            source_exprs.append(default)

    target_cols.append("is_deleted")
    source_exprs.append("0")

    where_clause = ""
    if "is_deleted" in source_cols:
        where_clause = " WHERE `is_deleted` = 0"

    sql = (
        f"INSERT INTO biz_region ({', '.join(target_cols)}) "
        f"SELECT {', '.join(source_exprs)} "
        f"FROM `{platform_db}`.sys_regions{where_clause}"
    )
    try:
        conn.execute(text(sql))
        print("  已同步地区数据")
    except Exception as e:
        print(f"  地区数据同步失败: {e}")


def _sync_vehicle_basicdata(conn, settings):
    """从平台 basicdata_* 同步品牌/车系/经销商到租户库"""
    platform_db = settings.platform_database_name

    def _safe_count(sql: str):
        try:
            return conn.execute(text(sql)).scalar() or 0
        except Exception:
            return -1

    if _safe_count("SELECT COUNT(*) FROM biz_vehicle_brand") < 0:
        print("  biz_vehicle_brand 不存在，跳过车辆/经销商基础同步")
        return

    if _safe_count("SELECT COUNT(*) FROM biz_vehicle_brand") == 0:
        try:
            conn.execute(text(
                f"INSERT INTO biz_vehicle_brand ("
                f"brand_id, brand_logo, brand_name_cn, brand_country, "
                f"brand_introduce, create_time, last_update_time) "
                f"SELECT brand_id, brand_logo, brand_name_cn, brand_country, "
                f"brand_introduce, create_time, last_update_time "
                f"FROM `{platform_db}`.basicdata_brand"
            ))
            print("  已同步品牌数据")
        except Exception as e:
            print(f"  品牌同步失败: {e}")
    else:
        print("  biz_vehicle_brand 已有数据，跳过品牌同步")

    if _safe_count("SELECT COUNT(*) FROM biz_vehicle_series") == 0:
        try:
            conn.execute(text(
                f"INSERT INTO biz_vehicle_series ("
                f"series_id, brand_id, price, series_image, series_name, "
                f"energy_type, length_mm, width_mm, height_mm, wheelbase_mm, "
                f"front_track_mm, rear_track_mm, approach_angle, "
                f"departure_angle, curb_weight_kg, create_time, last_update_time) "
                f"SELECT series_id, brand_id, price, series_image, series_name, "
                f"energy_type, length_mm, width_mm, height_mm, wheelbase_mm, "
                f"front_track_mm, rear_track_mm, approach_angle, "
                f"departure_angle, curb_weight_kg, create_time, last_update_time "
                f"FROM `{platform_db}`.basicdata_car_series"
            ))
            print("  已同步车系数据")
        except Exception as e:
            print(f"  车系同步失败: {e}")
    else:
        print("  biz_vehicle_series 已有数据，跳过车系同步")

    if _safe_count("SELECT COUNT(*) FROM biz_dealer") == 0:
        try:
            conn.execute(text(
                f"INSERT INTO biz_dealer ("
                f"dealer_id, dealer_name, dealer_type, main_brand, "
                f"province, city, address_detail, longitude, latitude, "
                f"created_at, updated_at) "
                f"SELECT dealer_id, dealer_name, dealer_type, main_brand, "
                f"province, city, address_detail, longitude, latitude, "
                f"created_at, updated_at "
                f"FROM `{platform_db}`.basicdata_dealer_info"
            ))
            print("  已同步经销商数据")
        except Exception as e:
            print(f"  经销商同步失败: {e}")
    else:
        print("  biz_dealer 已有数据，跳过经销商同步")


if __name__ == "__main__":
    settings = get_settings()

    if len(sys.argv) > 1:
        codes = [sys.argv[1]]
    else:
        codes = get_all_tenant_codes(settings)
        if not codes:
            print("未找到已初始化的租户库")
            sys.exit(0)
        print(f"找到 {len(codes)} 个已初始化的租户库: {codes}")

    for code in codes:
        try:
            fix_tenant_database(code, settings)
        except Exception as e:
            print(f"修复租户 {code} 失败: {e}")

    print(f"\n全部完成！共处理 {len(codes)} 个租户库")
