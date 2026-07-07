"""运营后台端 - 系统管理测试（用户 / 角色 / 数据字典 / 地区）

覆盖用例：TC-CON-ROLE-001~005、TC-CON-DICT-001~004、
          TC-CON-USER-001~004、TC-CON-REGION-001~004
对应需求：项目文档/02.需求文档/01.运营后台/**（系统管理 / 基础数据）
对应后端：backend/app/modules/console/api/system/{user,role}.py
          backend/app/modules/console/api/dictionary/dict.py
          backend/app/modules/console/api/region/region.py

所有写操作仅落平台库并由外层事务回滚，不落库。
"""

import uuid

import pytest


# =====================================================================
# 角色管理
# =====================================================================
class TestRole:
    async def test_role_page(self, auth_client):
        """TC-CON-ROLE-001：分页查询角色 → code=0"""
        resp = await auth_client.get("/api/console/system/role/page", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_role_list(self, auth_client):
        """TC-CON-ROLE-002：查询角色列表 → code=0，返回数组"""
        resp = await auth_client.get("/api/console/system/role")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert isinstance(body["data"], list)

    async def test_create_then_delete_role(self, auth_client):
        """TC-CON-ROLE-003：新增角色 → 分页可查到 → 删除（回滚不落库）"""
        code = f"test_role_{uuid.uuid4().hex[:8]}"
        create = await auth_client.post(
            "/api/console/system/role",
            json={"roleCode": code, "roleName": "自动化测试角色", "status": 1},
        )
        assert create.status_code == 200, create.text
        assert create.json()["code"] == 0

        page = await auth_client.get(
            "/api/console/system/role/page", params={"roleCode": code, "page": 1, "limit": 10}
        )
        rows = page.json()["data"]["list"]
        assert any(r.get("roleCode") == code for r in rows), rows
        role_id = next(r for r in rows if r.get("roleCode") == code)["roleId"]

        deleted = await auth_client.delete(f"/api/console/system/role/{role_id}")
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0

    async def test_create_duplicate_role_code(self, auth_client):
        """TC-CON-ROLE-004：角色编码重复 → 业务失败 code!=0"""
        code = f"test_dup_role_{uuid.uuid4().hex[:8]}"
        payload = {"roleCode": code, "roleName": "重复角色", "status": 1}
        assert (await auth_client.post("/api/console/system/role", json=payload)).json()["code"] == 0
        second = await auth_client.post("/api/console/system/role", json=payload)
        assert second.json()["code"] != 0

    async def test_create_role_missing_field_422(self, auth_client):
        """TC-CON-ROLE-005：缺失必填 roleName → HTTP 422"""
        resp = await auth_client.post("/api/console/system/role", json={"roleCode": "x"})
        assert resp.status_code == 422


# =====================================================================
# 数据字典
# =====================================================================
class TestDict:
    async def test_dict_page(self, auth_client):
        """TC-CON-DICT-001：分页查询字典 → code=0"""
        resp = await auth_client.get("/api/console/system/dictionary/page", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_create_then_delete_dict(self, auth_client):
        """TC-CON-DICT-002：新增字典 → 可查到 → 删除（回滚不落库）"""
        code = f"test_dict_{uuid.uuid4().hex[:8]}"
        create = await auth_client.post(
            "/api/console/system/dictionary",
            json={"dictCode": code, "dictName": "自动化测试字典"},
        )
        assert create.status_code == 200
        assert create.json()["code"] == 0

        page = await auth_client.get(
            "/api/console/system/dictionary/page", params={"dictCode": code, "page": 1, "limit": 10}
        )
        rows = page.json()["data"]["list"]
        match = [r for r in rows if r.get("dictCode") == code]
        assert match, rows
        dict_id = match[0]["dictId"]

        deleted = await auth_client.delete(f"/api/console/system/dictionary/{dict_id}")
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0

    async def test_create_duplicate_dict_code(self, auth_client):
        """TC-CON-DICT-003：字典编码重复 → 业务失败 code!=0"""
        code = f"test_dup_dict_{uuid.uuid4().hex[:8]}"
        payload = {"dictCode": code, "dictName": "重复字典"}
        assert (await auth_client.post("/api/console/system/dictionary", json=payload)).json()["code"] == 0
        second = await auth_client.post("/api/console/system/dictionary", json=payload)
        assert second.json()["code"] != 0

    async def test_dict_requires_auth(self, client):
        """TC-CON-DICT-004：未认证访问字典分页 → HTTP 401"""
        resp = await client.get("/api/console/system/dictionary/page")
        assert resp.status_code == 401


# =====================================================================
# 用户管理
# =====================================================================
class TestUser:
    async def test_user_page(self, auth_client):
        """TC-CON-USER-001：分页查询用户 → code=0"""
        resp = await auth_client.get("/api/console/system/user/page", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_check_existence_admin_phone(self, auth_client):
        """TC-CON-USER-002：校验已存在手机号 → data=True"""
        resp = await auth_client.get(
            "/api/console/system/user/existence",
            params={"field": "phone", "value": "13800000000"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"] is True

    async def test_check_existence_unused_phone(self, auth_client):
        """TC-CON-USER-003：校验未占用手机号 → data=False"""
        resp = await auth_client.get(
            "/api/console/system/user/existence",
            params={"field": "phone", "value": "10000000009"},
        )
        assert resp.json()["data"] is False

    async def test_create_then_delete_user(self, auth_client):
        """TC-CON-USER-004：新增用户 → 分页可查 → 批量删除（回滚不落库）"""
        phone = "199" + uuid.uuid4().hex[:8]
        phone = phone[:11]
        create = await auth_client.post(
            "/api/console/system/user",
            json={"phone": phone, "password": "123456", "nickname": "自动化测试用户", "status": 1},
        )
        assert create.status_code == 200, create.text
        assert create.json()["code"] == 0

        page = await auth_client.get(
            "/api/console/system/user/page", params={"phone": phone, "page": 1, "limit": 10}
        )
        rows = page.json()["data"]["list"]
        match = [r for r in rows if r.get("phone") == phone]
        assert match, rows
        user_id = match[0]["userId"]

        deleted = await auth_client.request(
            "DELETE", "/api/console/system/user/batch", json=[user_id]
        )
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0


# =====================================================================
# 地区数据
# =====================================================================
class TestRegion:
    async def test_region_nav_tree(self, auth_client):
        """TC-CON-REGION-001：省+市两级导航树 → code=0"""
        resp = await auth_client.get("/api/console/basic-data/region/nav-tree")
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_region_tree_root(self, auth_client):
        """TC-CON-REGION-002：不传 pcode 拉省级根节点 → code=0，返回数组"""
        resp = await auth_client.get("/api/console/basic-data/region/tree")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert isinstance(body["data"], list)

    async def test_region_search(self, auth_client):
        """TC-CON-REGION-003：按名称搜索地区 → code=0"""
        resp = await auth_client.get(
            "/api/console/basic-data/region/search", params={"name": "北京"}
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_region_requires_auth(self, client):
        """TC-CON-REGION-004：未认证访问地区导航树 → HTTP 401"""
        resp = await client.get("/api/console/basic-data/region/nav-tree")
        assert resp.status_code == 401
