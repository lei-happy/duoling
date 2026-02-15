"""
修复菜单数据：
1. 将页面菜单的 menu_type 从 1（按钮）修正为 0（菜单页面）
2. 补充 super_admin 角色与所有平台菜单的关联
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.modules.console.models.menu import Menu
from app.modules.console.models.role import Role
from app.modules.console.models.permission import RoleMenu


def fix_data():
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    with Session(engine) as session:
        # ---- 1. 修正 menu_type ----
        # 有 component 的菜单是页面，menu_type 应该是 0（菜单），不是 1（按钮）
        updated = session.execute(
            update(Menu)
            .where(
                Menu.component.isnot(None),
                Menu.component != "",
                Menu.menu_type == 1,
                Menu.is_deleted == 0,
            )
            .values(menu_type=0)
        )
        count = updated.rowcount
        if count > 0:
            print(f"[OK] 已修正 {count} 条菜单的 menu_type (1->0)")
        else:
            print("[SKIP] 无需修正 menu_type")

        # ---- 2. 补充角色-菜单关联 ----
        role_admin = session.query(Role).filter_by(role_code="super_admin").first()
        if not role_admin:
            print("[ERROR] 未找到 super_admin 角色，请先运行 seed_data.py")
            return

        # 查询所有平台菜单
        all_menus = session.query(Menu).filter_by(
            app_type="platform", is_deleted=0
        ).all()

        # 查询已关联的菜单 ID
        existing_ids = set(
            rm.menu_id for rm in
            session.query(RoleMenu).filter_by(
                role_id=role_admin.id, is_deleted=0
            ).all()
        )

        # 补充缺少的关联
        new_links = []
        for m in all_menus:
            if m.id not in existing_ids:
                new_links.append(RoleMenu(role_id=role_admin.id, menu_id=m.id))

        if new_links:
            session.add_all(new_links)
            print(f"[OK] 已补充 {len(new_links)} 条角色-菜单关联")
        else:
            print("[SKIP] 角色-菜单关联已完整")

        session.commit()

    engine.dispose()


if __name__ == "__main__":
    fix_data()
    print("\n数据修复完成！")
