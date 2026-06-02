"""
一键初始化开发环境

串联以下操作：
1. 初始化平台库（建库 + 建表）
2. 灌入平台种子数据（管理员、角色、菜单、版本、字典）
3. 灌入产品功能清单与版本-功能关联
4. 灌入客户端菜单（含 feature_code）
5. 创建开发用企业（tenant_code=dev1001）
6. 为开发企业开通旗舰版（enterprise），一次性建全 business 层表
7. 在租户库中灌入种子数据（角色、部门、管理员）

用法：
    python scripts/init/init_dev_env.py
    python scripts/init/init_dev_env.py --reset   # 重置（删除后重建开发企业库）
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import TenantBase, DatabaseManager
from app.common.utils import hash_password

# 确保所有模型被注册到 metadata
from app.modules.console.models import *  # noqa: F401, F403
from app.modules.client.models import *  # noqa: F401, F403

DEV_TENANT_CODE = "dev1001"
DEV_TENANT_NAME = "开发测试企业"
DEV_ADMIN_PHONE = "13900001001"
DEV_ADMIN_NAME = "开发管理员"


def step1_init_platform_db():
    """步骤1: 初始化平台库"""
    print("\n" + "=" * 60)
    print("步骤 1/7: 初始化平台库")
    print("=" * 60)
    from scripts.init.init_platform_db import init_platform_database
    init_platform_database()


def step2_seed_platform_data():
    """步骤2: 灌入平台种子数据"""
    print("\n" + "=" * 60)
    print("步骤 2/7: 灌入平台种子数据")
    print("=" * 60)
    from scripts.seed.seed_data import seed_platform_data
    seed_platform_data()


def step3_seed_product_features():
    """步骤3: 灌入产品功能清单"""
    print("\n" + "=" * 60)
    print("步骤 3/7: 灌入产品功能清单与版本关联")
    print("=" * 60)
    from scripts.seed.seed_product_features import main as seed_features
    seed_features()


def step4_seed_client_menus():
    """步骤4: 灌入客户端菜单"""
    print("\n" + "=" * 60)
    print("步骤 4/7: 灌入客户端菜单")
    print("=" * 60)
    from scripts.seed.seed_client_menus import main as seed_menus
    seed_menus()


def step5_create_dev_tenant(reset: bool = False):
    """步骤5: 创建开发用企业"""
    print("\n" + "=" * 60)
    print("步骤 5/7: 创建开发用企业")
    print("=" * 60)

    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)
    db_name = settings.tenant_database_name(DEV_TENANT_CODE)

    with Session(engine) as session:
        from app.modules.console.models.tenant.tenant import Tenant

        existing = session.query(Tenant).filter_by(
            tenant_code=DEV_TENANT_CODE, is_deleted=0
        ).first()

        if existing and not reset:
            print(f"[SKIP] 开发企业 {DEV_TENANT_CODE} 已存在 (id={existing.id})")
            engine.dispose()
            return

        if existing and reset:
            print(f"[RESET] 删除旧的开发企业记录...")
            existing.is_deleted = 1
            session.commit()
            root_url = (
                f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
                f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
                f"?charset=utf8mb4"
            )
            root_engine = create_engine(root_url)
            with root_engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS `{db_name}`"))
                conn.commit()
            root_engine.dispose()
            print(f"[OK] 已删除旧数据库 {db_name}")

        tenant = Tenant(
            tenant_code=DEV_TENANT_CODE,
            tenant_name=DEV_TENANT_NAME,
            short_name="开发企业",
            contact_person=DEV_ADMIN_NAME,
            contact_phone=DEV_ADMIN_PHONE,
            status=1,
            db_name=db_name,
            source_channel="script",
            remark="开发环境自动创建的测试企业",
        )
        session.add(tenant)
        session.flush()
        tenant_id = tenant.id
        print(f"[OK] 开发企业已创建: {DEV_TENANT_CODE} (id={tenant_id})")

        from app.modules.console.models.system.user import User
        from app.modules.console.models.system.user_tenant import UserTenant

        admin_user = session.query(User).filter_by(
            phone=DEV_ADMIN_PHONE, is_deleted=0
        ).first()

        if not admin_user:
            admin_user = User(
                password=hash_password("123456"),
                real_name=DEV_ADMIN_NAME,
                phone=DEV_ADMIN_PHONE,
                user_type=2,
                status=1,
                force_change_pwd=0,
            )
            session.add(admin_user)
            session.flush()
            print(f"[OK] 管理员账号已创建: {DEV_ADMIN_PHONE} / 123456")
        else:
            print(f"[SKIP] 管理员账号已存在: {admin_user.phone}")

        existing_ut = session.query(UserTenant).filter_by(
            user_id=admin_user.id, tenant_code=DEV_TENANT_CODE
        ).first()
        if not existing_ut:
            session.add(UserTenant(
                user_id=admin_user.id,
                tenant_code=DEV_TENANT_CODE,
                user_type=1,
                status=1,
            ))
            print(f"[OK] 用户-企业关联已创建")

        session.commit()

    # 创建租户数据库（core 层表）
    root_url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"?charset=utf8mb4"
    )
    root_engine = create_engine(root_url)
    with root_engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
        conn.commit()
    root_engine.dispose()
    print(f"[OK] 租户数据库 {db_name} 已创建")

    core_tables = DatabaseManager.get_tables_by_tier("core")
    tenant_engine = create_engine(settings.tenant_db_url_sync(DEV_TENANT_CODE))
    TenantBase.metadata.create_all(tenant_engine, tables=core_tables)
    tenant_engine.dispose()
    print(f"[OK] core 层表已初始化 ({len(core_tables)} 张)")

    # 更新 db_initialized
    with Session(engine) as session:
        from app.modules.console.models.tenant.tenant import Tenant
        tenant = session.query(Tenant).filter_by(
            tenant_code=DEV_TENANT_CODE, is_deleted=0
        ).first()
        if tenant:
            tenant.db_initialized = 1
            session.commit()

    engine.dispose()


def step6_assign_enterprise_version():
    """步骤6: 为开发企业开通旗舰版（enterprise）并建全 business 层表"""
    print("\n" + "=" * 60)
    print("步骤 6/7: 开通旗舰版（enterprise）")
    print("=" * 60)

    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    with Session(engine) as session:
        from app.modules.console.models.tenant.tenant import Tenant
        from app.modules.console.models.product.product_version import ProductVersion
        from app.modules.console.models.tenant.tenant_product import TenantProduct

        tenant = session.query(Tenant).filter_by(
            tenant_code=DEV_TENANT_CODE, is_deleted=0
        ).first()
        if not tenant:
            print("[ERROR] 开发企业不存在，请先执行步骤5")
            engine.dispose()
            return

        # 开通 basic 版（如果未开通）
        basic_ver = session.query(ProductVersion).filter_by(
            version_code="basic", status=1, is_deleted=0
        ).first()
        if basic_ver:
            existing_basic = session.query(TenantProduct).filter_by(
                tenant_id=tenant.id, version_code="basic", is_deleted=0
            ).first()
            if not existing_basic:
                session.add(TenantProduct(
                    tenant_id=tenant.id,
                    tenant_code=DEV_TENANT_CODE,
                    version_id=basic_ver.id,
                    version_code="basic",
                    start_time=datetime.now(),
                    status=1,
                ))
                print("[OK] basic 版已开通")
            else:
                print("[SKIP] basic 版已存在")

        # 开通 enterprise 版
        enterprise_ver = session.query(ProductVersion).filter_by(
            version_code="enterprise", status=1, is_deleted=0
        ).first()
        if not enterprise_ver:
            print("[ERROR] enterprise 版本不存在")
            engine.dispose()
            return

        existing_ent = session.query(TenantProduct).filter_by(
            tenant_id=tenant.id, version_code="enterprise", is_deleted=0
        ).first()
        if not existing_ent:
            session.add(TenantProduct(
                tenant_id=tenant.id,
                tenant_code=DEV_TENANT_CODE,
                version_id=enterprise_ver.id,
                version_code="enterprise",
                start_time=datetime.now(),
                status=1,
            ))
            print("[OK] enterprise 版已开通")
        else:
            print("[SKIP] enterprise 版已存在")

        session.commit()

        # 收集 enterprise 版本需要的全部 business 表
        from app.modules.console.models.product.product_feature import ProductFeature, VersionFeature

        vf_rows = (
            session.query(ProductFeature.required_tables)
            .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
            .filter(
                VersionFeature.version_id == enterprise_ver.id,
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
                ProductFeature.status == 1,
            )
            .all()
        )

        required_table_names = set()
        for (tables,) in vf_rows:
            if tables and isinstance(tables, list):
                required_table_names.update(tables)

    engine.dispose()

    # 在租户库中创建 business 层表
    if required_table_names:
        print(f"需要创建的 business 表: {sorted(required_table_names)}")
        tables_to_create = DatabaseManager.get_tables_by_names(list(required_table_names))
        if tables_to_create:
            tenant_engine = create_engine(
                settings.tenant_db_url_sync(DEV_TENANT_CODE)
            )
            TenantBase.metadata.create_all(tenant_engine, tables=tables_to_create)
            tenant_engine.dispose()
            print(f"[OK] business 层表已创建 ({len(tables_to_create)} 张)")
    else:
        print("[INFO] 无需创建额外的 business 表")


def step7_seed_tenant_data():
    """步骤7: 在租户库中灌入种子数据"""
    print("\n" + "=" * 60)
    print("步骤 7/7: 灌入租户种子数据")
    print("=" * 60)

    settings = get_settings()
    tenant_engine = create_engine(settings.tenant_db_url_sync(DEV_TENANT_CODE))

    from app.modules.client.models.role.biz_role import BizRole
    from app.modules.client.models.organization.biz_department import BizDepartment
    from app.modules.client.models.user.biz_user import BizUser
    from app.modules.client.models.user.biz_user_role import BizUserRole

    with Session(tenant_engine) as session:
        existing_user = session.query(BizUser).filter_by(
            phone=DEV_ADMIN_PHONE
        ).first()
        if existing_user:
            print("[SKIP] 租户种子数据已存在")
            tenant_engine.dispose()
            return

        roles = [
            BizRole(
                role_code="admin",
                role_name="管理员",
                sort_order=0,
                status=1,
                remark="拥有系统全部的操作权限",
            ),
        ]
        session.add_all(roles)
        session.flush()
        print("[OK] 默认角色已创建")

        hq = BizDepartment(
            parent_id=0, dept_name="总公司", dept_code="HQ", sort_order=0, status=1
        )
        session.add(hq)
        session.flush()
        sub_depts = [
            BizDepartment(parent_id=hq.id, dept_name="运营部", dept_code="OP", sort_order=0, status=1),
            BizDepartment(parent_id=hq.id, dept_name="车队部", dept_code="FL", sort_order=10, status=1),
            BizDepartment(parent_id=hq.id, dept_name="财务部", dept_code="FI", sort_order=20, status=1),
        ]
        session.add_all(sub_depts)
        session.flush()
        print("[OK] 默认部门已创建")

        admin_user = BizUser(
            password=hash_password("123456"),
            real_name=DEV_ADMIN_NAME,
            phone=DEV_ADMIN_PHONE,
            user_type=1,
            department_id=hq.id,
            status=1,
        )
        session.add(admin_user)
        session.flush()

        session.add(BizUserRole(user_id=admin_user.id, role_id=roles[0].id))
        print(f"[OK] 管理员 {DEV_ADMIN_PHONE} 已创建并关联管理员角色")

        session.commit()

    # 灌入字典数据（统一来源）
    from scripts.seed.seed_client_dicts import upsert_dicts_for_tenant
    created = upsert_dicts_for_tenant(DEV_TENANT_CODE, tenant_engine)
    print(f"[OK] 字典数据已灌入（新增 {created} 个字典）")

    # 同步地区数据
    platform_engine = create_engine(settings.platform_db_url_sync)
    platform_db = settings.platform_database_name
    try:
        with tenant_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM biz_region"))
            if (result.scalar() or 0) == 0:
                # 检查平台库是否有 sys_regions 表
                with platform_engine.connect() as pconn:
                    result = pconn.execute(text(
                        "SELECT COUNT(*) FROM information_schema.tables "
                        "WHERE table_schema = :db AND table_name = 'sys_regions'"
                    ), {"db": platform_db})
                    if result.scalar():
                        with tenant_engine.begin() as tconn:
                            cols_result = pconn.execute(text(
                                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                                "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'sys_regions' "
                                "ORDER BY ORDINAL_POSITION"
                            ), {"db": platform_db})
                            source_cols = [row[0] for row in cols_result]
                            col_candidates = {
                                "code": ["code", "region_code", "area_code"],
                                "name": ["name", "region_name", "area_name"],
                                "parent_code": ["parent_code", "parent_id", "pid", "pcode"],
                                "level": ["level", "region_level", "deep", "depth", "type"],
                                "sort_order": ["sort_order", "sort", "order_num"],
                                "status": ["status"],
                                "longitude": ["longitude", "lng"],
                                "latitude": ["latitude", "lat"],
                            }
                            mapping = {}
                            for target, candidates in col_candidates.items():
                                for c in candidates:
                                    if c in source_cols:
                                        mapping[target] = c
                                        break
                            if "code" in mapping and "name" in mapping:
                                target_cols = list(mapping.keys())
                                source_exprs = []
                                for t in target_cols:
                                    src_col = mapping[t]
                                    if t in ("code", "parent_code"):
                                        source_exprs.append(f"CAST(`{src_col}` AS CHAR)")
                                    else:
                                        source_exprs.append(f"`{src_col}`")
                                for col, default in [
                                    ("parent_code", "NULL"),
                                    ("level", "1"),
                                    ("sort_order", "0"),
                                    ("status", "1"),
                                ]:
                                    if col not in mapping:
                                        target_cols.append(col)
                                        source_exprs.append(default)
                                target_cols.extend(["is_deleted", "source"])
                                source_exprs.extend(["0", "0"])
                                where_parts = ["`is_deleted` = 0"]
                                if "level" in source_cols:
                                    where_parts.append("`level` <= 3")
                                where_clause = " WHERE " + " AND ".join(where_parts)
                                insert_sql = (
                                    f"INSERT INTO biz_region ({', '.join(target_cols)}) "
                                    f"SELECT {', '.join(source_exprs)} "
                                    f"FROM `{platform_db}`.sys_regions{where_clause}"
                                )
                                tconn.execute(text(insert_sql))
                        print("[OK] 地区数据已从平台同步")
                    else:
                        print("[SKIP] 平台库无 sys_regions 表，跳过地区同步")
            else:
                print("[SKIP] 地区数据已存在")
    except Exception as e:
        print(f"[WARN] 地区数据同步失败（非致命）: {e}")

    # 同步品牌/车系/经销商（与 TenantService._sync_vehicle_basicdata 一致）
    try:
        platform_db = settings.platform_database_name

        def _cnt_brand(c):
            try:
                return c.execute(text("SELECT COUNT(*) FROM biz_vehicle_brand")).scalar() or 0
            except Exception:
                return -1

        with tenant_engine.begin() as tconn:
            bc = _cnt_brand(tconn)
            if bc < 0:
                print("[SKIP] 租户库无 biz_vehicle_brand 表，跳过车辆/经销商基础同步")
            else:
                if bc == 0:
                    tconn.execute(text(
                        f"INSERT INTO biz_vehicle_brand ("
                        f"brand_id, brand_logo, brand_name_cn, brand_country, "
                        f"brand_introduce, create_time, last_update_time) "
                        f"SELECT brand_id, brand_logo, brand_name_cn, brand_country, "
                        f"brand_introduce, create_time, last_update_time "
                        f"FROM `{platform_db}`.basicdata_brand"
                    ))
                    print("[OK] 品牌数据已从平台同步")
                else:
                    print("[SKIP] 品牌数据已存在")
                sc = tconn.execute(text("SELECT COUNT(*) FROM biz_vehicle_series")).scalar() or 0
                if sc == 0:
                    tconn.execute(text(
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
                    print("[OK] 车系数据已从平台同步")
                else:
                    print("[SKIP] 车系数据已存在")
                dc = tconn.execute(text("SELECT COUNT(*) FROM biz_dealer")).scalar() or 0
                if dc == 0:
                    tconn.execute(text(
                        f"INSERT INTO biz_dealer ("
                        f"dealer_id, dealer_name, dealer_type, main_brand, "
                        f"province, city, address_detail, longitude, latitude, "
                        f"created_at, updated_at) "
                        f"SELECT dealer_id, dealer_name, dealer_type, main_brand, "
                        f"province, city, address_detail, longitude, latitude, "
                        f"created_at, updated_at "
                        f"FROM `{platform_db}`.basicdata_dealer_info"
                    ))
                    print("[OK] 经销商数据已从平台同步")
                else:
                    print("[SKIP] 经销商数据已存在")
    except Exception as e:
        print(f"[WARN] 车辆/经销商基础数据同步失败（非致命）: {e}")

    platform_engine.dispose()
    tenant_engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="一键初始化开发环境")
    parser.add_argument("--reset", action="store_true", help="重置开发企业（删库重建）")
    args = parser.parse_args()

    print("=" * 60)
    print("  智图 SaaS - 开发环境一键初始化")
    print("=" * 60)
    print(f"  开发企业编码: {DEV_TENANT_CODE}")
    print(f"  开发企业名称: {DEV_TENANT_NAME}")
    print(f"  管理员手机号: {DEV_ADMIN_PHONE}")
    print(f"  管理员密码:   123456")
    if args.reset:
        print(f"  模式: 重置（将删除旧开发企业数据库）")
    print("=" * 60)

    step1_init_platform_db()
    step2_seed_platform_data()
    step3_seed_product_features()
    step4_seed_client_menus()
    step5_create_dev_tenant(reset=args.reset)
    step6_assign_enterprise_version()
    step7_seed_tenant_data()

    print("\n" + "=" * 60)
    print("  开发环境初始化完成！")
    print("=" * 60)
    print(f"\n  客户端登录信息：")
    print(f"    地址: http://localhost:5174")
    print(f"    账号: {DEV_ADMIN_PHONE}")
    print(f"    密码: 123456")
    print(f"    企业: {DEV_TENANT_NAME}")
    print(f"\n  管理后台登录信息：")
    print(f"    地址: http://localhost:5173")
    print(f"    账号: 13800000000")
    print(f"    密码: admin123")
    print()


if __name__ == "__main__":
    main()
