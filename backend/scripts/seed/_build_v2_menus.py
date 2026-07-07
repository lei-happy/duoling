"""
v2.0 菜单数据构建脚本（一次性工具）

按照《01.客户端菜单架构重构设计.md》v2.0 设计：
1. 读取现有 sys_menu.json
2. 应用 v2.0 转换：重命名/移动现有 client 菜单，新增 v2.0 菜单，软删除废弃容器
3. 输出新的 sys_menu.json

设计原则：
- 保留现有菜单的 ID 与 menu_code，避免破坏角色权限关联
- 仅更新 menu_name/parent_id/path/sort_order/feature_code/icon/component
- 新菜单使用 300+ 的 ID，避免与现有 ID 冲突
- 废弃容器（资源管理/基础数据 root）标记为 is_deleted=1
"""

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sys_menu.json"
DST = ROOT / "sys_menu.json"  # in-place 覆盖

NOW = "19/4/2026 12:00:00"

# ---------------------------------------------------------------------------
# v2.0 一级菜单（更新现有 + 新增预留位）
# 字段：menu_name / menu_code / path / icon / sort_order / visible / feature_code
# ---------------------------------------------------------------------------
LEVEL1_UPDATES = {
    164: dict(menu_name="智能工作台", menu_code=None, path="/dashboard", component=None,
              icon="smart-workspace", sort_order=0, visible=1, feature_code="base_dashboard"),
    191: dict(menu_name="运营调度", menu_code=None, path="/operation", component=None,
              icon="yunying", sort_order=100, visible=1, feature_code=None),
    260: dict(menu_name="运力中心", menu_code="capacity", path="/capacity", component=None,
              icon="yunli", sort_order=200, visible=1, feature_code="capacity_manage"),
    237: dict(menu_name="客商中心", menu_code=None, path="/partner", component=None,
              icon="keshang", sort_order=300, visible=1, feature_code=None),
    248: dict(menu_name="计费中心", menu_code=None, path="/billing", component=None,
              icon="jifei", sort_order=400, visible=1, feature_code=None),
    196: dict(menu_name="财务结算", menu_code=None, path="/finance", component=None,
              icon="caiwu", sort_order=600, visible=1, feature_code=None),
    215: dict(menu_name="数据洞察", menu_code=None, path="/insight", component=None,
              icon="shuju", sort_order=700, visible=1, feature_code=None),
    166: dict(menu_name="企业管理", menu_code=None, path="/enterprise", component=None,
              icon="qiye", sort_order=900, visible=1, feature_code="base_system"),
}

# 软删除的现有一级容器（其子项已迁出）
LEVEL1_DEPRECATED = {
    177: "资源管理 → 拆分到运力中心 / 计费中心",
    208: "基础数据 → 归入企业管理",
}

# ---------------------------------------------------------------------------
# v2.0 二级菜单更新（保留 ID 与 menu_code）
# ---------------------------------------------------------------------------
LEVEL2_UPDATES = {
    # 智能工作台（parent=164）
    165: dict(parent_id=164, menu_name="今日工作台", menu_code="dashboard:workplace",
             path="/dashboard/workplace", component="/dashboard/workplace/index",
             icon="workspace", sort_order=0, visible=1, feature_code="base_dashboard"),
    # 运营调度（parent=191）
    243: dict(parent_id=191, menu_name="运单管理", menu_code="business:waybill",
             path="/operation/waybill", component="/business/waybill/index",
             icon="yundanguanli", sort_order=0, visible=1, feature_code="biz_waybill"),
    193: dict(parent_id=191, menu_name="智能调度", menu_code="business:dispatch",
             path="/operation/dispatch", component="/business/dispatch/index",
             icon="ScheduleOutlined", sort_order=10, visible=1, feature_code="biz_dispatch"),
    194: dict(parent_id=191, menu_name="在途监控", menu_code="business:tracking",
             path="/operation/tracking", component="/operation/tracking/index",
             icon="EnvironmentOutlined", sort_order=20, visible=1, feature_code="biz_tracking"),
    195: dict(parent_id=191, menu_name="回单签收", menu_code="business:receipt",
             path="/operation/receipt", component="/operation/receipt/index",
             icon="AuditOutlined", sort_order=30, visible=1, feature_code="biz_receipt"),
    # 运力中心（parent=260）—— 从原 资源管理(177) 迁入
    178: dict(parent_id=260, menu_name="车辆管理", menu_code="resource:vehicle",
             path="/capacity/vehicle", component="/resource/vehicle/index",
             icon="cheliang", sort_order=0, visible=1, feature_code="resource_vehicle"),
    183: dict(parent_id=260, menu_name="挂车管理", menu_code="resource:trailer",
             path="/capacity/trailer", component="/resource/trailer/index",
             icon="guache", sort_order=10, visible=1, feature_code="resource_trailer"),
    188: dict(parent_id=260, menu_name="驾驶员管理", menu_code="resource:driver",
             path="/capacity/driver", component="/resource/driver/index",
             icon="jiashiyuanguanli", sort_order=20, visible=1, feature_code="resource_driver"),
    261: dict(parent_id=260, menu_name="运力调配", menu_code="capacity:list",
             path="/capacity/dispatch", component="/capacity/list/index",
             icon="yunliliebiao", sort_order=50, visible=1, feature_code="capacity_manage"),
    265: dict(parent_id=260, menu_name="运力记录", menu_code="capacity:log",
             path="/capacity/dispatch-log", component="/capacity/log/index",
             icon="lishijilu", sort_order=60, visible=1, feature_code="capacity_manage"),
    # 客商中心（parent=237）—— 经销商门店从原 基础数据(208) 迁入
    238: dict(parent_id=237, menu_name="客户管理", menu_code="partner:customer",
             path="/partner/customer", component="/partner/customer/index",
             icon="kehuguanli", sort_order=0, visible=1, feature_code="partner_customer"),
    232: dict(parent_id=237, menu_name="经销商门店", menu_code="basic_data:dealer",
             path="/partner/dealer", component="/basic_data/dealer/index",
             icon="jingxiaoshang", sort_order=10, visible=1, feature_code="basic_data_dealer"),
    # 计费中心（parent=248）—— 路线管理从原 资源管理(177) 迁入并改 feature_code
    249: dict(parent_id=248, menu_name="运价合同", menu_code="billing:contract",
             path="/billing/contract", component="/billing/contract/index",
             icon="yunjiaguanli", sort_order=0, visible=1, feature_code="billing_contract"),
    190: dict(parent_id=248, menu_name="路线管理", menu_code="resource:route",
             path="/billing/route", component="/resource/route/index",
             icon="NodeIndexOutlined", sort_order=10, visible=1, feature_code="billing_route"),
    # 财务结算（parent=196）
    197: dict(parent_id=196, menu_name="应收管理", menu_code="finance:receivable",
             path="/finance/receivable", component="/finance/receivable/index",
             icon="MoneyCollectOutlined", sort_order=0, visible=1, feature_code="finance_receivable"),
    198: dict(parent_id=196, menu_name="应付管理", menu_code="finance:payable",
             path="/finance/payable", component="/finance/payable/index",
             icon="PayCircleOutlined", sort_order=10, visible=1, feature_code="finance_payable"),
    199: dict(parent_id=196, menu_name="对账中心", menu_code="finance:reconciliation",
             path="/finance/reconciliation", component="/finance/reconciliation/index",
             icon="ReconciliationOutlined", sort_order=20, visible=1, feature_code="finance_reconciliation"),
    # 数据洞察（parent=215）
    201: dict(parent_id=215, menu_name="运营看板", menu_code="analytics:overview",
             path="/insight/overview", component="/dashboard/analysis/index",
             icon="DashboardOutlined", sort_order=0, visible=1, feature_code="bi_overview"),
    202: dict(parent_id=215, menu_name="数据报表", menu_code="analytics:report",
             path="/insight/report", component="/dashboard/monitor/index",
             icon="LineChartOutlined", sort_order=10, visible=1, feature_code="bi_report"),
    # 企业管理（parent=166）
    167: dict(parent_id=166, menu_name="组织架构", menu_code="system:organization",
             path="/enterprise/organization", component="/system/organization/index",
             icon="zzjg", sort_order=0, visible=1, feature_code="base_organization"),
    168: dict(parent_id=166, menu_name="员工管理", menu_code="system:user",
             path="/enterprise/user", component="/system/user/index",
             icon="yonghuguanli", sort_order=10, visible=1, feature_code="base_user"),
    173: dict(parent_id=166, menu_name="角色权限", menu_code="system:role",
             path="/enterprise/role", component="/system/role/index",
             icon="role", sort_order=20, visible=1, feature_code="base_role"),
    174: dict(parent_id=166, menu_name="数据字典", menu_code="system:dictionary",
             path="/enterprise/dictionary", component="/system/dictionary/index",
             icon="dataa", sort_order=40, visible=1, feature_code="base_dict"),
    254: dict(parent_id=166, menu_name="系统设置", menu_code="system:config",
             path="/enterprise/config", component="/system/config/index",
             icon="galileoset", sort_order=50, visible=1, feature_code="base_config"),
    175: dict(parent_id=166, menu_name="操作记录", menu_code="system:operation-record",
             path="/enterprise/operation-log", component="/logcenter/operation-record/index",
             icon="czrz", sort_order=60, visible=1, feature_code="base_log"),
    176: dict(parent_id=166, menu_name="登录记录", menu_code="system:login-record",
             path="/enterprise/login-log", component="/logcenter/login-record/index",
             icon="dlrz", sort_order=70, visible=1, feature_code="base_log"),
    # 基础数据（parent=320 新容器）—— 从原 基础数据(208) 迁入
    210: dict(parent_id=320, menu_name="地区数据", menu_code="basic_data:regional_data",
             path="/enterprise/basic-data/regional", component="/basic_data/regional_data/index",
             icon="xingzhengquhua", sort_order=0, visible=1, feature_code="basic_data_region"),
    224: dict(parent_id=320, menu_name="品牌车型", menu_code="basic_data:vehicle_brand_series",
             path="/enterprise/basic-data/brand-series", component="/basic_data/brand_series/index",
             icon="pinpaichexing", sort_order=10, visible=1, feature_code="basic_data_vehicle_brand_series"),
}

# ---------------------------------------------------------------------------
# 三级按钮权限：parent_id 不变（仍指向其所属菜单 ID），无需更新
# 但由于父菜单可能改了 menu_code，子按钮 menu_code 保持原状即可（已是 child:list 等格式）
# 这里仅做一致性校验，不需要修改
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# v2.0 新增菜单（ID 从 300 起步）
# ---------------------------------------------------------------------------
def _new_menu(id_, parent_id, menu_name, menu_code, menu_type, path, component,
              icon, sort_order, visible, feature_code):
    return {
        "parent_id": parent_id,
        "menu_name": menu_name,
        "menu_code": menu_code,
        "menu_type": menu_type,
        "path": path,
        "component": component,
        "icon": icon,
        "sort_order": sort_order,
        "visible": visible,
        "status": 1,
        "app_type": "client",
        "feature_code": feature_code,
        "id": id_,
        "created_at": NOW,
        "updated_at": NOW,
        "is_deleted": 0,
    }


NEW_MENUS = [
    # 一级菜单：审批中心 / 生态平台（预留）
    _new_menu(300, 0, "审批中心", "approval", 0, "/approval", None,
              "shenpi", 500, 1, "approval_manage"),
    _new_menu(301, 0, "生态平台", "ecosystem", 0, "/ecosystem", None,
              "shengtai", 800, 0, None),  # visible=0 预留
    # 智能工作台：数字员工
    _new_menu(302, 164, "数字员工", "dashboard:ai-assistant", 0,
              "/dashboard/ai-assistant", "/dashboard/ai-assistant/index",
              "AI", 10, 1, "ai_assistant"),  # 旗舰版默认放开
    # 运力中心：外协供应商 / 社会运力池 / 车辆维保（远期） / 证照监控（远期）
    _new_menu(303, 260, "外协供应商", "capacity:external-carrier", 0,
              "/capacity/external-carrier", "/capacity/external-carrier/index",
              "waixiegongyingshang", 30, 1, "carrier_external"),
    _new_menu(304, 260, "社会运力池", "capacity:social", 0,
              "/capacity/social", "/capacity/social/index",
              "shehuiyunli", 40, 1, "carrier_social"),
    _new_menu(305, 260, "车辆维保", "capacity:maintenance", 0,
              "/capacity/maintenance", "/capacity/maintenance/index",
              "weibao", 70, 0, "fleet_maintenance"),  # visible=0 远期
    _new_menu(306, 260, "证照监控", "capacity:compliance", 0,
              "/capacity/compliance", "/capacity/compliance/index",
              "zhengjian", 80, 0, "fleet_compliance"),  # visible=0 远期
    # 客商中心：供应商管理
    _new_menu(307, 237, "供应商管理", "partner:supplier", 0,
              "/partner/supplier", "/partner/supplier/index",
              "gongyingshang", 20, 1, "partner_supplier"),
    # 计费中心：成本政策（任务支出成本自动计算引擎）/ 费用模板（远期）
    _new_menu(308, 248, "成本政策", "billing:cost-policy", 0,
              "/billing/cost-policy", "/billing/cost-policy/index",
              "chengbenguize", 20, 1, "billing_cost_rule"),
    _new_menu(830, 308, "查询", "billing:cost-policy:list", 1,
              None, None, "", 0, 1, "billing_cost_rule"),
    _new_menu(831, 308, "新增", "billing:cost-policy:add", 1,
              None, None, "", 1, 1, "billing_cost_rule"),
    _new_menu(832, 308, "编辑", "billing:cost-policy:edit", 1,
              None, None, "", 2, 1, "billing_cost_rule"),
    _new_menu(833, 308, "删除", "billing:cost-policy:delete", 1,
              None, None, "", 3, 1, "billing_cost_rule"),
    _new_menu(834, 308, "重算", "billing:cost-policy:recalc", 1,
              None, None, "", 4, 1, "billing_cost_rule"),
    # 社会运力资金账户（往来账）按钮点（parent 344 运力列表）
    _new_menu(835, 344, "资金账户", "capacity:social_capacity:list:fund-account", 1,
              None, None, "", 7, 1, "capacity_social_list"),
    _new_menu(836, 344, "资金记账", "capacity:social_capacity:list:fund-post", 1,
              None, None, "", 8, 1, "capacity_social_list"),
    _new_menu(837, 344, "冻结/解冻资金账户", "capacity:social_capacity:list:fund-freeze", 1,
              None, None, "", 9, 1, "capacity_social_list"),
    _new_menu(309, 248, "费用模板", "billing:fee-template", 0,
              "/billing/fee-template", "/billing/fee-template/index",
              "feiyongmoban", 30, 0, "billing_fee_template"),  # visible=0 远期
    # 审批中心子菜单
    _new_menu(310, 300, "我的待办", "approval:pending", 0,
              "/approval/pending", "/approval/pending/index",
              "daiban", 0, 1, "approval_manage"),
    _new_menu(311, 300, "我的申请", "approval:initiated", 0,
              "/approval/initiated", "/approval/initiated/index",
              "shenqing", 10, 1, "approval_manage"),
    _new_menu(312, 300, "审批记录", "approval:history", 0,
              "/approval/history", "/approval/history/index",
              "lishi", 20, 1, "approval_manage"),
    # 财务结算：发票管理（远期）/ 利润分析（远期）
    _new_menu(313, 196, "发票管理", "finance:invoice", 0,
              "/finance/invoice", "/finance/invoice/index",
              "fapiao", 30, 0, "finance_invoice"),  # visible=0 远期
    _new_menu(314, 196, "利润分析", "finance:profit", 0,
              "/finance/profit", "/finance/profit/index",
              "lirun", 40, 0, "finance_profit"),  # visible=0 远期
    # 数据洞察：智能预测（远期）
    _new_menu(315, 215, "智能预测", "insight:prediction", 0,
              "/insight/prediction", "/insight/prediction/index",
              "yuce", 20, 0, "bi_prediction"),  # visible=0 远期
    # 生态平台子菜单（visible=0 预留）
    _new_menu(316, 301, "货源大厅", "ecosystem:cargo-hall", 0,
              "/ecosystem/cargo-hall", "/ecosystem/cargo-hall/index",
              "huoyuan", 0, 0, "ecosystem_cargo_hall"),
    _new_menu(317, 301, "运力大厅", "ecosystem:capacity-hall", 0,
              "/ecosystem/capacity-hall", "/ecosystem/capacity-hall/index",
              "yunlidating", 10, 0, "ecosystem_capacity_hall"),
    _new_menu(318, 301, "服务大厅", "ecosystem:service-hall", 0,
              "/ecosystem/service-hall", "/ecosystem/service-hall/index",
              "fuwu", 20, 0, "ecosystem_service_hall"),
    # 企业管理：审批流程配置 + 基础数据容器
    _new_menu(319, 166, "审批流程配置", "enterprise:approval-config", 0,
              "/enterprise/approval-config", "/enterprise/approval-config/index",
              "liucheng", 25, 1, "approval_config"),
    _new_menu(320, 166, "基础数据", "enterprise:basic-data", 0,
              "/enterprise/basic-data", None,
              "jichushuju", 30, 1, "basic_data"),
]


def transform(rows: list) -> list:
    """对 rows 应用 v2.0 转换"""
    by_id = {int(r["id"]): r for r in rows}

    # 1. 软删除废弃容器
    for mid, reason in LEVEL1_DEPRECATED.items():
        if mid in by_id:
            r = by_id[mid]
            r["is_deleted"] = 1
            r["updated_at"] = NOW

    # 2. 应用一级菜单更新
    for mid, patch in LEVEL1_UPDATES.items():
        if mid in by_id:
            r = by_id[mid]
            for k, v in patch.items():
                r[k] = v
            r["updated_at"] = NOW

    # 3. 应用二级菜单更新
    for mid, patch in LEVEL2_UPDATES.items():
        if mid in by_id:
            r = by_id[mid]
            for k, v in patch.items():
                r[k] = v
            r["updated_at"] = NOW
        else:
            print(f"  [WARN] 未找到 ID={mid}，跳过更新")

    # 4. 追加新增菜单（避免重复）
    existing_ids = set(by_id.keys())
    for nm in NEW_MENUS:
        if nm["id"] not in existing_ids:
            rows.append(nm)
        else:
            print(f"  [WARN] 新增菜单 ID={nm['id']} 已存在，跳过")

    return rows


def main():
    with open(SRC, encoding="utf-8") as f:
        rows = json.load(f)

    print(f"原始记录数: {len(rows)}")
    rows = transform(rows)
    print(f"v2.0 后记录数: {len(rows)}")

    with open(DST, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"已写入: {DST}")


if __name__ == "__main__":
    main()
