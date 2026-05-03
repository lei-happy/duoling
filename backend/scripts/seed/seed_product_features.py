"""
初始化产品功能清单和版本-功能关联（v2.0）

对应：项目文档/02.需求文档/02.企业端/01.客户端菜单架构重构设计.md (v2.0)

用法：
    python scripts/seed_product_features.py

v2.0 关键变化：
1. 承运资源新增三类（自营/外协/社会），新增 carrier_external、carrier_social
2. 供应商管理 partner_supplier 由 enterprise 提前到 standard
3. 新增审批中心 approval_manage、审批流程配置 approval_config
4. 路线管理由 resource_route 迁移为 billing_route（归入计费中心）
5. 新增财务远期能力：finance_invoice、finance_profit
6. 新增计费远期能力：billing_cost_rule、billing_fee_template
7. 新增运力远期能力：fleet_maintenance、fleet_compliance
8. 新增 BI 远期能力：bi_prediction
9. 新增 AI 助手 ai_assistant
10. 预留生态平台三大厅：ecosystem_cargo_hall / ecosystem_capacity_hall / ecosystem_service_hall
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

# ---------------------------------------------------------------------------
# 功能清单（feature_code 全集）
# 与 sys_menu.json 中的 feature_code 字段一一对应
# ---------------------------------------------------------------------------
FEATURES = [
    # ===== 智能工作台 =====
    {"feature_code": "base_dashboard", "feature_name": "工作台", "module": "dashboard", "sort_order": 0, "required_tables": None},
    {"feature_code": "ai_assistant", "feature_name": "AI 数字员工", "module": "dashboard", "sort_order": 5, "required_tables": '["biz_ai_session", "biz_ai_message", "biz_ai_tool_call_log", "biz_ai_context"]'},
    # 子能力：远期可独立挂版本控制（当前继承 ai_assistant 总开关）
    {"feature_code": "ai_form_recorder", "feature_name": "AI 录单员", "module": "dashboard", "sort_order": 6, "required_tables": None},
    {"feature_code": "ai_data_analyst", "feature_name": "AI 数据分析员", "module": "dashboard", "sort_order": 7, "required_tables": None},

    # ===== 企业管理（含基础数据）=====
    {"feature_code": "base_system", "feature_name": "企业管理", "module": "enterprise", "sort_order": 10, "required_tables": None},
    {"feature_code": "base_organization", "feature_name": "组织架构", "module": "enterprise", "sort_order": 11, "required_tables": None},
    {"feature_code": "base_user", "feature_name": "员工管理", "module": "enterprise", "sort_order": 12, "required_tables": None},
    {"feature_code": "base_role", "feature_name": "角色权限", "module": "enterprise", "sort_order": 13, "required_tables": None},
    {"feature_code": "base_dict", "feature_name": "数据字典", "module": "enterprise", "sort_order": 14, "required_tables": None},
    {"feature_code": "base_log", "feature_name": "操作/登录记录", "module": "enterprise", "sort_order": 15, "required_tables": None},
    {"feature_code": "base_config", "feature_name": "系统设置", "module": "enterprise", "sort_order": 16, "required_tables": None},
    {"feature_code": "basic_data", "feature_name": "基础数据", "module": "enterprise", "sort_order": 17, "required_tables": None},
    {"feature_code": "basic_data_region", "feature_name": "地区数据", "module": "enterprise", "sort_order": 18, "required_tables": None},
    {"feature_code": "basic_data_vehicle_brand_series", "feature_name": "品牌车型", "module": "enterprise", "sort_order": 19, "required_tables": '["biz_vehicle_brand", "biz_vehicle_series"]'},

    # ===== 运营调度 =====
    {"feature_code": "biz_waybill", "feature_name": "运单管理", "module": "operation", "sort_order": 30, "required_tables": '["biz_waybill"]'},
    {"feature_code": "biz_dispatch", "feature_name": "智能调度", "module": "operation", "sort_order": 31, "required_tables": '["biz_waybill"]'},
    {"feature_code": "biz_tracking", "feature_name": "在途监控", "module": "operation", "sort_order": 32, "required_tables": '["biz_waybill"]'},
    {"feature_code": "biz_receipt", "feature_name": "回单签收", "module": "operation", "sort_order": 33, "required_tables": '["biz_waybill"]'},

    # ===== 运力中心 =====
    {"feature_code": "capacity_manage", "feature_name": "运力调配/记录", "module": "capacity", "sort_order": 40, "required_tables": '["biz_capacity", "biz_capacity_log"]'},
    {"feature_code": "resource_vehicle", "feature_name": "车辆管理", "module": "capacity", "sort_order": 41, "required_tables": '["biz_vehicle", "biz_vehicle_ext"]'},
    {"feature_code": "resource_trailer", "feature_name": "挂车管理", "module": "capacity", "sort_order": 42, "required_tables": '["biz_trailer", "biz_trailer_ext"]'},
    {"feature_code": "resource_driver", "feature_name": "驾驶员管理", "module": "capacity", "sort_order": 43, "required_tables": '["biz_driver", "biz_driver_license", "biz_driver_operation", "biz_driver_account", "biz_driver_route"]'},
    {"feature_code": "carrier_external", "feature_name": "外协供应商运力", "module": "capacity", "sort_order": 44, "required_tables": None},
    {"feature_code": "carrier_social", "feature_name": "社会运力池", "module": "capacity", "sort_order": 45, "required_tables": None},
    {"feature_code": "fleet_maintenance", "feature_name": "车辆维保", "module": "capacity", "sort_order": 46, "required_tables": None},
    {"feature_code": "fleet_compliance", "feature_name": "证照监控", "module": "capacity", "sort_order": 47, "required_tables": None},

    # ===== 客商中心 =====
    {"feature_code": "partner_customer", "feature_name": "客户管理", "module": "partner", "sort_order": 50, "required_tables": '["biz_customer"]'},
    {"feature_code": "basic_data_dealer", "feature_name": "经销商门店", "module": "partner", "sort_order": 51, "required_tables": '["biz_dealer"]'},
    {"feature_code": "partner_supplier", "feature_name": "供应商管理", "module": "partner", "sort_order": 52, "required_tables": None},

    # ===== 计费中心 =====
    {"feature_code": "billing_contract", "feature_name": "运价合同", "module": "billing", "sort_order": 60, "required_tables": '["biz_freight_contract", "biz_freight_rate"]'},
    {"feature_code": "billing_route", "feature_name": "路线管理", "module": "billing", "sort_order": 61, "required_tables": '["biz_route"]'},
    {"feature_code": "billing_cost_rule", "feature_name": "成本规则", "module": "billing", "sort_order": 62, "required_tables": None},
    {"feature_code": "billing_fee_template", "feature_name": "费用模板", "module": "billing", "sort_order": 63, "required_tables": None},

    # ===== 审批中心 =====
    {"feature_code": "approval_manage", "feature_name": "审批中心", "module": "approval", "sort_order": 70, "required_tables": None},
    {"feature_code": "approval_config", "feature_name": "审批流程配置", "module": "approval", "sort_order": 71, "required_tables": None},

    # ===== 财务结算 =====
    {"feature_code": "finance_receivable", "feature_name": "应收管理", "module": "finance", "sort_order": 80, "required_tables": None},
    {"feature_code": "finance_payable", "feature_name": "应付管理（三类路径）", "module": "finance", "sort_order": 81, "required_tables": None},
    {"feature_code": "finance_reconciliation", "feature_name": "对账中心（含供应商对账）", "module": "finance", "sort_order": 82, "required_tables": None},
    {"feature_code": "finance_invoice", "feature_name": "发票管理", "module": "finance", "sort_order": 83, "required_tables": None},
    {"feature_code": "finance_profit", "feature_name": "利润分析", "module": "finance", "sort_order": 84, "required_tables": None},

    # ===== 数据洞察 =====
    {"feature_code": "bi_overview", "feature_name": "运营看板", "module": "insight", "sort_order": 90, "required_tables": None},
    {"feature_code": "bi_report", "feature_name": "数据报表（+承运结构分析）", "module": "insight", "sort_order": 91, "required_tables": None},
    {"feature_code": "bi_prediction", "feature_name": "智能预测", "module": "insight", "sort_order": 92, "required_tables": None},

    # ===== 生态平台（v2.0 预留） =====
    {"feature_code": "ecosystem_cargo_hall", "feature_name": "货源大厅", "module": "ecosystem", "sort_order": 100, "required_tables": None},
    {"feature_code": "ecosystem_capacity_hall", "feature_name": "运力大厅", "module": "ecosystem", "sort_order": 101, "required_tables": None},
    {"feature_code": "ecosystem_service_hall", "feature_name": "服务大厅", "module": "ecosystem", "sort_order": 102, "required_tables": None},
]


# ---------------------------------------------------------------------------
# 版本-功能关联（v2.0 阶梯式累加）
#
# basic   = 基础管理：工作台 + 企业管理（含基础数据）
# standard= basic + 运营调度 + 运力中心（自营/外协/社会三类）
#                + 客商中心（含供应商管理）+ 计费中心（基础）
# pro     = standard + 审批中心 + 财务结算（应收/应付/对账）+ 数据洞察（基础）
# enterprise = pro + AI 助手 + 远期高阶能力（车辆维保/证照监控/智能预测/
#              利润分析/发票管理/成本规则/费用模板/审批流程配置）
# ecosystem (远期) = enterprise + 生态平台三大厅
# ---------------------------------------------------------------------------

_BASIC_FEATURES = [
    # 智能工作台
    "base_dashboard",
    # 企业管理（含基础数据）
    "base_system", "base_organization", "base_user", "base_role",
    "base_dict", "base_log", "base_config",
    "basic_data", "basic_data_region", "basic_data_vehicle_brand_series",
]

_STANDARD_DELTA = [
    # 运营调度
    "biz_waybill", "biz_dispatch", "biz_tracking", "biz_receipt",
    # 运力中心（含 v2.0 三类承运资源）
    "capacity_manage", "resource_vehicle", "resource_trailer", "resource_driver",
    "carrier_external", "carrier_social",
    # 客商中心（v2.0 供应商管理提前到 standard）
    "partner_customer", "basic_data_dealer", "partner_supplier",
    # 计费中心（基础）
    "billing_contract", "billing_route",
]

_PRO_DELTA = [
    # 审批中心
    "approval_manage",
    # 财务结算（基础）
    "finance_receivable", "finance_payable", "finance_reconciliation",
    # 数据洞察（基础）
    "bi_overview", "bi_report",
]

_ENTERPRISE_DELTA = [
    # 智能工作台·AI 数字员工（含子能力）
    "ai_assistant", "ai_form_recorder", "ai_data_analyst",
    # 运力中心·远期
    "fleet_maintenance", "fleet_compliance",
    # 计费中心·远期
    "billing_cost_rule", "billing_fee_template",
    # 审批流程配置
    "approval_config",
    # 财务结算·远期
    "finance_invoice", "finance_profit",
    # 数据洞察·远期
    "bi_prediction",
]

_ECOSYSTEM_DELTA = [
    # 生态平台（远期，预留）
    "ecosystem_cargo_hall", "ecosystem_capacity_hall", "ecosystem_service_hall",
]

VERSION_FEATURES = {
    "basic": list(_BASIC_FEATURES),
    "standard": _BASIC_FEATURES + _STANDARD_DELTA,
    "pro": _BASIC_FEATURES + _STANDARD_DELTA + _PRO_DELTA,
    "enterprise": _BASIC_FEATURES + _STANDARD_DELTA + _PRO_DELTA + _ENTERPRISE_DELTA,
    "ecosystem": _BASIC_FEATURES + _STANDARD_DELTA + _PRO_DELTA + _ENTERPRISE_DELTA + _ECOSYSTEM_DELTA,
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
                print(f"  版本 {version_code} 不存在，跳过（如需启用请先在 seed_data.py 创建该版本）")
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

        # ---- 末尾自检：打印「脏 feature_code」「未绑版本 feature_code」清单 ----
        feature_codes_in_features = {f["feature_code"] for f in FEATURES}

        menu_codes_rows = conn.execute(text(
            "SELECT DISTINCT feature_code FROM sys_menu "
            "WHERE app_type = 'client' AND is_deleted = 0 "
            "AND feature_code IS NOT NULL AND feature_code <> ''"
        )).fetchall()
        menu_codes = {r[0] for r in menu_codes_rows if r[0]}

        bound_codes_rows = conn.execute(text(
            "SELECT DISTINCT pf.feature_code "
            "FROM sys_product_feature pf "
            "JOIN sys_version_feature vf ON vf.feature_id = pf.id "
            "WHERE pf.is_deleted = 0 AND vf.is_deleted = 0 AND vf.status = 1"
        )).fetchall()
        bound_codes = {r[0] for r in bound_codes_rows if r[0]}

        orphan = sorted(menu_codes - feature_codes_in_features)
        unbound = sorted(feature_codes_in_features - bound_codes)

        print("\n========== 全链路自检 ==========")
        if orphan:
            print(f"[警告] sys_menu 中引用但 FEATURES 未定义的脏 feature_code 共 {len(orphan)} 个：")
            for c in orphan:
                print(f"  - {c}")
            print("  请使用 backend/scripts/fix/fix_stale_feature_codes.py 修复")
        else:
            print("[OK] sys_menu 全部 feature_code 均在 FEATURES 中存在")

        if unbound:
            print(f"[提示] FEATURES 中存在但任何启用版本都未勾选的 feature_code 共 {len(unbound)} 个：")
            for c in unbound:
                print(f"  - {c}")
        else:
            print("[OK] 所有功能都至少已关联到一个版本")
        print("==================================\n")

    engine.dispose()
    print("\n产品功能清单和版本关联初始化完成！")


if __name__ == "__main__":
    main()
