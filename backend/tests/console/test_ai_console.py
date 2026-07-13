"""运营后台端 - AI 数字员工测试（employee / provider / prompt / tool）

覆盖用例：TC-CON-AIEMP-001~005、TC-CON-AIPROV-001、TC-CON-AIPROMPT-001、
          TC-CON-AITOOL-001~002
对应需求：doc/02.需求文档/01.运营后台/**（AI 数字员工平台配置）
对应后端：backend/app/modules/ai/api/console/{employee,provider,prompt,tool}.py

写操作仅落平台库 ai_* 表并由外层事务回滚，不落库。
"""

import uuid

import pytest


class TestAiEmployee:
    async def test_employee_page(self, auth_client):
        """TC-CON-AIEMP-001：数字员工分页 → code=0"""
        resp = await auth_client.get("/api/console/ai/employee", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"]

    async def test_create_get_delete_employee(self, auth_client):
        """TC-CON-AIEMP-002：新增数字员工 → 详情可查 → 删除（回滚不落库）"""
        code = f"test_emp_{uuid.uuid4().hex[:8]}"
        create = await auth_client.post(
            "/api/console/ai/employee",
            json={"code": code, "name": "自动化测试员工", "employeeType": "custom", "status": 1},
        )
        assert create.status_code == 200, create.text
        body = create.json()
        assert body["code"] == 0, body
        emp_id = body["data"]["id"]

        got = await auth_client.get(f"/api/console/ai/employee/{emp_id}")
        assert got.status_code == 200
        assert got.json()["code"] == 0
        assert got.json()["data"]["code"] == code

        deleted = await auth_client.delete(f"/api/console/ai/employee/{emp_id}")
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0

    async def test_create_employee_missing_field_422(self, auth_client):
        """TC-CON-AIEMP-003：缺失必填 code → HTTP 422"""
        resp = await auth_client.post("/api/console/ai/employee", json={"name": "缺编码"})
        assert resp.status_code == 422

    async def test_employee_requires_auth(self, client):
        """TC-CON-AIEMP-004：未认证访问数字员工列表 → HTTP 401"""
        resp = await client.get("/api/console/ai/employee")
        assert resp.status_code == 401

    async def test_get_nonexistent_employee(self, auth_client):
        """TC-CON-AIEMP-005：查询不存在的数字员工 → code!=0 或 404 语义"""
        resp = await auth_client.get("/api/console/ai/employee/99999999")
        assert resp.status_code == 200
        assert resp.json()["code"] != 0


class TestAiProviderPromptTool:
    async def test_provider_page(self, auth_client):
        """TC-CON-AIPROV-001：LLM Provider 分页 → code=0"""
        resp = await auth_client.get("/api/console/ai/provider", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_prompt_page(self, auth_client):
        """TC-CON-AIPROMPT-001：提示词模板分页 → code=0"""
        resp = await auth_client.get("/api/console/ai/prompt", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_tool_page(self, auth_client):
        """TC-CON-AITOOL-001：AI 工具分页 → code=0"""
        resp = await auth_client.get("/api/console/ai/tool", params={"page": 1, "limit": 20})
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_tool_categories(self, auth_client):
        """TC-CON-AITOOL-002：工具分类列表 → code=0，返回 list"""
        resp = await auth_client.get("/api/console/ai/tool/categories")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"]
