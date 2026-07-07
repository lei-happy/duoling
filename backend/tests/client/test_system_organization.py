"""账号与组织 · 组织架构（租户库，事务回滚不落库）集成测试

对应需求：项目文档/02.需求文档/02.企业端/01.账号与组织/**
对应代码：backend/app/modules/client/services/organization/department_service.py
覆盖用例：TC-CLI-ORG-001
"""

from __future__ import annotations

import uuid

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.organization.department import (
    DepartmentCreate,
    DepartmentUpdate,
)
from app.modules.client.services.organization.department_service import DepartmentService


def _dept_name(prefix: str = "测试部门") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestDepartmentCrud:
    async def test_create_update_tree_delete(self, tenant_session):
        parent = await DepartmentService.create_department(
            tenant_session,
            DepartmentCreate(parentId=0, organizationName=_dept_name("父部门")),
        )
        child = await DepartmentService.create_department(
            tenant_session,
            DepartmentCreate(
                parentId=parent.id,
                organizationName=_dept_name("子部门"),
            ),
        )

        updated = await DepartmentService.update_department(
            tenant_session,
            child.id,
            DepartmentUpdate(
                organizationId=child.id,
                organizationName="子部门已更新",
                sortNumber=99,
            ),
        )
        assert updated.dept_name == "子部门已更新"
        assert updated.sort_order == 99

        tree = await DepartmentService.get_department_tree(tenant_session)
        parent_node = next(
            (n for n in tree if n["organizationId"] == parent.id), None
        )
        assert parent_node is not None
        assert any(
            c["organizationName"] == "子部门已更新"
            for c in (parent_node.get("children") or [])
        )

        await DepartmentService.delete_department(tenant_session, child.id)
        await DepartmentService.delete_department(tenant_session, parent.id)

        with pytest.raises(BizException):
            await DepartmentService.delete_department(tenant_session, parent.id)

    async def test_delete_parent_with_children_rejected(self, tenant_session):
        parent = await DepartmentService.create_department(
            tenant_session,
            DepartmentCreate(parentId=0, organizationName=_dept_name()),
        )
        await DepartmentService.create_department(
            tenant_session,
            DepartmentCreate(parentId=parent.id, organizationName=_dept_name("子")),
        )
        with pytest.raises(BizException):
            await DepartmentService.delete_department(tenant_session, parent.id)
