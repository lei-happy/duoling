"""AI 数字人 · 数字员工列表（平台库，事务回滚不落库）集成测试

对应需求：项目文档/02.需求文档/02.企业端/11.AI数字员工/**
对应代码：backend/app/modules/ai/services/employee_service.py
覆盖用例：TC-CLI-AI-030
"""

from __future__ import annotations

import uuid

import pytest

from app.modules.ai.services.employee_service import EmployeeService


class TestAiEmployeeList:
    async def test_list_visible_returns_enabled_only(self, platform_session):
        rows = await EmployeeService.list_visible_for_user(platform_session)
        assert rows, "平台库应存在 seed_ai_employees 预置员工"
        assert all(int(r.status) == 1 for r in rows)
        codes = {r.code for r in rows}
        assert "form_recorder_default" in codes or "data_analyst_default" in codes

    async def test_get_by_code(self, platform_session):
        rows = await EmployeeService.list_visible_for_user(platform_session)
        if not rows:
            pytest.skip("平台库无启用数字员工")
        emp = rows[0]
        found = await EmployeeService.get_by_code(platform_session, emp.code)
        assert found is not None
        assert found.id == emp.id

    async def test_list_enabled_tool_codes(self, platform_session):
        rows = await EmployeeService.list_visible_for_user(platform_session)
        if not rows:
            pytest.skip("平台库无启用数字员工")
        tools = await EmployeeService.list_enabled_tool_codes(
            platform_session, rows[0].id
        )
        assert isinstance(tools, list)
