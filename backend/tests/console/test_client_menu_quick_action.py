"""运营后台端 · 客户端菜单「快捷操作」配置测试

对应代码：
  - backend/app/modules/console/services/product/client_menu_service.py
  - backend/app/modules/client/services/quick_action_service.py
  - backend/app/modules/client/api/workbench/quick_action.py

覆盖：
  1. 纯逻辑（无 DB）：
     - ClientMenuService._build_quick_action：开关/清洗/类型收敛
     - ClientMenuService._to_out：JSON -> 扁平字段展开
     - QuickActionService._split_link：link 解析为 type/path/query
  2. Service 集成（平台库外层事务回滚，不落库）：
     - 创建带快捷操作的 client 菜单 -> 列表回读扁平字段
     - 更新关闭快捷操作 -> quick_action 置空
     - QuickActionService.list_registry 下发目录并正确映射
  3. HTTP 鉴权门槛：未登录访问下发接口应被拦截
"""

from __future__ import annotations

import uuid

import pytest

from app.modules.console.models.system.menu import Menu
from app.modules.console.schemas.product.client_menu import (
    ClientMenuCreate,
    ClientMenuUpdate,
)
from app.modules.console.services.product.client_menu_service import (
    ClientMenuService,
)
from app.modules.client.services.quick_action_service import (
    QuickActionService,
    _split_link,
)


def _rand_authority() -> str:
    return f"test:quick:{uuid.uuid4().hex[:8]}"


# =====================================================================
# 1. 纯逻辑（无 DB）
# =====================================================================
class TestBuildQuickAction:
    def test_disabled_returns_none(self):
        assert (
            ClientMenuService._build_quick_action(
                False, "/uploads/quick_action/a.png", "x", "#fff", "/x", "g", 1, True
            )
            is None
        )
        assert (
            ClientMenuService._build_quick_action(
                None, None, None, None, None, None, None, None
            )
            is None
        )

    def test_enabled_builds_dict_and_cleans_blank(self):
        qa = ClientMenuService._build_quick_action(
            True, "  /uploads/quick_action/a.png ", "  ", "#69c0ff", "", "运营调度", None, None
        )
        assert qa == {
            "icon": "/uploads/quick_action/a.png",  # 已 strip
            "name": None,  # 空白清成 None
            "color": "#69c0ff",
            "link": None,  # 空字符串清成 None
            "group": "运营调度",
            "sort": 0,  # None -> 0
            "default": False,  # None -> False
        }

    def test_sort_and_default_coercion(self):
        qa = ClientMenuService._build_quick_action(
            True, None, "新建运单", None, "/operation/waybill?action=create", None, 30, True
        )
        assert qa["sort"] == 30
        assert qa["default"] is True
        assert qa["link"] == "/operation/waybill?action=create"


class TestToOutExpand:
    def _menu(self, quick_action) -> Menu:
        m = Menu(
            parent_id=0,
            menu_name="运单管理",
            menu_code="business:waybill:list",
            menu_type=0,
            path="/operation/waybill",
            sort_order=10,
            visible=1,
            app_type="client",
            feature_code="biz_waybill",
        )
        m.id = 123
        m.quick_action = quick_action
        return m

    def test_expand_none(self):
        out = ClientMenuService._to_out(self._menu(None))
        assert out.quickActionEnabled is False
        assert out.quickActionIcon is None
        assert out.quickActionDefault is False

    def test_expand_dict(self):
        out = ClientMenuService._to_out(
            self._menu(
                {
                    "icon": "/uploads/quick_action/a.png",
                    "name": "运单管理",
                    "color": "#5cdbd3",
                    "link": "/operation/waybill",
                    "group": "运营调度",
                    "sort": 30,
                    "default": True,
                }
            )
        )
        assert out.quickActionEnabled is True
        assert out.quickActionIcon == "/uploads/quick_action/a.png"
        assert out.quickActionName == "运单管理"
        assert out.quickActionColor == "#5cdbd3"
        assert out.quickActionLink == "/operation/waybill"
        assert out.quickActionGroup == "运营调度"
        assert out.quickActionSort == 30
        assert out.quickActionDefault is True


class TestSplitLink:
    def test_external(self):
        info = _split_link("https://example.com/x", "/fallback")
        assert info["type"] == "external"
        assert info["path"] == "https://example.com/x"
        assert info["query"] is None

    def test_route_with_query(self):
        info = _split_link("/operation/waybill?action=create&tab=all", None)
        assert info["type"] == "route"
        assert info["path"] == "/operation/waybill"
        assert info["query"] == {"action": "create", "tab": "all"}

    def test_route_without_query(self):
        info = _split_link("/partner/customer", None)
        assert info["type"] == "route"
        assert info["path"] == "/partner/customer"
        assert info["query"] is None

    def test_fallback_to_menu_path(self):
        info = _split_link(None, "/operation/task")
        assert info["type"] == "route"
        assert info["path"] == "/operation/task"

    def test_empty(self):
        info = _split_link(None, None)
        assert info["path"] == ""
        assert info["query"] is None


# =====================================================================
# 2. Service 集成（平台库事务回滚，不落库）
# =====================================================================
class TestClientMenuQuickActionService:
    async def test_create_then_readback_flattened(self, platform_db):
        authority = _rand_authority()
        await ClientMenuService.create_menu(
            platform_db,
            ClientMenuCreate(
                parentId=0,
                title="自动化-快捷操作菜单",
                path="/auto/qa",
                menuType=0,
                sortNumber=5,
                authority=authority,
                quickActionEnabled=True,
                quickActionIcon="/uploads/quick_action/auto.png",
                quickActionName="自动化入口",
                quickActionColor="#69c0ff",
                quickActionLink="/auto/qa?action=create",
                quickActionGroup="自动化组",
                quickActionSort=42,
                quickActionDefault=True,
            ),
        )

        rows = await ClientMenuService.list_menus(platform_db, authority=authority)
        assert len(rows) == 1
        row = rows[0]
        assert row.quickActionEnabled is True
        assert row.quickActionIcon == "/uploads/quick_action/auto.png"
        assert row.quickActionName == "自动化入口"
        assert row.quickActionLink == "/auto/qa?action=create"
        assert row.quickActionSort == 42
        assert row.quickActionDefault is True

    async def test_update_disable_clears_quick_action(self, platform_db):
        authority = _rand_authority()
        await ClientMenuService.create_menu(
            platform_db,
            ClientMenuCreate(
                parentId=0,
                title="自动化-待关闭",
                path="/auto/off",
                menuType=0,
                sortNumber=6,
                authority=authority,
                quickActionEnabled=True,
                quickActionIcon="/uploads/quick_action/off.png",
            ),
        )
        created = (await ClientMenuService.list_menus(platform_db, authority=authority))[0]
        assert created.quickActionEnabled is True

        await ClientMenuService.update_menu(
            platform_db,
            ClientMenuUpdate(menuId=created.menuId, quickActionEnabled=False),
        )
        after = (await ClientMenuService.list_menus(platform_db, authority=authority))[0]
        assert after.quickActionEnabled is False
        assert after.quickActionIcon is None

    async def test_registry_lists_and_maps(self, platform_db):
        authority = _rand_authority()
        await ClientMenuService.create_menu(
            platform_db,
            ClientMenuCreate(
                parentId=0,
                title="自动化-目录下发",
                path="/auto/reg",
                menuType=0,
                sortNumber=7,
                authority=authority,
                featureCode="biz_auto",
                quickActionEnabled=True,
                quickActionName="下发入口",
                quickActionColor="#b37feb",
                quickActionLink="/auto/reg?action=create",
                quickActionGroup="下发组",
                quickActionSort=88,
                quickActionDefault=True,
            ),
        )

        items = await QuickActionService.list_registry(platform_db)
        mine = next((x for x in items if x["key"] == authority), None)
        assert mine is not None, "新建的快捷操作应出现在目录中"
        assert mine["title"] == "下发入口"
        assert mine["color"] == "#b37feb"
        assert mine["type"] == "route"
        assert mine["path"] == "/auto/reg"
        assert mine["query"] == {"action": "create"}
        assert mine["permission"] == authority
        assert mine["feature"] == "biz_auto"
        assert mine["group"] == "下发组"
        assert mine["defaultVisible"] is True
        assert mine["sortOrder"] == 88

    async def test_disabled_menu_absent_from_registry(self, platform_db):
        authority = _rand_authority()
        await ClientMenuService.create_menu(
            platform_db,
            ClientMenuCreate(
                parentId=0,
                title="自动化-未开启",
                path="/auto/none",
                menuType=0,
                sortNumber=8,
                authority=authority,
                quickActionEnabled=False,
            ),
        )
        items = await QuickActionService.list_registry(platform_db)
        assert all(x["key"] != authority for x in items)


# =====================================================================
# 3. HTTP 鉴权门槛
# =====================================================================
class TestQuickActionAuthGuard:
    async def test_missing_token_rejected(self, client):
        resp = await client.get("/api/client/workbench/quick-action")
        assert resp.status_code in {400, 401, 403}
        assert resp.json().get("code") != 0
