"""运营后台端 - 租户管理与产品版本测试

覆盖用例：TC-CON-TENANT-001 ~ TC-CON-TENANT-006、TC-CON-PRODUCT-001 ~ 006
对应需求：项目文档/02.需求文档/01.运营后台/**（租户管理 / 产品版本授权）
对应后端：backend/app/modules/console/api/tenant/tenant.py
          backend/app/modules/console/api/product/product_version.py

说明：
- 租户「创建」会调用 db_manager.create_tenant_database 建真实租户库（不可事务回滚），
  故本套件不通过 HTTP 创建租户，仅覆盖分页/统计/详情等读接口与鉴权。
- 产品版本 CRUD 仅写平台库 sys_product_version，可被外层事务安全回滚。
"""

import uuid


class TestTenantRead:
    async def test_tenant_page(self, auth_client):
        """TC-CON-TENANT-001：分页查询租户列表 → code=0，含 list/total"""
        resp = await auth_client.get("/api/console/tenant/page", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        # 租户分页返回结构为 {"list": [...], "count": N}
        assert "list" in data and "count" in data

    async def test_tenant_stats(self, auth_client):
        """TC-CON-TENANT-002：各生命周期阶段客户数量统计 → code=0"""
        resp = await auth_client.get("/api/console/tenant/stats")
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_tenant_page_requires_auth(self, client):
        """TC-CON-TENANT-003：未认证访问租户分页 → HTTP 401"""
        resp = await client.get("/api/console/tenant/page")
        assert resp.status_code == 401

    async def test_get_nonexistent_tenant(self, auth_client):
        """TC-CON-TENANT-004：查询不存在的租户 → code!=0（业务失败）"""
        resp = await auth_client.get("/api/console/tenant/99999999")
        assert resp.status_code == 200
        assert resp.json()["code"] != 0


class TestProductVersionCrud:
    async def test_list_versions(self, auth_client):
        """TC-CON-PRODUCT-001：产品版本分页列表 → code=0"""
        resp = await auth_client.get("/api/console/product-version", params={"page": 1, "page_size": 20})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"]

    async def test_create_then_get_product_version(self, auth_client):
        """TC-CON-PRODUCT-002：新增版本应返回 code=0 与 id（BUG-CON-001 已修复）"""
        code = f"test_ver_{uuid.uuid4().hex[:8]}"
        create = await auth_client.post(
            "/api/console/product-version",
            json={
                "version_code": code,
                "version_name": "自动化测试版本",
                "sort_order": 999,
            },
        )
        assert create.status_code == 200, create.text
        body = create.json()
        assert body["code"] == 0, body
        version_id = body["data"]["id"]
        assert body["data"].get("createdAt") or body["data"].get("created_at")

        got = await auth_client.get(f"/api/console/product-version/{version_id}")
        assert got.status_code == 200
        assert got.json()["code"] == 0

    async def test_update_product_version(self, auth_client):
        """TC-CON-PRODUCT-003：创建后更新版本名称 → code=0，含 updatedAt"""
        code = f"test_ver_{uuid.uuid4().hex[:8]}"
        create = await auth_client.post(
            "/api/console/product-version",
            json={"version_code": code, "version_name": "更新前"},
        )
        assert create.status_code == 200, create.text
        version_id = create.json()["data"]["id"]

        updated = await auth_client.put(
            f"/api/console/product-version/{version_id}",
            json={"versionName": "更新后"},
        )
        assert updated.status_code == 200, updated.text
        body = updated.json()
        assert body["code"] == 0, body
        assert body["data"]["versionName"] == "更新后"
        assert body["data"].get("updatedAt") or body["data"].get("updated_at")

    async def test_get_nonexistent_version(self, auth_client):
        """TC-CON-PRODUCT-004：查询不存在的版本 → code!=0"""
        resp = await auth_client.get("/api/console/product-version/99999999")
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_create_missing_field_422(self, auth_client):
        """TC-CON-PRODUCT-005：缺失必填 version_code → HTTP 422"""
        resp = await auth_client.post(
            "/api/console/product-version",
            json={"version_name": "缺编码"},
        )
        assert resp.status_code == 422

    async def test_list_versions_requires_auth(self, client):
        """TC-CON-PRODUCT-006：未认证访问版本列表 → HTTP 401"""
        resp = await client.get("/api/console/product-version")
        assert resp.status_code == 401
