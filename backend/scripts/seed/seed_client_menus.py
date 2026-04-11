"""
同步 Client 端菜单数据到 sys_menu 表（upsert 模式）

脚本是菜单数据的唯一真实来源（Single Source of Truth）：
- 新菜单：插入全部字段
- 已有菜单：更新全部字段（以脚本数据为准）

匹配规则：
  - 有 menu_code 的菜单：按 menu_code + app_type 匹配
  - 无 menu_code 的菜单：按 path + parent_id + app_type 匹配

修改菜单（icon、排序、名称等）请直接编辑本文件的 CLIENT_MENUS，
然后执行脚本或通过 deploy.sh db-sync / deploy.sh update 部署到线上。

用法：
    python scripts/seed/seed_client_menus.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


# feature_code 命名规范:
#   base_*     : 基础模块（所有版本可用）
#   resource_* : 资源模块（standard 及以上）
#   partner_*  : 合作伙伴模块（standard 及以上）
#   biz_*      : 业务模块（standard 及以上）
#   billing_*  : 计费模块（standard 及以上）
#   finance_*  : 财务模块（pro 及以上）
#   bi_*       : 数据分析（pro 及以上）

CLIENT_MENUS = [
    # ---- 首页 ----
    {
        "menu_name": "首页",
        "menu_code": None,
        "menu_type": 0,
        "path": "/",
        "component": None,
        "icon": "home",
        "sort_order": 0,
        "feature_code": "base_dashboard",
        "children": [
            {
                "menu_name": "工作台",
                "menu_code": "dashboard:workplace",
                "menu_type": 0,
                "path": "/dashboard/workplace",
                "component": "/dashboard/workplace/index",
                "icon": "workspace",
                "sort_order": 0,
                "feature_code": "base_dashboard",
            },
        ],
    },
    # ---- 数据分析 ----
    {
        "menu_name": "数据分析",
        "menu_code": None,
        "menu_type": 0,
        "path": "/analytics",
        "component": None,
        "icon": "bi",
        "sort_order": 50,
        "feature_code": "bi_analytics",
        "children": [
            {
                "menu_name": "运营看板",
                "menu_code": "analytics:overview",
                "menu_type": 0,
                "path": "/analytics/overview",
                "component": "/dashboard/analysis/index",
                "icon": "DashboardOutlined",
                "sort_order": 0,
                "feature_code": "bi_overview",
            },
            {
                "menu_name": "数据报表",
                "menu_code": "analytics:report",
                "menu_type": 0,
                "path": "/analytics/report",
                "component": "/dashboard/monitor/index",
                "icon": "LineChartOutlined",
                "sort_order": 10,
                "feature_code": "bi_report",
            },
        ],
    },
    # ---- 业务管理 ----
    {
        "menu_name": "业务管理",
        "menu_code": None,
        "menu_type": 0,
        "path": "/business",
        "component": None,
        "icon": "yewuguanli",
        "sort_order": 700,
        "feature_code": "biz_manage",
        "children": [
            {
                "menu_name": "运单管理",
                "menu_code": "business:waybill",
                "menu_type": 0,
                "path": "/business/waybill",
                "component": "/waybill/index",
                "icon": "yundanguanli",
                "sort_order": 0,
                "feature_code": "biz_waybill",
                "children": [
                    {"menu_name": "查询", "menu_code": "business:waybill:list", "menu_type": 1, "sort_order": 0, "feature_code": "biz_waybill"},
                    {"menu_name": "新增", "menu_code": "business:waybill:add", "menu_type": 1, "sort_order": 1, "feature_code": "biz_waybill"},
                    {"menu_name": "编辑", "menu_code": "business:waybill:edit", "menu_type": 1, "sort_order": 2, "feature_code": "biz_waybill"},
                    {"menu_name": "删除", "menu_code": "business:waybill:delete", "menu_type": 1, "sort_order": 3, "feature_code": "biz_waybill"},
                ],
            },
            {
                "menu_name": "调度管理",
                "menu_code": "business:dispatch",
                "menu_type": 0,
                "path": "/business/dispatch",
                "component": "/business/dispatch/index",
                "icon": "ScheduleOutlined",
                "sort_order": 10,
                "feature_code": "biz_dispatch",
            },
            {
                "menu_name": "在途追踪",
                "menu_code": "business:tracking",
                "menu_type": 0,
                "path": "/business/tracking",
                "component": "/business/tracking/index",
                "icon": "EnvironmentOutlined",
                "sort_order": 20,
                "feature_code": "biz_tracking",
            },
            {
                "menu_name": "回单管理",
                "menu_code": "business:receipt",
                "menu_type": 0,
                "path": "/business/receipt",
                "component": "/business/receipt/index",
                "icon": "AuditOutlined",
                "sort_order": 30,
                "feature_code": "biz_receipt",
            },
        ],
    },
    # ---- 财务管理 ----
    {
        "menu_name": "财务管理",
        "menu_code": None,
        "menu_type": 0,
        "path": "/finance",
        "component": None,
        "icon": "caiwuguanli",
        "sort_order": 800,
        "feature_code": "finance_manage",
        "children": [
            {
                "menu_name": "应收管理",
                "menu_code": "finance:receivable",
                "menu_type": 0,
                "path": "/finance/receivable",
                "component": "/finance/receivable/index",
                "icon": "MoneyCollectOutlined",
                "sort_order": 0,
                "feature_code": "finance_receivable",
            },
            {
                "menu_name": "应付管理",
                "menu_code": "finance:payable",
                "menu_type": 0,
                "path": "/finance/payable",
                "component": "/finance/payable/index",
                "icon": "PayCircleOutlined",
                "sort_order": 10,
                "feature_code": "finance_payable",
            },
            {
                "menu_name": "对账管理",
                "menu_code": "finance:reconciliation",
                "menu_type": 0,
                "path": "/finance/reconciliation",
                "component": "/finance/reconciliation/index",
                "icon": "ReconciliationOutlined",
                "sort_order": 20,
                "feature_code": "finance_reconciliation",
            },
        ],
    },
    # ---- 计费引擎 ----
    {
        "menu_name": "计费引擎",
        "menu_code": None,
        "menu_type": 0,
        "path": "/billing",
        "component": None,
        "icon": "jifeiyinqing",
        "sort_order": 825,
        "feature_code": "billing_manage",
        "children": [
            {
                "menu_name": "运价合同",
                "menu_code": "billing:contract",
                "menu_type": 0,
                "path": "/billing/contract",
                "component": "/billing/contract/index",
                "icon": "yunjiaguanli",
                "sort_order": 0,
                "feature_code": "billing_contract",
                "children": [
                    {"menu_name": "查询", "menu_code": "billing:contract:list", "menu_type": 1, "sort_order": 0, "feature_code": "billing_contract"},
                    {"menu_name": "新增", "menu_code": "billing:contract:add", "menu_type": 1, "sort_order": 1, "feature_code": "billing_contract"},
                    {"menu_name": "编辑", "menu_code": "billing:contract:edit", "menu_type": 1, "sort_order": 2, "feature_code": "billing_contract"},
                    {"menu_name": "删除", "menu_code": "billing:contract:delete", "menu_type": 1, "sort_order": 3, "feature_code": "billing_contract"},
                ],
            },
        ],
    },
    # ---- 合作伙伴 ----
    {
        "menu_name": "合作伙伴",
        "menu_code": None,
        "menu_type": 0,
        "path": "/partner",
        "component": None,
        "icon": "hezuohuoban",
        "sort_order": 850,
        "feature_code": "partner_manage",
        "children": [
            {
                "menu_name": "客户管理",
                "menu_code": "partner:customer",
                "menu_type": 0,
                "path": "/partner/customer",
                "component": "/partner/customer/index",
                "icon": "kehuguanli",
                "sort_order": 0,
                "feature_code": "partner_customer",
                "children": [
                    {"menu_name": "查询", "menu_code": "partner:customer:list", "menu_type": 1, "sort_order": 0, "feature_code": "partner_customer"},
                    {"menu_name": "新增", "menu_code": "partner:customer:add", "menu_type": 1, "sort_order": 1, "feature_code": "partner_customer"},
                    {"menu_name": "编辑", "menu_code": "partner:customer:edit", "menu_type": 1, "sort_order": 2, "feature_code": "partner_customer"},
                    {"menu_name": "删除", "menu_code": "partner:customer:delete", "menu_type": 1, "sort_order": 3, "feature_code": "partner_customer"},
                ],
            },
        ],
    },
    # ---- 资源管理 ----
    {
        "menu_name": "资源管理",
        "menu_code": None,
        "menu_type": 0,
        "path": "/resource",
        "component": None,
        "icon": "ziyuanguanli",
        "sort_order": 900,
        "feature_code": "resource_manage",
        "children": [
            {
                "menu_name": "车辆管理",
                "menu_code": "resource:vehicle",
                "menu_type": 0,
                "path": "/resource/vehicle",
                "component": "/resource/vehicle/index",
                "icon": "CarOutlined",
                "sort_order": 0,
                "feature_code": "resource_vehicle",
                "children": [
                    {"menu_name": "查询", "menu_code": "resource:vehicle:list", "menu_type": 1, "sort_order": 0, "feature_code": "resource_vehicle"},
                    {"menu_name": "新增", "menu_code": "resource:vehicle:add", "menu_type": 1, "sort_order": 1, "feature_code": "resource_vehicle"},
                    {"menu_name": "编辑", "menu_code": "resource:vehicle:edit", "menu_type": 1, "sort_order": 2, "feature_code": "resource_vehicle"},
                    {"menu_name": "删除", "menu_code": "resource:vehicle:delete", "menu_type": 1, "sort_order": 3, "feature_code": "resource_vehicle"},
                ],
            },
            {
                "menu_name": "挂车管理",
                "menu_code": "resource:trailer",
                "menu_type": 0,
                "path": "/resource/trailer",
                "component": "/resource/trailer/index",
                "icon": "CarOutlined",
                "sort_order": 5,
                "feature_code": "resource_trailer",
                "children": [
                    {"menu_name": "查询", "menu_code": "resource:trailer:list", "menu_type": 1, "sort_order": 0, "feature_code": "resource_trailer"},
                    {"menu_name": "新增", "menu_code": "resource:trailer:add", "menu_type": 1, "sort_order": 1, "feature_code": "resource_trailer"},
                    {"menu_name": "编辑", "menu_code": "resource:trailer:edit", "menu_type": 1, "sort_order": 2, "feature_code": "resource_trailer"},
                    {"menu_name": "删除", "menu_code": "resource:trailer:delete", "menu_type": 1, "sort_order": 3, "feature_code": "resource_trailer"},
                ],
            },
            {
                "menu_name": "驾驶员管理",
                "menu_code": "resource:driver",
                "menu_type": 0,
                "path": "/resource/driver",
                "component": "/resource/driver/index",
                "icon": "IdcardOutlined",
                "sort_order": 10,
                "feature_code": "resource_driver",
            },
            {
                "menu_name": "客户管理",
                "menu_code": "resource:customer",
                "menu_type": 0,
                "path": "/resource/customer",
                "component": "/resource/customer/index",
                "icon": "ContactsOutlined",
                "sort_order": 20,
                "feature_code": "resource_customer",
            },
            {
                "menu_name": "路线管理",
                "menu_code": "resource:route",
                "menu_type": 0,
                "path": "/resource/route",
                "component": "/resource/route/index",
                "icon": "NodeIndexOutlined",
                "sort_order": 30,
                "feature_code": "resource_route",
            },
        ],
    },
    # ---- 基础数据 ----
    {
        "menu_name": "基础数据",
        "menu_code": None,
        "menu_type": 0,
        "path": "/basic_data",
        "component": None,
        "icon": "jichushuju",
        "sort_order": 950,
        "feature_code": "basic_data",
        "children": [
            {
                "menu_name": "地区数据",
                "menu_code": "basic_data:regional_data",
                "menu_type": 0,
                "path": "/basic_data/regional_data",
                "component": "/basic_data/regional_data/index",
                "icon": "xingzhengquhua",
                "sort_order": 0,
                "feature_code": "basic_data_region",
                "children": [
                    {"menu_name": "查询", "menu_code": "basic_data:regional_data:list", "menu_type": 1, "sort_order": 0, "feature_code": "basic_data_region"},
                    {"menu_name": "新增", "menu_code": "basic_data:regional_data:add", "menu_type": 1, "sort_order": 1, "feature_code": "basic_data_region"},
                    {"menu_name": "编辑", "menu_code": "basic_data:regional_data:edit", "menu_type": 1, "sort_order": 2, "feature_code": "basic_data_region"},
                    {"menu_name": "删除", "menu_code": "basic_data:regional_data:delete", "menu_type": 1, "sort_order": 3, "feature_code": "basic_data_region"},
                ],
            },
            {
                "menu_name": "品牌车型",
                "menu_code": "basic_data:vehicle_brand_series",
                "menu_type": 0,
                "path": "/basic_data/brand_series",
                "component": "/basic_data/brand_series/index",
                "icon": "pinpaichexing",
                "sort_order": 10,
                "feature_code": "basic_data_vehicle_brand_series",
                "children": [
                    {"menu_name": "查询", "menu_code": "basic_data:vehicle_brand_series:list", "menu_type": 1, "sort_order": 0, "feature_code": "basic_data_vehicle_brand_series"},
                    {"menu_name": "新增", "menu_code": "basic_data:vehicle_brand_series:add", "menu_type": 1, "sort_order": 1, "feature_code": "basic_data_vehicle_brand_series"},
                    {"menu_name": "编辑", "menu_code": "basic_data:vehicle_brand_series:edit", "menu_type": 1, "sort_order": 2, "feature_code": "basic_data_vehicle_brand_series"},
                    {"menu_name": "删除", "menu_code": "basic_data:vehicle_brand_series:delete", "menu_type": 1, "sort_order": 3, "feature_code": "basic_data_vehicle_brand_series"},
                ],
            },
            {
                "menu_name": "经销商门店",
                "menu_code": "basic_data:dealer",
                "menu_type": 0,
                "path": "/basic_data/dealer",
                "component": "/basic_data/dealer/index",
                "icon": "jingxiaoshang",
                "sort_order": 20,
                "feature_code": "basic_data_dealer",
                "children": [
                    {"menu_name": "查询", "menu_code": "basic_data:dealer:list", "menu_type": 1, "sort_order": 0, "feature_code": "basic_data_dealer"},
                    {"menu_name": "新增", "menu_code": "basic_data:dealer:add", "menu_type": 1, "sort_order": 1, "feature_code": "basic_data_dealer"},
                    {"menu_name": "编辑", "menu_code": "basic_data:dealer:edit", "menu_type": 1, "sort_order": 2, "feature_code": "basic_data_dealer"},
                    {"menu_name": "删除", "menu_code": "basic_data:dealer:delete", "menu_type": 1, "sort_order": 3, "feature_code": "basic_data_dealer"},
                ],
            },
        ],
    },
    # ---- 系统管理 ----
    {
        "menu_name": "系统管理",
        "menu_code": None,
        "menu_type": 0,
        "path": "/system",
        "component": None,
        "icon": "setting",
        "sort_order": 1000,
        "feature_code": "base_system",
        "children": [
            {
                "menu_name": "组织架构",
                "menu_code": "system:organization",
                "menu_type": 0,
                "path": "/system/organization",
                "component": "/system/organization/index",
                "icon": "zzjg",
                "sort_order": 0,
                "feature_code": "base_organization",
            },
            {
                "menu_name": "员工管理",
                "menu_code": "system:user",
                "menu_type": 0,
                "path": "/system/user",
                "component": "/system/user/index",
                "icon": "yonghuguanli",
                "sort_order": 10,
                "feature_code": "base_user",
                "children": [
                    {"menu_name": "查询", "menu_code": "system:user:list", "menu_type": 1, "sort_order": 0, "feature_code": "base_user"},
                    {"menu_name": "新增", "menu_code": "system:user:add", "menu_type": 1, "sort_order": 1, "feature_code": "base_user"},
                    {"menu_name": "编辑", "menu_code": "system:user:edit", "menu_type": 1, "sort_order": 2, "feature_code": "base_user"},
                    {"menu_name": "删除", "menu_code": "system:user:delete", "menu_type": 1, "sort_order": 3, "feature_code": "base_user"},
                ],
            },
            {
                "menu_name": "角色管理",
                "menu_code": "system:role",
                "menu_type": 0,
                "path": "/system/role",
                "component": "/system/role/index",
                "icon": "role",
                "sort_order": 20,
                "feature_code": "base_role",
            },
            {
                "menu_name": "数据字典",
                "menu_code": "system:dictionary",
                "menu_type": 0,
                "path": "/system/dictionary",
                "component": "/system/dictionary/index",
                "icon": "dataa",
                "sort_order": 30,
                "feature_code": "base_dict",
            },
            {
                "menu_name": "系统设置",
                "menu_code": "system:config",
                "menu_type": 0,
                "path": "/system/config",
                "component": "/system/config/index",
                "icon": "ControlOutlined",
                "sort_order": 35,
                "feature_code": "base_config",
            },
            {
                "menu_name": "操作记录",
                "menu_code": "system:operation-record",
                "menu_type": 0,
                "path": "/system/operation-record",
                "component": "/logcenter/operation-record/index",
                "icon": "czrz",
                "sort_order": 40,
                "feature_code": "base_log",
            },
            {
                "menu_name": "登录记录",
                "menu_code": "system:login-record",
                "menu_type": 0,
                "path": "/system/login-record",
                "component": "/system/login-record/index",
                "icon": "dlrz",
                "sort_order": 50,
                "feature_code": "base_log",
            },
        ],
    },
    # ---- 个人中心（隐藏路由，visible=0） ----
    {
        "menu_name": "个人中心",
        "menu_code": None,
        "menu_type": 0,
        "path": "/user/profile",
        "component": "/user/profile/index",
        "icon": "",
        "sort_order": 1100,
        "visible": 0,
        "feature_code": "",
    },
    # ---- 消息中心（隐藏路由，visible=0） ----
    {
        "menu_name": "消息中心",
        "menu_code": None,
        "menu_type": 0,
        "path": "/user/message",
        "component": "/user/message/index",
        "icon": "",
        "sort_order": 1200,
        "visible": 0,
        "feature_code": "",
    },
]


def upsert_menus(conn, menus, parent_id=0):
    """
    递归同步菜单树（upsert 模式，脚本数据为唯一真实来源）

    匹配规则：
      - 有 menu_code 的菜单：按 menu_code + app_type 匹配（跨父级唯一）
      - 无 menu_code 的菜单：按 path + parent_id + app_type 匹配（避免改名导致重复）
    """
    for menu in menus:
        children = menu.pop("children", None)
        menu_code = menu.get("menu_code")
        menu_path = menu.get("path")
        visible = menu.get("visible", 1)

        if menu_code:
            result = conn.execute(text(
                "SELECT id FROM sys_menu "
                "WHERE menu_code = :code AND app_type = 'client' AND is_deleted = 0"
            ), {"code": menu_code})
        else:
            result = conn.execute(text(
                "SELECT id FROM sys_menu "
                "WHERE path = :path AND app_type = 'client' "
                "AND parent_id = :pid AND is_deleted = 0"
            ), {"path": menu_path, "pid": parent_id})

        existing_id = result.scalar()

        if existing_id:
            conn.execute(text(
                "UPDATE sys_menu SET "
                "menu_name = :menu_name, menu_code = :menu_code, "
                "menu_type = :menu_type, path = :path, component = :component, "
                "icon = :icon, sort_order = :sort_order, visible = :visible, "
                "feature_code = :feature_code, parent_id = :parent_id "
                "WHERE id = :id"
            ), {
                "id": existing_id,
                "parent_id": parent_id,
                "menu_name": menu["menu_name"],
                "menu_code": menu_code,
                "menu_type": menu["menu_type"],
                "path": menu_path,
                "component": menu.get("component"),
                "icon": menu.get("icon"),
                "sort_order": menu.get("sort_order", 0),
                "visible": visible,
                "feature_code": menu.get("feature_code"),
            })
            menu_id = existing_id
            print(f"  更新菜单: {menu['menu_name']} (id={menu_id})")
        else:
            conn.execute(text(
                "INSERT INTO sys_menu "
                "(parent_id, menu_name, menu_code, menu_type, path, component, "
                "icon, sort_order, visible, status, app_type, feature_code, is_deleted) "
                "VALUES (:parent_id, :menu_name, :menu_code, :menu_type, :path, "
                ":component, :icon, :sort_order, :visible, 1, 'client', :feature_code, 0)"
            ), {
                "parent_id": parent_id,
                "menu_name": menu["menu_name"],
                "menu_code": menu_code,
                "menu_type": menu["menu_type"],
                "path": menu_path,
                "component": menu.get("component"),
                "icon": menu.get("icon"),
                "sort_order": menu.get("sort_order", 0),
                "visible": visible,
                "feature_code": menu.get("feature_code"),
            })
            result = conn.execute(text("SELECT LAST_INSERT_ID()"))
            menu_id = result.scalar()
            print(f"  新增菜单: {menu['menu_name']} (id={menu_id}, feature_code={menu.get('feature_code')})")

        if children:
            upsert_menus(conn, children, parent_id=menu_id)


def main():
    settings = get_settings()
    db_name = settings.platform_database_name
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{db_name}?charset=utf8mb4"
    )
    engine = create_engine(url)

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = :db AND table_name = 'sys_menu' "
            "AND column_name = 'feature_code'"
        ), {"db": db_name})
        if result.scalar() == 0:
            print("添加 feature_code 列...")
            conn.execute(text(
                "ALTER TABLE sys_menu ADD COLUMN feature_code VARCHAR(50) DEFAULT NULL "
                "COMMENT '关联功能编码' AFTER app_type"
            ))
            conn.execute(text("CREATE INDEX idx_feature_code ON sys_menu (feature_code)"))
            conn.commit()
            print("feature_code 列已添加")

    import copy
    menus = copy.deepcopy(CLIENT_MENUS)
    with engine.connect() as conn:
        print("\n开始同步 Client 端菜单...")
        upsert_menus(conn, menus)
        conn.commit()

    engine.dispose()
    print("\nClient 端菜单同步完成！")


if __name__ == "__main__":
    main()
