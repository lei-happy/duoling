"""账号与组织 · 角色管理（租户库，事务回滚不落库）集成测试

对应需求：项目文档/02.需求文档/02.企业端/01.账号与组织/**
对应代码：backend/app/modules/client/services/role/role_service.py
覆盖用例：TC-CLI-ROLE-001（CRUD 部分）
"""

from __future__ import annotations

import uuid

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.role.role import BizRoleCreate, BizRoleUpdate
from app.modules.client.services.role.role_service import BizRoleService
from tests.client.conftest import unique_code


class TestBizRoleCrud:
    async def test_create_update_page_delete(self, tenant_session):
        code = unique_code("ROLE")
        role = await BizRoleService.create_role(
            tenant_session,
            BizRoleCreate(roleCode=code, roleName=f"测试角色_{uuid.uuid4().hex[:4]}"),
        )
        assert role.id is not None
        assert role.role_code == code

        updated = await BizRoleService.update_role(
            tenant_session,
            role.id,
            BizRoleUpdate(roleId=role.id, roleName="新角色名"),
        )
        assert updated.role_name == "新角色名"

        page = await BizRoleService.page_roles(
            tenant_session, page=1, limit=20, role_code=code
        )
        assert page["count"] >= 1
        assert any(item["roleCode"] == code for item in page["list"])

        await BizRoleService.delete_role(tenant_session, role.id)
        page_after = await BizRoleService.page_roles(
            tenant_session, page=1, limit=20, role_code=code
        )
        assert not any(item["roleCode"] == code for item in page_after["list"])

    async def test_duplicate_role_code_rejected(self, tenant_session):
        code = unique_code("DUP")
        await BizRoleService.create_role(
            tenant_session,
            BizRoleCreate(roleCode=code, roleName="角色A"),
        )
        with pytest.raises(BizException):
            await BizRoleService.create_role(
                tenant_session,
                BizRoleCreate(roleCode=code, roleName="角色B"),
            )

    async def test_admin_role_cannot_delete(self, tenant_session):
        roles = await BizRoleService.list_roles(tenant_session)
        admin = next((r for r in roles if r.roleCode == "admin"), None)
        if admin is None:
            pytest.skip("租户库无 admin 种子角色")
        with pytest.raises(BizException):
            await BizRoleService.delete_role(tenant_session, admin.roleId)
