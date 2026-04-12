"""
初始化产品功能清单和版本-功能关联

用法：
    python scripts/seed_product_features.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

FEATURES = [
    # 基础模块 (所有版本)
    {"feature_code": "base_dashboard", "feature_name": "工作台", "module": "base", "sort_order": 0, "required_tables": None},
    {"feature_code": "base_system", "feature_name": "系统管理", "module": "base", "sort_order": 1, "required_tables": None},
    {"feature_code": "base_organization", "feature_name": "组织架构", "module": "base", "sort_order": 2, "required_tables": None},
    {"feature_code": "base_user", "feature_name": "员工管理", "module": "base", "sort_order": 3, "required_tables": None},
    {"feature_code": "base_role", "feature_name": "角色管理", "module": "base", "sort_order": 4, "required_tables": None},
    {"feature_code": "base_dict", "feature_name": "数据字典", "module": "base", "sort_order": 5, "required_tables": None},
    {"feature_code": "base_log", "feature_name": "日志记录", "module": "base", "sort_order": 6, "required_tables": None},
    {"feature_code": "base_config", "feature_name": "系统设置", "module": "base", "sort_order": 7, "required_tables": None},
    # 基础数据模块 (所有版本)
    {"feature_code": "basic_data", "feature_name": "基础数据", "module": "basic_data", "sort_order": 7, "required_tables": None},
    {"feature_code": "basic_data_region", "feature_name": "地区数据管理", "module": "basic_data", "sort_order": 8, "required_tables": None},
    {"feature_code": "basic_data_vehicle_brand_series", "feature_name": "品牌车型管理", "module": "basic_data", "sort_order": 9, "required_tables": '["biz_vehicle_brand", "biz_vehicle_series"]'},
    {"feature_code": "basic_data_dealer", "feature_name": "经销商门店管理", "module": "basic_data", "sort_order": 10, "required_tables": '["biz_dealer"]'},
    # 资源模块 (standard 及以上)
    {"feature_code": "resource_manage", "feature_name": "资源管理", "module": "resource", "sort_order": 10, "required_tables": None},
    {"feature_code": "resource_vehicle", "feature_name": "车辆管理", "module": "resource", "sort_order": 11, "required_tables": '["biz_vehicle", "biz_vehicle_ext"]'},
    {"feature_code": "resource_trailer", "feature_name": "挂车管理", "module": "resource", "sort_order": 12, "required_tables": '["biz_trailer", "biz_trailer_ext"]'},
    {"feature_code": "resource_driver", "feature_name": "驾驶员管理", "module": "resource", "sort_order": 13, "required_tables": '["biz_driver", "biz_driver_license", "biz_driver_operation", "biz_driver_account", "biz_driver_route"]'},
    {"feature_code": "resource_route", "feature_name": "路线管理", "module": "resource", "sort_order": 14, "required_tables": '["biz_route"]'},
    # 合作伙伴模块 (standard 及以上)
    {"feature_code": "partner_manage", "feature_name": "合作伙伴", "module": "partner", "sort_order": 15, "required_tables": None},
    {"feature_code": "partner_customer", "feature_name": "客户管理", "module": "partner", "sort_order": 16, "required_tables": '["biz_customer"]'},
    # 业务模块 (standard 及以上)
    {"feature_code": "biz_manage", "feature_name": "业务管理", "module": "biz", "sort_order": 20, "required_tables": None},
    {"feature_code": "biz_waybill", "feature_name": "运单管理", "module": "biz", "sort_order": 21, "required_tables": '["biz_waybill"]'},
    {"feature_code": "biz_dispatch", "feature_name": "调度管理", "module": "biz", "sort_order": 22, "required_tables": '["biz_waybill"]'},
    {"feature_code": "biz_tracking", "feature_name": "在途追踪", "module": "biz", "sort_order": 23, "required_tables": '["biz_waybill"]'},
    {"feature_code": "biz_receipt", "feature_name": "回单管理", "module": "biz", "sort_order": 24, "required_tables": '["biz_waybill"]'},
    # 计费引擎模块 (standard 及以上)
    {"feature_code": "billing_manage", "feature_name": "计费管理", "module": "billing", "sort_order": 25, "required_tables": None},
    {"feature_code": "billing_contract", "feature_name": "运价合同", "module": "billing", "sort_order": 26, "required_tables": '["biz_freight_contract", "biz_freight_rate"]'},
    # 财务模块 (pro 及以上)
    {"feature_code": "finance_manage", "feature_name": "财务管理", "module": "finance", "sort_order": 30, "required_tables": None},
    {"feature_code": "finance_receivable", "feature_name": "应收管理", "module": "finance", "sort_order": 31, "required_tables": None},
    {"feature_code": "finance_payable", "feature_name": "应付管理", "module": "finance", "sort_order": 32, "required_tables": None},
    {"feature_code": "finance_reconciliation", "feature_name": "对账管理", "module": "finance", "sort_order": 33, "required_tables": None},
    # 数据分析 (pro 及以上)
    {"feature_code": "bi_analytics", "feature_name": "数据分析", "module": "bi", "sort_order": 40, "required_tables": None},
    {"feature_code": "bi_overview", "feature_name": "运营看板", "module": "bi", "sort_order": 41, "required_tables": None},
    {"feature_code": "bi_report", "feature_name": "数据报表", "module": "bi", "sort_order": 42, "required_tables": None},
]

# 版本包含的功能（feature_code 列表）
VERSION_FEATURES = {
    "basic": [
        "base_dashboard", "base_system", "base_organization", "base_user",
        "base_role", "base_dict", "base_log", "base_config",
        "basic_data", "basic_data_region", "basic_data_vehicle_brand_series",
        "basic_data_dealer",
    ],
    "standard": [
        "base_dashboard", "base_system", "base_organization", "base_user",
        "base_role", "base_dict", "base_log", "base_config",
        "basic_data", "basic_data_region", "basic_data_vehicle_brand_series",
        "basic_data_dealer",
        "resource_manage", "resource_vehicle", "resource_trailer", "resource_driver",
        "resource_route",
        "partner_manage", "partner_customer",
        "biz_manage", "biz_waybill", "biz_dispatch", "biz_tracking", "biz_receipt",
        "billing_manage", "billing_contract",
    ],
    "pro": [
        "base_dashboard", "base_system", "base_organization", "base_user",
        "base_role", "base_dict", "base_log", "base_config",
        "basic_data", "basic_data_region", "basic_data_vehicle_brand_series",
        "basic_data_dealer",
        "resource_manage", "resource_vehicle", "resource_trailer", "resource_driver",
        "resource_route",
        "partner_manage", "partner_customer",
        "biz_manage", "biz_waybill", "biz_dispatch", "biz_tracking", "biz_receipt",
        "billing_manage", "billing_contract",
        "finance_manage", "finance_receivable", "finance_payable", "finance_reconciliation",
        "bi_analytics", "bi_overview", "bi_report",
    ],
    "enterprise": [
        "base_dashboard", "base_system", "base_organization", "base_user",
        "base_role", "base_dict", "base_log", "base_config",
        "basic_data", "basic_data_region", "basic_data_vehicle_brand_series",
        "basic_data_dealer",
        "resource_manage", "resource_vehicle", "resource_trailer", "resource_driver",
        "resource_route",
        "partner_manage", "partner_customer",
        "biz_manage", "biz_waybill", "biz_dispatch", "biz_tracking", "biz_receipt",
        "billing_manage", "billing_contract",
        "finance_manage", "finance_receivable", "finance_payable", "finance_reconciliation",
        "bi_analytics", "bi_overview", "bi_report",
    ],
}


def main():
    settings = get_settings()
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)

    with engine.connect() as conn:
        # 确保表存在
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sys_product_feature (
                id BIGINT NOT NULL AUTO_INCREMENT,
                feature_code VARCHAR(50) NOT NULL,
                feature_name VARCHAR(100) NOT NULL,
                module VARCHAR(50) DEFAULT NULL,
                description VARCHAR(255) DEFAULT NULL,
                required_tables JSON DEFAULT NULL,
                sort_order SMALLINT DEFAULT 0,
                status SMALLINT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted SMALLINT DEFAULT 0,
                PRIMARY KEY (id),
                UNIQUE KEY uk_feature_code (feature_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品功能清单表'
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sys_version_feature (
                id BIGINT NOT NULL AUTO_INCREMENT,
                version_id BIGINT NOT NULL,
                feature_id BIGINT NOT NULL,
                status SMALLINT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted SMALLINT DEFAULT 0,
                PRIMARY KEY (id),
                KEY idx_vf_version_id (version_id),
                KEY idx_vf_feature_id (feature_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='版本功能关联表'
        """))
        conn.commit()

        # 插入或更新功能清单
        for f in FEATURES:
            result = conn.execute(text(
                "SELECT id FROM sys_product_feature WHERE feature_code = :code AND is_deleted = 0"
            ), {"code": f["feature_code"]})
            existing_id = result.scalar()
            rt = f["required_tables"]
            if existing_id:
                conn.execute(text(
                    "UPDATE sys_product_feature "
                    "SET feature_name = :name, module = :module, sort_order = :sort, required_tables = :tables "
                    "WHERE id = :id"
                ), {
                    "id": existing_id,
                    "name": f["feature_name"],
                    "module": f["module"],
                    "sort": f["sort_order"],
                    "tables": rt,
                })
                print(f"  更新功能: {f['feature_code']} (id={existing_id})")
            else:
                conn.execute(text(
                    "INSERT INTO sys_product_feature (feature_code, feature_name, module, sort_order, required_tables) "
                    "VALUES (:code, :name, :module, :sort, :tables)"
                ), {
                    "code": f["feature_code"],
                    "name": f["feature_name"],
                    "module": f["module"],
                    "sort": f["sort_order"],
                    "tables": rt,
                })
                print(f"  插入功能: {f['feature_code']} - {f['feature_name']}")
        conn.commit()

        # 建立版本-功能关联
        for version_code, feature_codes in VERSION_FEATURES.items():
            result = conn.execute(text(
                "SELECT id FROM sys_product_version WHERE version_code = :code AND is_deleted = 0"
            ), {"code": version_code})
            version_id = result.scalar()
            if not version_id:
                print(f"  版本 {version_code} 不存在，跳过")
                continue

            # 清除旧关联
            conn.execute(text(
                "UPDATE sys_version_feature SET is_deleted = 1 WHERE version_id = :vid"
            ), {"vid": version_id})

            for fc in feature_codes:
                result = conn.execute(text(
                    "SELECT id FROM sys_product_feature WHERE feature_code = :code AND is_deleted = 0"
                ), {"code": fc})
                feature_id = result.scalar()
                if not feature_id:
                    continue
                conn.execute(text(
                    "INSERT INTO sys_version_feature (version_id, feature_id, status) "
                    "VALUES (:vid, :fid, 1)"
                ), {"vid": version_id, "fid": feature_id})

            print(f"  版本 {version_code}: 关联 {len(feature_codes)} 个功能")
        conn.commit()

    engine.dispose()
    print("\n产品功能清单和版本关联初始化完成！")


if __name__ == "__main__":
    main()
