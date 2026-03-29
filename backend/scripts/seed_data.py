"""
初始种子数据
创建超级管理员、默认角色、基础菜单、角色-菜单关联、产品版本等初始数据
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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


def seed_platform_data():
    """写入平台种子数据"""
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    with Session(engine) as session:
        # ---- 1. 超级管理员 ----
        existing_admin = session.query(User).filter_by(username="admin").first()
        role_admin = session.query(Role).filter_by(role_code="super_admin").first()

        if not existing_admin:
            admin = User(
                username="admin",
                password=hash_password("admin123"),
                real_name="超级管理员",
                phone="13800000000",
                user_type=0,  # 平台管理员
                status=1,
            )
            session.add(admin)
            session.flush()
            print("[OK] 超级管理员已创建 (admin / admin123)")

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
            system_menu = next(m for m in menus if m.menu_code == "system")
            product_menu = next(m for m in menus if m.menu_code == "product")

            sub_menus = [
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

            # 补充：短信验证码（若不存在）
            sms_code_menu = session.query(Menu).filter_by(
                menu_code="system:sms-code", app_type="platform", is_deleted=0
            ).first()
            if system_menu and not sms_code_menu:
                m = Menu(
                    parent_id=system_menu.id, menu_name="短信验证码",
                    menu_code="system:sms-code", menu_type=0,
                    path="/system/sms-code", component="/system/sms-code/index",
                    sort_order=27, app_type="platform",
                )
                session.add(m)
                session.flush()
                all_menus.append(m)
                if role_admin:
                    session.add(RoleMenu(role_id=role_admin.id, menu_id=m.id))
                print("[OK] 短信验证码菜单已补充")

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

                session.flush()

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
        existing_version = session.query(ProductVersion).first()
        if not existing_version:
            versions = [
                ProductVersion(
                    version_code="basic", version_name="基础版",
                    description="适合小型车队，包含基础车辆和驾驶员管理功能",
                    max_users=5, max_vehicles=20, price="免费",
                    sort_order=0, status=1,
                ),
                ProductVersion(
                    version_code="standard", version_name="标准版",
                    description="适合中型车队，包含运单管理、路线管理等功能",
                    max_users=20, max_vehicles=100, price="2999/年",
                    sort_order=10, status=1,
                ),
                ProductVersion(
                    version_code="pro", version_name="专业版",
                    description="适合大型车队，包含数据分析、结算管理等高级功能",
                    max_users=100, max_vehicles=500, price="9999/年",
                    sort_order=20, status=1,
                ),
                ProductVersion(
                    version_code="enterprise", version_name="企业版",
                    description="定制化解决方案，不限用户和车辆数，专属技术支持",
                    max_users=9999, max_vehicles=9999, price="面议",
                    sort_order=30, status=1,
                ),
            ]
            session.add_all(versions)
            print("[OK] 产品版本已创建")
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

            # 运单状态字典
            d3 = Dict(dict_code="order_status", dict_name="运单状态", sort_order=20, status=1)
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

        session.commit()

    engine.dispose()


if __name__ == "__main__":
    seed_platform_data()
    print("\n种子数据初始化完成！")
