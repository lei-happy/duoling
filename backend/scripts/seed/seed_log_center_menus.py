"""
日志中心菜单种子数据

在 sys_menu 表中添加日志中心的目录和子菜单。
运行方式：python scripts/seed_log_center_menus.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.modules.console.models.system.menu import Menu
from app.modules.console.models.system.permission import RoleMenu
from app.modules.console.models.system.role import Role


def seed_log_center_menus():
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    with Session(engine) as session:
        existing = session.query(Menu).filter_by(
            menu_code="log-center", app_type="platform", is_deleted=0
        ).first()

        if existing:
            print("[SKIP] 日志中心菜单已存在")
            return

        log_center = Menu(
            parent_id=0,
            menu_name="日志中心",
            menu_code="log-center",
            menu_type=0,
            path="/log-center",
            icon="Notebook",
            sort_order=15,
            app_type="platform",
        )
        session.add(log_center)
        session.flush()
        print(f"[OK] 日志中心目录已创建 (id={log_center.id})")

        operation_log_menu = Menu(
            parent_id=log_center.id,
            menu_name="操作日志",
            menu_code="log-center:operation-log",
            menu_type=0,
            path="/log-center/operation-log",
            component="/log-center/operation-log/index",
            sort_order=0,
            app_type="platform",
        )
        session.add(operation_log_menu)
        session.flush()
        print(f"[OK] 操作日志菜单已创建 (id={operation_log_menu.id})")

        super_admin_role = session.query(Role).filter_by(
            role_code="super_admin", is_deleted=0
        ).first()
        if super_admin_role:
            session.add_all([
                RoleMenu(role_id=super_admin_role.id, menu_id=log_center.id),
                RoleMenu(role_id=super_admin_role.id, menu_id=operation_log_menu.id),
            ])
            print(f"[OK] 已关联超级管理员角色 (role_id={super_admin_role.id})")

        session.commit()
        print("[DONE] 日志中心菜单种子数据写入完成")


if __name__ == "__main__":
    seed_log_center_menus()
