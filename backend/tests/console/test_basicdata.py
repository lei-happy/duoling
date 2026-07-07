"""运营后台端 - 基础数据测试（品牌 / 车系 / 经销商 / 角色菜单）

覆盖用例：TC-CON-BASIC-001~006、TC-CON-ROLEMENU-001~002
对应需求：项目文档/02.需求文档/01.运营后台/**（基础数据 / 角色菜单）
对应后端：backend/app/modules/console/api/basicdata/*
          backend/app/modules/console/api/system/role_menu.py

写操作仅落平台库并由外层事务回滚，不落库。
"""

import uuid

import pytest


class TestVehicleBrand:
    async def test_brand_page(self, auth_client):
        """TC-CON-BASIC-001：品牌分页 → code=0，含 list/count"""
        resp = await auth_client.get(
            "/api/console/basic-data/vehicle-brand", params={"page": 1, "limit": 10}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"] and "count" in body["data"]

    async def test_create_then_delete_brand(self, auth_client):
        """TC-CON-BASIC-002：新增品牌 → 详情可查 → 删除（回滚不落库）"""
        name = f"测试品牌_{uuid.uuid4().hex[:6]}"
        create = await auth_client.post(
            "/api/console/basic-data/vehicle-brand",
            json={"brandNameCn": name, "brandCountry": "中国"},
        )
        assert create.status_code == 200, create.text
        body = create.json()
        assert body["code"] == 0, body
        brand_id = body["data"]["brandId"]

        got = await auth_client.get(f"/api/console/basic-data/vehicle-brand/{brand_id}")
        assert got.status_code == 200
        assert got.json()["code"] == 0
        assert got.json()["data"]["brandNameCn"] == name

        deleted = await auth_client.delete(f"/api/console/basic-data/vehicle-brand/{brand_id}")
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0

    async def test_brand_requires_auth(self, client):
        """TC-CON-BASIC-003：未认证访问品牌分页 → HTTP 401"""
        resp = await client.get("/api/console/basic-data/vehicle-brand")
        assert resp.status_code == 401


class TestVehicleSeries:
    async def test_series_page(self, auth_client):
        """TC-CON-BASIC-004：车系分页（需 brandId）→ code=0"""
        brands = await auth_client.get(
            "/api/console/basic-data/vehicle-brand", params={"page": 1, "limit": 1}
        )
        assert brands.json()["code"] == 0
        brand_list = brands.json()["data"]["list"]
        if not brand_list:
            pytest.skip("平台库无品牌数据，跳过车系分页测试")
        brand_id = brand_list[0]["brandId"]

        resp = await auth_client.get(
            "/api/console/basic-data/vehicle-series",
            params={"brandId": brand_id, "page": 1, "limit": 10},
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_create_series_under_brand(self, auth_client):
        """TC-CON-BASIC-005：创建品牌 → 新增车系 → 删除（回滚不落库）"""
        brand_name = f"车系测试品牌_{uuid.uuid4().hex[:6]}"
        brand_resp = await auth_client.post(
            "/api/console/basic-data/vehicle-brand",
            json={"brandNameCn": brand_name},
        )
        assert brand_resp.json()["code"] == 0, brand_resp.text
        brand_id = brand_resp.json()["data"]["brandId"]

        series_name = f"测试车系_{uuid.uuid4().hex[:6]}"
        create = await auth_client.post(
            "/api/console/basic-data/vehicle-series",
            json={"brandId": brand_id, "seriesName": series_name},
        )
        assert create.status_code == 200, create.text
        body = create.json()
        assert body["code"] == 0, body
        series_id = body["data"]["seriesId"]

        got = await auth_client.get(f"/api/console/basic-data/vehicle-series/{series_id}")
        assert got.json()["code"] == 0
        assert got.json()["data"]["seriesName"] == series_name

        await auth_client.delete(f"/api/console/basic-data/vehicle-series/{series_id}")
        await auth_client.delete(f"/api/console/basic-data/vehicle-brand/{brand_id}")


class TestDealer:
    async def test_dealer_page(self, auth_client):
        """TC-CON-BASIC-006：经销商分页 → code=0"""
        resp = await auth_client.get(
            "/api/console/basic-data/dealer", params={"page": 1, "limit": 10}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"]

    async def test_create_then_delete_dealer(self, auth_client):
        """TC-CON-BASIC-007：新增经销商 → 详情可查 → 删除（回滚不落库）"""
        name = f"测试经销商_{uuid.uuid4().hex[:6]}"
        create = await auth_client.post(
            "/api/console/basic-data/dealer",
            json={
                "dealerName": name,
                "dealerType": "4S店",
                "mainBrand": "测试品牌",
                "province": "北京市",
                "city": "北京市",
                "addressDetail": "自动化测试地址",
            },
        )
        assert create.status_code == 200, create.text
        body = create.json()
        assert body["code"] == 0, body
        dealer_id = body["data"]["dealerId"]

        got = await auth_client.get(f"/api/console/basic-data/dealer/{dealer_id}")
        assert got.json()["code"] == 0
        assert got.json()["data"]["dealerName"] == name

        deleted = await auth_client.delete(f"/api/console/basic-data/dealer/{dealer_id}")
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0


class TestRoleMenu:
    async def _get_super_admin_role_id(self, auth_client) -> int:
        page = await auth_client.get(
            "/api/console/system/role/page",
            params={"roleCode": "super_admin", "page": 1, "limit": 1},
        )
        rows = page.json()["data"]["list"]
        match = [r for r in rows if r.get("roleCode") == "super_admin"]
        if not match:
            pytest.skip("平台库无 super_admin 角色，跳过角色菜单测试")
        return match[0]["roleId"]

    async def test_get_role_menus(self, auth_client):
        """TC-CON-ROLEMENU-001：查询 super_admin 已分配菜单 → code=0，返回数组"""
        role_id = await self._get_super_admin_role_id(auth_client)
        resp = await auth_client.get(f"/api/console/system/role-menu/{role_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert isinstance(body["data"], list)

    async def test_update_role_menus_for_temp_role(self, auth_client):
        """TC-CON-ROLEMENU-002：临时角色分配菜单 → 可查到 → 清空（回滚不落库）"""
        super_admin_id = await self._get_super_admin_role_id(auth_client)
        admin_menus = (
            await auth_client.get(f"/api/console/system/role-menu/{super_admin_id}")
        ).json()["data"]
        sample_menu_ids = admin_menus[:2] if admin_menus else []

        code = f"test_role_menu_{uuid.uuid4().hex[:8]}"
        create = await auth_client.post(
            "/api/console/system/role",
            json={"roleCode": code, "roleName": "菜单分配测试角色", "status": 1},
        )
        assert create.json()["code"] == 0, create.text
        page = await auth_client.get(
            "/api/console/system/role/page", params={"roleCode": code, "page": 1, "limit": 1}
        )
        role_id = next(r for r in page.json()["data"]["list"] if r["roleCode"] == code)["roleId"]

        updated = await auth_client.put(
            f"/api/console/system/role-menu/{role_id}",
            json={"menuIds": sample_menu_ids},
        )
        assert updated.status_code == 200
        assert updated.json()["code"] == 0

        got = await auth_client.get(f"/api/console/system/role-menu/{role_id}")
        assert got.json()["code"] == 0
        assert got.json()["data"] == sample_menu_ids

        await auth_client.put(
            f"/api/console/system/role-menu/{role_id}", json={"menuIds": []}
        )
        await auth_client.delete(f"/api/console/system/role/{role_id}")
