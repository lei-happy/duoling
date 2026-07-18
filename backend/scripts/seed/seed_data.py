"""
初始种子数据
创建超级管理员、默认角色、基础菜单、角色-菜单关联、产品版本等初始数据
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.common.utils import hash_password

# 导入模型
from app.modules.console.models.system.user import User
from app.modules.console.models.system.role import Role
from app.modules.console.models.system.user_role import UserRole
from app.modules.console.models.system.menu import Menu
from app.modules.console.models.system.permission import RoleMenu
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.dictionary.dict_model import Dict, DictItem
from app.modules.console.models.system.platform_setting import PlatformSetting
from app.modules.console.constants.open_register_policy import (
    KEY_OPEN_REGISTER_DEFAULT_VERSION_CODE,
    KEY_OPEN_REGISTER_TRIAL_DAYS,
    DEFAULT_VERSION_CODE,
    DEFAULT_TRIAL_DAYS,
)


def seed_platform_data():
    """写入平台种子数据"""
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    with Session(engine) as session:
        # ---- 1. 超级管理员 ----
        existing_admin = session.query(User).filter_by(phone="13800000000").first()
        role_admin = session.query(Role).filter_by(role_code="super_admin").first()

        if not existing_admin:
            admin = User(
                password=hash_password("admin123"),
                real_name="超级管理员",
                phone="13800000000",
                user_type=0,  # 平台管理员
                status=1,
            )
            session.add(admin)
            session.flush()
            print("[OK] 超级管理员已创建 (13800000000 / admin123)")

            # ---- 2. 默认角色 ----
            if not role_admin:
                role_admin = Role(
                    role_code="super_admin",
                    role_name="超级管理员",
                    role_type=0,
                    sort_order=0,
                    status=1,
                )
                session.add(role_admin)
                session.flush()
                print("[OK] 默认角色已创建")

            # 关联用户角色
            session.add(UserRole(user_id=admin.id, role_id=role_admin.id))
        else:
            print("[SKIP] 超级管理员已存在")
            if not role_admin:
                role_admin = Role(
                    role_code="super_admin",
                    role_name="超级管理员",
                    role_type=0,
                    sort_order=0,
                    status=1,
                )
                session.add(role_admin)
                session.flush()
                print("[OK] 默认角色已创建")

        # ---- 3. 平台管理菜单 ----
        # menu_type 说明：0=目录/菜单页面  1=按钮权限
        # 前端会过滤掉 menuType===1 的项（不在侧边栏显示）
        existing_menu = session.query(Menu).filter_by(
            menu_name="系统管理", app_type="platform"
        ).first()

        all_menus = []
        if not existing_menu:
            # 顶级菜单（目录）
            menus = [
                Menu(parent_id=0, menu_name="工作台", menu_code="dashboard",
                     menu_type=0, path="/dashboard",
                     component="/dashboard/workplace/index",
                     icon="HomeFilled", sort_order=0, app_type="platform"),
                Menu(parent_id=0, menu_name="客户运营中心", menu_code="customer",
                     menu_type=0, path="/customer",
                     icon="DataAnalysis", sort_order=10, app_type="platform"),
                Menu(parent_id=0, menu_name="基础数据", menu_code="basic_data",
                     menu_type=0, path="/basic_data",
                     icon="AppstoreOutlined", sort_order=15, app_type="platform"),
                Menu(parent_id=0, menu_name="数据同步", menu_code="data_sync",
                     menu_type=0, path="/data_sync",
                     icon="DownloadOutlined", sort_order=17, app_type="platform"),
                Menu(parent_id=0, menu_name="系统管理", menu_code="system",
                     menu_type=0, path="/system",
                     icon="Setting", sort_order=20, app_type="platform"),
                Menu(parent_id=0, menu_name="产品管理", menu_code="product",
                     menu_type=0, path="/product",
                     icon="Box", sort_order=30, app_type="platform"),
            ]
            session.add_all(menus)
            session.flush()

            # 子菜单（页面，menu_type=0）
            customer_menu = next(m for m in menus if m.menu_code == "customer")
            basic_data_menu = next(m for m in menus if m.menu_code == "basic_data")
            data_sync_menu = next(m for m in menus if m.menu_code == "data_sync")
            system_menu = next(m for m in menus if m.menu_code == "system")
            product_menu = next(m for m in menus if m.menu_code == "product")

            sub_menus = [
                # 基础数据子菜单
                Menu(parent_id=basic_data_menu.id, menu_name="地区数据",
                     menu_code="basic_data:region", menu_type=0,
                     path="/basic_data/regional_data",
                     component="/basic_data/regional_data/index",
                     icon="EnvironmentOutlined",
                     sort_order=0, app_type="platform"),
                Menu(parent_id=basic_data_menu.id, menu_name="品牌与车系",
                     menu_code="basic_data:vehicle_brand_series", menu_type=0,
                     path="/basic_data/brand_series",
                     component="/basic_data/brand_series/index",
                     icon="CarOutlined",
                     sort_order=5, app_type="platform"),
                Menu(parent_id=basic_data_menu.id, menu_name="经销商门店",
                     menu_code="basic_data:dealer", menu_type=0,
                     path="/basic_data/dealer",
                     component="/basic_data/dealer/index",
                     icon="ShopOutlined",
                     sort_order=10, app_type="platform"),
                # 数据同步子菜单
                Menu(parent_id=data_sync_menu.id, menu_name="汽车之家同步",
                     menu_code="data_sync:autohome", menu_type=0,
                     path="/data_sync/autohome",
                     component="/data_sync/autohome/index",
                     icon="CarOutlined",
                     sort_order=0, app_type="platform"),
                Menu(parent_id=data_sync_menu.id, menu_name="经销商数据同步",
                     menu_code="data_sync:dealer", menu_type=0,
                     path="/data_sync/dealer",
                     component="/data_sync/dealer/index",
                     icon="ShopOutlined",
                     sort_order=5, app_type="platform"),
                Menu(parent_id=data_sync_menu.id, menu_name="行政区域同步",
                     menu_code="data_sync:region", menu_type=0,
                     path="/data_sync/region",
                     component="/data_sync/region/index",
                     icon="EnvironmentOutlined",
                     sort_order=3, app_type="platform"),
                # 客户运营中心子菜单
                Menu(parent_id=customer_menu.id, menu_name="试用期客户",
                     menu_code="customer:trial", menu_type=0,
                     path="/customer/trial", component="/customer/trial/index",
                     sort_order=0, app_type="platform"),
                Menu(parent_id=customer_menu.id, menu_name="付费客户",
                     menu_code="customer:paid", menu_type=0,
                     path="/customer/paid", component="/customer/paid/index",
                     sort_order=10, app_type="platform"),
                Menu(parent_id=customer_menu.id, menu_name="流失客户",
                     menu_code="customer:churned", menu_type=0,
                     path="/customer/churned", component="/customer/churned/index",
                     sort_order=20, app_type="platform"),
                Menu(parent_id=customer_menu.id, menu_name="自助注册策略",
                     menu_code="customer:open-register-policy", menu_type=0,
                     path="/customer/open-register-policy",
                     component="/customer/open-register-policy/index",
                     icon="Setting", sort_order=8, app_type="platform"),
                # 系统管理子菜单
                Menu(parent_id=system_menu.id, menu_name="用户管理",
                     menu_code="system:user", menu_type=0,
                     path="/system/user", component="/system/user/index",
                     sort_order=0, app_type="platform"),
                Menu(parent_id=system_menu.id, menu_name="角色管理",
                     menu_code="system:role", menu_type=0,
                     path="/system/role", component="/system/role/index",
                     sort_order=10, app_type="platform"),
                Menu(parent_id=system_menu.id, menu_name="菜单管理",
                     menu_code="system:menu", menu_type=0,
                     path="/system/menu", component="/system/menu/index",
                     sort_order=20, app_type="platform"),
                Menu(parent_id=system_menu.id, menu_name="客户端菜单",
                     menu_code="system:client-menu", menu_type=0,
                     path="/system/client-menu", component="/system/client-menu/index",
                     sort_order=25, app_type="platform"),
                Menu(parent_id=system_menu.id, menu_name="短信验证码",
                     menu_code="system:sms-code", menu_type=0,
                     path="/system/sms-code", component="/system/sms-code/index",
                     sort_order=27, app_type="platform"),
                Menu(parent_id=system_menu.id, menu_name="数据字典",
                     menu_code="system:dict", menu_type=0,
                     path="/system/dictionary", component="/system/dictionary/index",
                     sort_order=30, app_type="platform"),
                Menu(parent_id=system_menu.id, menu_name="操作日志",
                     menu_code="system:log", menu_type=0,
                     path="/system/log", component="/system/log/index",
                     sort_order=40, app_type="platform"),
                # 产品管理子菜单
                Menu(parent_id=product_menu.id, menu_name="版本管理",
                     menu_code="product:version", menu_type=0,
                     path="/product/version", component="/product/version/index",
                     sort_order=0, app_type="platform"),
                Menu(parent_id=product_menu.id, menu_name="功能模块",
                     menu_code="product:feature", menu_type=0,
                     path="/product/feature", component="/product/feature/index",
                     sort_order=5, app_type="platform"),
                Menu(parent_id=product_menu.id, menu_name="授权管理",
                     menu_code="product:auth", menu_type=0,
                     path="/product/auth", component="/product/auth/index",
                     sort_order=10, app_type="platform"),
                Menu(parent_id=product_menu.id, menu_name="更新记录",
                     menu_code="product:changelog", menu_type=0,
                     path="/product/changelog", component="/product/changelog/index",
                     sort_order=20, app_type="platform"),
            ]
            session.add_all(sub_menus)
            session.flush()

            all_menus = menus + sub_menus
            print("[OK] 平台菜单已创建")
        else:
            # 菜单已存在，查出所有平台菜单用于后续关联
            all_menus = session.query(Menu).filter_by(
                app_type="platform", is_deleted=0
            ).all()
            print("[SKIP] 平台菜单已存在")
            # 补充：更新记录菜单（若不存在）
            product_menu = session.query(Menu).filter_by(
                menu_code="product", app_type="platform", is_deleted=0
            ).first()
            changelog_menu = session.query(Menu).filter_by(
                menu_code="product:changelog", app_type="platform", is_deleted=0
            ).first()
            if product_menu and not changelog_menu:
                m = Menu(
                    parent_id=product_menu.id, menu_name="更新记录",
                    menu_code="product:changelog", menu_type=0,
                    path="/product/changelog", component="/product/changelog/index",
                    sort_order=20, app_type="platform",
                )
                session.add(m)
                session.flush()
                all_menus.append(m)
                # 超级管理员关联新菜单
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
                print("[OK] 更新记录菜单已补充")

            # 补充：功能模块菜单（若不存在）
            feature_menu = session.query(Menu).filter_by(
                menu_code="product:feature", app_type="platform", is_deleted=0
            ).first()
            if product_menu and not feature_menu:
                m = Menu(
                    parent_id=product_menu.id, menu_name="功能模块",
                    menu_code="product:feature", menu_type=0,
                    path="/product/feature", component="/product/feature/index",
                    sort_order=5, app_type="platform",
                )
                session.add(m)
                session.flush()
                all_menus.append(m)
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
                print("[OK] 功能模块菜单已补充")

            # 补充：客户端菜单管理（若不存在）
            system_menu = session.query(Menu).filter_by(
                menu_code="system", app_type="platform", is_deleted=0
            ).first()
            client_menu_mgr = session.query(Menu).filter_by(
                menu_code="system:client-menu", app_type="platform", is_deleted=0
            ).first()
            if system_menu and not client_menu_mgr:
                m = Menu(
                    parent_id=system_menu.id, menu_name="客户端菜单",
                    menu_code="system:client-menu", menu_type=0,
                    path="/system/client-menu", component="/system/client-menu/index",
                    sort_order=25, app_type="platform",
                )
                session.add(m)
                session.flush()
                all_menus.append(m)
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
                print("[OK] 客户端菜单管理已补充")

            # 迁移：客户运营中心菜单精简（移除旧菜单，更新保留菜单）
            customer_menu = session.query(Menu).filter_by(
                menu_code="customer", app_type="platform", is_deleted=0
            ).first()
            if customer_menu:
                deprecated_codes = ["customer:new", "customer:follow-up", "customer:all"]
                for code in deprecated_codes:
                    old_menu = session.query(Menu).filter_by(
                        menu_code=code, app_type="platform", is_deleted=0
                    ).first()
                    if old_menu:
                        old_menu.is_deleted = 1
                        session.query(RoleMenu).filter_by(menu_id=old_menu.id).delete()
                        print(f"[OK] 已移除旧菜单: {old_menu.menu_name} ({code})")

                trial_menu = session.query(Menu).filter_by(
                    menu_code="customer:trial", app_type="platform", is_deleted=0
                ).first()
                if trial_menu and trial_menu.menu_name != "试用期客户":
                    trial_menu.menu_name = "试用期客户"
                    trial_menu.sort_order = 0
                    print("[OK] 已更新菜单: 免费体验客户 -> 试用期客户")

                paid_menu = session.query(Menu).filter_by(
                    menu_code="customer:paid", app_type="platform", is_deleted=0
                ).first()
                if paid_menu and paid_menu.sort_order != 10:
                    paid_menu.sort_order = 10

                churned_menu = session.query(Menu).filter_by(
                    menu_code="customer:churned", app_type="platform", is_deleted=0
                ).first()
                if churned_menu and churned_menu.sort_order != 20:
                    churned_menu.sort_order = 20

                open_reg_menu = session.query(Menu).filter_by(
                    menu_code="customer:open-register-policy",
                    app_type="platform", is_deleted=0
                ).first()
                if customer_menu and not open_reg_menu:
                    m = Menu(
                        parent_id=customer_menu.id, menu_name="自助注册策略",
                        menu_code="customer:open-register-policy", menu_type=0,
                        path="/customer/open-register-policy",
                        component="/customer/open-register-policy/index",
                        icon="Setting", sort_order=8, app_type="platform",
                    )
                    session.add(m)
                    session.flush()
                    if role_admin:
                        session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
                    print("[OK] 自助注册策略菜单已补充")

                session.flush()

            # 补充：基础数据 + 地区数据菜单（若不存在）
            basic_data_menu = session.query(Menu).filter_by(
                menu_code="basic_data", app_type="platform", is_deleted=0
            ).first()
            if not basic_data_menu:
                basic_data_menu = Menu(
                    parent_id=0, menu_name="基础数据",
                    menu_code="basic_data", menu_type=0,
                    path="/basic_data",
                    icon="AppstoreOutlined", sort_order=15, app_type="platform",
                )
                session.add(basic_data_menu)
                session.flush()
                all_menus.append(basic_data_menu)
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=basic_data_menu.id))
                print("[OK] 基础数据菜单已补充")

            region_menu = session.query(Menu).filter_by(
                menu_code="basic_data:region", app_type="platform", is_deleted=0
            ).first()
            if basic_data_menu and not region_menu:
                region_menu = Menu(
                    parent_id=basic_data_menu.id, menu_name="地区数据",
                    menu_code="basic_data:region", menu_type=0,
                    path="/basic_data/regional_data",
                    component="/basic_data/regional_data/index",
                    icon="EnvironmentOutlined", sort_order=0, app_type="platform",
                )
                session.add(region_menu)
                session.flush()
                all_menus.append(region_menu)
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=region_menu.id))
                print("[OK] 地区数据菜单已补充")

            brand_series_menu = session.query(Menu).filter_by(
                menu_code="basic_data:vehicle_brand_series",
                app_type="platform", is_deleted=0
            ).first()
            if basic_data_menu and not brand_series_menu:
                brand_series_menu = Menu(
                    parent_id=basic_data_menu.id, menu_name="品牌与车系",
                    menu_code="basic_data:vehicle_brand_series", menu_type=0,
                    path="/basic_data/brand_series",
                    component="/basic_data/brand_series/index",
                    icon="CarOutlined", sort_order=5, app_type="platform",
                )
                session.add(brand_series_menu)
                session.flush()
                all_menus.append(brand_series_menu)
                if role_admin:
                    session.add(
                        RoleMenu(role_id=role_admin.id, menu_id=brand_series_menu.id)
                    )
                print("[OK] 品牌与车系菜单已补充")

            dealer_menu = session.query(Menu).filter_by(
                menu_code="basic_data:dealer", app_type="platform", is_deleted=0
            ).first()
            if basic_data_menu and not dealer_menu:
                dealer_menu = Menu(
                    parent_id=basic_data_menu.id, menu_name="经销商门店",
                    menu_code="basic_data:dealer", menu_type=0,
                    path="/basic_data/dealer",
                    component="/basic_data/dealer/index",
                    icon="ShopOutlined", sort_order=10, app_type="platform",
                )
                session.add(dealer_menu)
                session.flush()
                all_menus.append(dealer_menu)
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=dealer_menu.id))
                print("[OK] 经销商门店菜单已补充")

            data_sync_root = session.query(Menu).filter_by(
                menu_code="data_sync", app_type="platform", is_deleted=0
            ).first()
            if not data_sync_root:
                data_sync_root = Menu(
                    parent_id=0, menu_name="数据同步",
                    menu_code="data_sync", menu_type=0,
                    path="/data_sync",
                    icon="DownloadOutlined", sort_order=17, app_type="platform",
                )
                session.add(data_sync_root)
                session.flush()
                all_menus.append(data_sync_root)
                if role_admin:
                    session.add(
                        RoleMenu(role_id=role_admin.id, menu_id=data_sync_root.id)
                    )
                print("[OK] 数据同步菜单已补充")

            autohome_menu = session.query(Menu).filter_by(
                menu_code="data_sync:autohome", app_type="platform", is_deleted=0
            ).first()
            if data_sync_root and not autohome_menu:
                autohome_menu = Menu(
                    parent_id=data_sync_root.id, menu_name="汽车之家同步",
                    menu_code="data_sync:autohome", menu_type=0,
                    path="/data_sync/autohome",
                    component="/data_sync/autohome/index",
                    icon="CarOutlined", sort_order=0, app_type="platform",
                )
                session.add(autohome_menu)
                session.flush()
                all_menus.append(autohome_menu)
                if role_admin:
                    session.add(
                        RoleMenu(role_id=role_admin.id, menu_id=autohome_menu.id)
                    )
                print("[OK] 汽车之家同步菜单已补充")

            dealer_sync_menu = session.query(Menu).filter_by(
                menu_code="data_sync:dealer", app_type="platform", is_deleted=0
            ).first()
            if data_sync_root and not dealer_sync_menu:
                dealer_sync_menu = Menu(
                    parent_id=data_sync_root.id, menu_name="经销商数据同步",
                    menu_code="data_sync:dealer", menu_type=0,
                    path="/data_sync/dealer",
                    component="/data_sync/dealer/index",
                    icon="ShopOutlined", sort_order=5, app_type="platform",
                )
                session.add(dealer_sync_menu)
                session.flush()
                all_menus.append(dealer_sync_menu)
                if role_admin:
                    session.add(
                        RoleMenu(role_id=role_admin.id, menu_id=dealer_sync_menu.id)
                    )
                print("[OK] 经销商数据同步菜单已补充")

            region_sync_menu = session.query(Menu).filter_by(
                menu_code="data_sync:region", app_type="platform", is_deleted=0
            ).first()
            if data_sync_root and not region_sync_menu:
                region_sync_menu = Menu(
                    parent_id=data_sync_root.id, menu_name="行政区域同步",
                    menu_code="data_sync:region", menu_type=0,
                    path="/data_sync/region",
                    component="/data_sync/region/index",
                    icon="EnvironmentOutlined", sort_order=3, app_type="platform",
                )
                session.add(region_sync_menu)
                session.flush()
                all_menus.append(region_sync_menu)
                if role_admin:
                    session.add(
                        RoleMenu(role_id=role_admin.id, menu_id=region_sync_menu.id)
                    )
                print("[OK] 行政区域同步菜单已补充")

        # ---- 4. 角色-菜单关联（super_admin 关联所有平台菜单）----
        existing_role_menu = session.query(RoleMenu).filter_by(
            role_id=role_admin.id
        ).first()
        if not existing_role_menu and all_menus:
            role_menus = [
                RoleMenu(role_id=role_admin.id, menu_id=m.id)
                for m in all_menus
            ]
            session.add_all(role_menus)
            print(f"[OK] 角色-菜单关联已创建（{len(role_menus)}条）")
        else:
            print("[SKIP] 角色-菜单关联已存在")

        # ---- 5. 产品版本 ----
        # lite 版本独立于阶梯：由承运商邀请激活专用，仅含运力管理 + 合作客户反向视角
        existing_version = session.query(ProductVersion).first()
        if not existing_version:
            versions = [
                ProductVersion(
                    version_code="lite", version_name="轻量版",
                    description="承运商邀请激活专用：仅运力中心 + 合作客户反向视角，可升级到标准版/专业版",
                    max_users=5, max_vehicles=20, price="免费",
                    sort_order=5, status=1,
                ),
                ProductVersion(
                    version_code="basic", version_name="基础版",
                    description="基础管理能力：智能工作台 + 企业管理（组织/员工/角色/数据字典/基础数据）+ 客商中心（客户/承运商管理）",
                    max_users=5, max_vehicles=20, price="免费",
                    sort_order=10, status=1,
                ),
                ProductVersion(
                    version_code="standard", version_name="标准版",
                    description="完整运输业务能力：basic + 运营调度 + 运力中心（自营/外协/社会三类）+ 计费中心 + 审批中心",
                    max_users=20, max_vehicles=100, price="2999/年",
                    sort_order=20, status=1,
                ),
                ProductVersion(
                    version_code="pro", version_name="专业版",
                    description="企业级管理 + 数据分析：standard + 财务结算（应收/应付三路径/对账中心）+ 数据洞察",
                    max_users=100, max_vehicles=500, price="9999/年",
                    sort_order=30, status=1,
                ),
                ProductVersion(
                    version_code="enterprise", version_name="旗舰版",
                    description="全功能 + AI 增值：pro + AI 助手 + 智能预测 + 利润分析 + 车辆维保 + 证照监控 + 审批流程配置 + 发票管理 + 成本规则/费用模板 + 上游供应商管理",
                    max_users=9999, max_vehicles=9999, price="面议",
                    sort_order=40, status=1,
                ),
                # v2.0 预留：生态版（货源/运力/服务三大厅，远期开启）
                # status=0 表示当前不对外销售；菜单 sys_menu 同样以 visible=0 预留
                ProductVersion(
                    version_code="ecosystem", version_name="生态版",
                    description="平台运营产品（远期）：enterprise + 生态平台（货源大厅/运力大厅/服务大厅）",
                    max_users=9999, max_vehicles=9999, price="面议",
                    sort_order=50, status=0,
                ),
            ]
            session.add_all(versions)
            print("[OK] 产品版本已创建")
        else:
            # 已存在版本时补 lite（幂等）
            lite = session.query(ProductVersion).filter_by(
                version_code="lite", is_deleted=0
            ).first()
            if not lite:
                session.add(ProductVersion(
                    version_code="lite", version_name="轻量版",
                    description="承运商邀请激活专用：仅运力中心 + 合作客户反向视角，可升级到标准版/专业版",
                    max_users=5, max_vehicles=20, price="免费",
                    sort_order=5, status=1,
                ))
                print("[OK] 已补全 lite 产品版本")
            else:
                print("[SKIP] 产品版本已存在")

        # ---- 6. 数据字典 ----
        existing_dict = session.query(Dict).first()
        if not existing_dict:
            # 车辆类型字典
            d1 = Dict(dict_code="vehicle_type", dict_name="车辆类型", sort_order=0, status=1)
            session.add(d1)
            session.flush()
            session.add_all([
                DictItem(dict_id=d1.id, dict_code="vehicle_type", item_name="重型货车", item_value="heavy_truck", sort_order=0),
                DictItem(dict_id=d1.id, dict_code="vehicle_type", item_name="中型货车", item_value="medium_truck", sort_order=10),
                DictItem(dict_id=d1.id, dict_code="vehicle_type", item_name="轻型货车", item_value="light_truck", sort_order=20),
                DictItem(dict_id=d1.id, dict_code="vehicle_type", item_name="微型货车", item_value="mini_truck", sort_order=30),
                DictItem(dict_id=d1.id, dict_code="vehicle_type", item_name="挂车", item_value="trailer", sort_order=40),
            ])

            # 驾照类型字典
            d2 = Dict(dict_code="license_type", dict_name="驾照类型", sort_order=10, status=1)
            session.add(d2)
            session.flush()
            session.add_all([
                DictItem(dict_id=d2.id, dict_code="license_type", item_name="A1", item_value="A1", sort_order=0),
                DictItem(dict_id=d2.id, dict_code="license_type", item_name="A2", item_value="A2", sort_order=10),
                DictItem(dict_id=d2.id, dict_code="license_type", item_name="B1", item_value="B1", sort_order=20),
                DictItem(dict_id=d2.id, dict_code="license_type", item_name="B2", item_value="B2", sort_order=30),
                DictItem(dict_id=d2.id, dict_code="license_type", item_name="C1", item_value="C1", sort_order=40),
            ])

            # 计划状态字典
            d3 = Dict(dict_code="order_status", dict_name="计划状态", sort_order=20, status=1)
            session.add(d3)
            session.flush()
            session.add_all([
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="待派车", item_value="0", sort_order=0),
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="已派车", item_value="1", sort_order=10),
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="运输中", item_value="2", sort_order=20),
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="已到达", item_value="3", sort_order=30),
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="已签收", item_value="4", sort_order=40),
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="已完成", item_value="5", sort_order=50),
                DictItem(dict_id=d3.id, dict_code="order_status", item_name="已取消", item_value="6", sort_order=60),
            ])

            # 性别字典
            d4 = Dict(dict_code="sex", dict_name="性别", sort_order=30, status=1)
            session.add(d4)
            session.flush()
            session.add_all([
                DictItem(dict_id=d4.id, dict_code="sex", item_name="男", item_value="男", sort_order=0),
                DictItem(dict_id=d4.id, dict_code="sex", item_name="女", item_value="女", sort_order=10),
            ])

            # 产品模块字典
            d5 = Dict(dict_code="product_module", dict_name="产品模块", sort_order=40, status=1)
            session.add(d5)
            session.flush()
            session.add_all([
                DictItem(dict_id=d5.id, dict_code="product_module", item_name="基础模块", item_value="base", sort_order=0),
                DictItem(dict_id=d5.id, dict_code="product_module", item_name="资源管理", item_value="resource", sort_order=10),
                DictItem(dict_id=d5.id, dict_code="product_module", item_name="业务模块", item_value="biz", sort_order=20),
                DictItem(dict_id=d5.id, dict_code="product_module", item_name="财务模块", item_value="finance", sort_order=30),
                DictItem(dict_id=d5.id, dict_code="product_module", item_name="数据分析", item_value="bi", sort_order=40),
            ])
            print("[OK] 数据字典已创建")
        else:
            print("[SKIP] 数据字典已存在")

            # 补充：产品模块字典（若不存在）
            existing_pm = session.query(Dict).filter_by(
                dict_code="product_module", is_deleted=0
            ).first()
            if not existing_pm:
                d5 = Dict(dict_code="product_module", dict_name="产品模块", sort_order=40, status=1)
                session.add(d5)
                session.flush()
                session.add_all([
                    DictItem(dict_id=d5.id, dict_code="product_module", item_name="基础模块", item_value="base", sort_order=0),
                    DictItem(dict_id=d5.id, dict_code="product_module", item_name="资源管理", item_value="resource", sort_order=10),
                    DictItem(dict_id=d5.id, dict_code="product_module", item_name="业务模块", item_value="biz", sort_order=20),
                    DictItem(dict_id=d5.id, dict_code="product_module", item_name="财务模块", item_value="finance", sort_order=30),
                    DictItem(dict_id=d5.id, dict_code="product_module", item_name="数据分析", item_value="bi", sort_order=40),
                ])
                print("[OK] 产品模块字典已补充")

        # ---- 补充：用户管理目录 + 司机列表子菜单 ----
        user_mgmt_menu = session.query(Menu).filter_by(
            menu_code="user_management", app_type="platform", is_deleted=0
        ).first()
        if not user_mgmt_menu:
            user_mgmt_menu = Menu(
                parent_id=0, menu_name="用户管理",
                menu_code="user_management", menu_type=0,
                path="/user_management",
                icon="TeamOutlined", sort_order=12, app_type="platform",
            )
            session.add(user_mgmt_menu)
            session.flush()
            all_menus.append(user_mgmt_menu)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=user_mgmt_menu.id))
            print("[OK] 用户管理菜单已补充")

        driver_list_menu = session.query(Menu).filter_by(
            menu_code="user_management:drivers", app_type="platform", is_deleted=0
        ).first()
        if user_mgmt_menu and not driver_list_menu:
            m = Menu(
                parent_id=user_mgmt_menu.id, menu_name="司机列表",
                menu_code="user_management:drivers", menu_type=0,
                path="/user_management/drivers",
                component="/user_management/drivers/index",
                icon="UserFilled", sort_order=10, app_type="platform",
            )
            session.add(m)
            session.flush()
            all_menus.append(m)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
            print("[OK] 司机列表菜单已补充")

        # ---- 补充：运力中心菜单（平台端） ----
        capacity_menu = session.query(Menu).filter_by(
            menu_code="platform_capacity", app_type="platform", is_deleted=0
        ).first()
        if not capacity_menu:
            capacity_menu = Menu(
                parent_id=user_mgmt_menu.id if user_mgmt_menu else 0,
                menu_name="平台运力",
                menu_code="platform_capacity", menu_type=0,
                path="/user_management/capacity",
                component="/capacity/index",
                icon="CarFilled", sort_order=20, app_type="platform",
            )
            session.add(capacity_menu)
            session.flush()
            all_menus.append(capacity_menu)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=capacity_menu.id))
            print("[OK] 平台运力菜单已补充")

        # ---- 补充：AI 数字员工 Console 菜单（一级 + 五子项） ----
        ai_root = session.query(Menu).filter_by(
            menu_code="ai", app_type="platform", is_deleted=0
        ).first()
        if not ai_root:
            ai_root = Menu(
                parent_id=0, menu_name="AI 数字员工",
                menu_code="ai", menu_type=0,
                path="/ai", icon="MagicStick",
                sort_order=18, app_type="platform",
            )
            session.add(ai_root)
            session.flush()
            all_menus.append(ai_root)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=ai_root.id))
            print("[OK] AI 数字员工 顶级菜单已补充")

        ai_children = [
            ("ai:employee", "数字员工", "/ai/employee", "/ai/employee/index", 0),
            ("ai:tool", "工具中心", "/ai/tool", "/ai/tool/index", 10),
            ("ai:prompt", "提示词模板", "/ai/prompt", "/ai/prompt/index", 20),
            ("ai:provider", "模型 Provider", "/ai/provider", "/ai/provider/index", 30),
            ("ai:observe", "调用观测", "/ai/observe", "/ai/observe/index", 40),
        ]
        for code, name, path, comp, order in ai_children:
            ex = session.query(Menu).filter_by(
                menu_code=code, app_type="platform", is_deleted=0
            ).first()
            if ex:
                continue
            m = Menu(
                parent_id=ai_root.id, menu_name=name, menu_code=code,
                menu_type=0, path=path, component=comp,
                sort_order=order, app_type="platform",
            )
            session.add(m)
            session.flush()
            all_menus.append(m)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
            print(f"[OK] AI 子菜单 {name} 已补充")

        # ---- 补充：运营推广 → Banner 管理菜单 ----
        promotion_root = session.query(Menu).filter_by(
            menu_code="promotion", app_type="platform", is_deleted=0
        ).first()
        if not promotion_root:
            promotion_root = Menu(
                parent_id=0, menu_name="运营推广",
                menu_code="promotion", menu_type=0,
                path="/promotion", icon="PictureFilled",
                sort_order=19, app_type="platform",
            )
            session.add(promotion_root)
            session.flush()
            all_menus.append(promotion_root)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=promotion_root.id))
            print("[OK] 运营推广 顶级菜单已补充")

        banner_menu = session.query(Menu).filter_by(
            menu_code="promotion:banner", app_type="platform", is_deleted=0
        ).first()
        if promotion_root and not banner_menu:
            m = Menu(
                parent_id=promotion_root.id, menu_name="Banner 管理",
                menu_code="promotion:banner", menu_type=0,
                path="/promotion/banner",
                component="/promotion/banner/index",
                icon="PictureFilled", sort_order=0, app_type="platform",
            )
            session.add(m)
            session.flush()
            all_menus.append(m)
            if role_admin:
                session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
            print("[OK] Banner 管理菜单已补充")

        # ---- 自助注册策略默认配置 ----
        _policy_defaults = [
            (
                KEY_OPEN_REGISTER_DEFAULT_VERSION_CODE,
                DEFAULT_VERSION_CODE,
                "官网自助注册默认开通的产品版本编码",
            ),
            (
                KEY_OPEN_REGISTER_TRIAL_DAYS,
                str(DEFAULT_TRIAL_DAYS),
                "官网自助注册试用天数，0 表示不限期",
            ),
        ]
        for _key, _val, _rmk in _policy_defaults:
            _ex = session.query(PlatformSetting).filter_by(
                config_key=_key, is_deleted=0
            ).first()
            if not _ex:
                session.add(
                    PlatformSetting(
                        config_key=_key, config_value=_val, remark=_rmk
                    )
                )
        print("[OK] 自助注册策略默认配置已就绪")

        session.commit()

    engine.dispose()


if __name__ == "__main__":
    seed_platform_data()
    print("\n种子数据初始化完成！")
