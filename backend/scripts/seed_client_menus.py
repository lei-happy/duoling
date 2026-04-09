"""
同步 Client 端菜单数据到 sys_menu 表（upsert 模式）

- 新菜单：插入全部字段（含默认 icon、sort_order）
- 已有菜单：只更新结构字段（path/component/feature_code/menu_type），
            保留用户在后台自定义的 icon、sort_order、visible

安全说明：此脚本可在生产环境重复执行，不会破坏用户已有的菜单配置。

用法：
    python scripts/seed_client_menus.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


# feature_code 命名规范:
#   base_*     : 基础模块（所有版本可用）
#   resource_* : 资源模块（standard 及以上）
#   biz_*      : 业务模块（standard 及以上）
#   finance_*  : 财务模块（pro 及以上）
#   bi_*       : 数据分析（pro 及以上）

CLIENT_MENUS = [
    # ---- 首页 ----
    {
        "menu_name": "首页",
        "menu_code": None,
        "menu_type": 0,  # 0=菜单/目录, 1=按钮
        "path": "/",
        "component": None,
        "icon": "HomeOutlined",
        "sort_order": 0,
        "feature_code": "base_dashboard",
        "children": [
            {
                "menu_name": "工作台",
                "menu_code": "dashboard:workplace",
                "menu_type": 0,
                "path": "/dashboard/workplace",
                "component": "/dashboard/workplace/index",
                "icon": "DesktopOutlined",
                "sort_order": 0,
                "feature_code": "base_dashboard",
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
        "icon": "SettingOutlined",
        "sort_order": 10,
        "feature_code": "base_system",
        "children": [
            {
                "menu_name": "组织架构",
                "menu_code": "system:organization",
                "menu_type": 0,
                "path": "/system/organization",
                "component": "/system/organization/index",
                "icon": "ApartmentOutlined",
                "sort_order": 0,
                "feature_code": "base_organization",
            },
            {
                "menu_name": "员工管理",
                "menu_code": "system:user",
                "menu_type": 0,
                "path": "/system/user",
                "component": "/system/user/index",
                "icon": "UserOutlined",
                "sort_order": 10,
                "feature_code": "base_user",
                "children": [
                    {
                        "menu_name": "查询",
                        "menu_code": "system:user:list",
                        "menu_type": 1,
                        "sort_order": 0,
                        "feature_code": "base_user",
                    },
                    {
                        "menu_name": "新增",
                        "menu_code": "system:user:add",
                        "menu_type": 1,
                        "sort_order": 1,
                        "feature_code": "base_user",
                    },
                    {
                        "menu_name": "编辑",
                        "menu_code": "system:user:edit",
                        "menu_type": 1,
                        "sort_order": 2,
                        "feature_code": "base_user",
                    },
                    {
                        "menu_name": "删除",
                        "menu_code": "system:user:delete",
                        "menu_type": 1,
                        "sort_order": 3,
                        "feature_code": "base_user",
                    },
                ],
            },
            {
                "menu_name": "角色管理",
                "menu_code": "system:role",
                "menu_type": 0,
                "path": "/system/role",
                "component": "/system/role/index",
                "icon": "TeamOutlined",
                "sort_order": 20,
                "feature_code": "base_role",
            },
            {
                "menu_name": "数据字典",
                "menu_code": "system:dictionary",
                "menu_type": 0,
                "path": "/system/dictionary",
                "component": "/system/dictionary/index",
                "icon": "BookOutlined",
                "sort_order": 30,
                "feature_code": "base_dict",
            },
            {
                "menu_name": "操作记录",
                "menu_code": "system:operation-record",
                "menu_type": 0,
                "path": "/system/operation-record",
                "component": "/logcenter/operation-record/index",
                "icon": "FileTextOutlined",
                "sort_order": 40,
                "feature_code": "base_log",
            },
            {
                "menu_name": "登录记录",
                "menu_code": "system:login-record",
                "menu_type": 0,
                "path": "/system/login-record",
                "component": "/system/login-record/index",
                "icon": "LoginOutlined",
                "sort_order": 50,
                "feature_code": "base_log",
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
        "icon": "DatabaseOutlined",
        "sort_order": 20,
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
    # ---- 业务管理 ----
    {
        "menu_name": "业务管理",
        "menu_code": None,
        "menu_type": 0,
        "path": "/business",
        "component": None,
        "icon": "SolutionOutlined",
        "sort_order": 30,
        "feature_code": "biz_manage",
        "children": [
            {
                "menu_name": "运单管理",
                "menu_code": "business:order",
                "menu_type": 0,
                "path": "/business/order",
                "component": "/business/order/index",
                "icon": "FileProtectOutlined",
                "sort_order": 0,
                "feature_code": "biz_order",
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
    # ---- 基础数据 ----
    {
        "menu_name": "基础数据",
        "menu_code": None,
        "menu_type": 0,
        "path": "/basic_data",
        "component": None,
        "icon": "AppstoreOutlined",
        "sort_order": 35,
        "feature_code": "basic_data",
        "children": [
            {
                "menu_name": "地区数据",
                "menu_code": "basic_data:regional_data",
                "menu_type": 0,
                "path": "/basic_data/regional_data",
                "component": "/basic_data/regional_data/index",
                "icon": "EnvironmentOutlined",
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
                "icon": "CarOutlined",
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
                "icon": "ShopOutlined",
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
    # ---- 财务管理 ----
    {
        "menu_name": "财务管理",
        "menu_code": None,
        "menu_type": 0,
        "path": "/finance",
        "component": None,
        "icon": "AccountBookOutlined",
        "sort_order": 40,
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
    # ---- 数据分析 ----
    {
        "menu_name": "数据分析",
        "menu_code": None,
        "menu_type": 0,
        "path": "/analytics",
        "component": None,
        "icon": "BarChartOutlined",
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
]


def upsert_menus(conn, menus, parent_id=0):
    """
    递归同步菜单树（upsert 模式）

    已存在的菜单：只更新结构字段（path/component/feature_code/menu_type/menu_name），
                  保留用户自定义的 icon、sort_order、visible 不被覆盖。
    不存在的菜单：使用脚本中的全部默认值插入。

    匹配规则：
      - 有 menu_code 的菜单：按 menu_code + app_type 匹配（跨父级唯一）
      - 无 menu_code 的菜单（顶级目录）：按 menu_name + parent_id + app_type 匹配
    """
    for menu in menus:
        children = menu.pop("children", None)
        menu_code = menu.get("menu_code")

        if menu_code:
            result = conn.execute(text(
                "SELECT id FROM sys_menu "
                "WHERE menu_code = :code AND app_type = 'client' AND is_deleted = 0"
            ), {"code": menu_code})
        else:
            result = conn.execute(text(
                "SELECT id FROM sys_menu "
                "WHERE menu_name = :name AND app_type = 'client' "
                "AND parent_id = :pid AND is_deleted = 0"
            ), {"name": menu["menu_name"], "pid": parent_id})

        existing_id = result.scalar()

        if existing_id:
            conn.execute(text(
                "UPDATE sys_menu SET "
                "menu_name = :menu_name, menu_code = :menu_code, "
                "menu_type = :menu_type, path = :path, component = :component, "
                "feature_code = :feature_code, parent_id = :parent_id "
                "WHERE id = :id"
            ), {
                "id": existing_id,
                "parent_id": parent_id,
                "menu_name": menu["menu_name"],
                "menu_code": menu_code,
                "menu_type": menu["menu_type"],
                "path": menu.get("path"),
                "component": menu.get("component"),
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
                ":component, :icon, :sort_order, 1, 1, 'client', :feature_code, 0)"
            ), {
                "parent_id": parent_id,
                "menu_name": menu["menu_name"],
                "menu_code": menu_code,
                "menu_type": menu["menu_type"],
                "path": menu.get("path"),
                "component": menu.get("component"),
                "icon": menu.get("icon"),
                "sort_order": menu.get("sort_order", 0),
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

    # 确保 feature_code 列存在
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
