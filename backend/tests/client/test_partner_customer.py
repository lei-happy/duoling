"""合作伙伴 · 客户管理（租户库，事务回滚不落库）集成测试

覆盖 CustomerService 核心链路：新增（自动编码）、查询、更新、软删除、
以及反向：同名去重、按 ID 查询不存在报错。

对应需求：doc/02.需求文档/02.企业端/09.合作伙伴/客户管理.md
对应接口：GET/POST/PUT/DELETE /api/client/partner/customer
对应代码：backend/app/modules/client/services/partner/customer_service.py
覆盖用例：TC-CLI-CUSTOMER-001 ~ TC-CLI-CUSTOMER-010
"""

from __future__ import annotations

import uuid

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.partner.customer import (
    CustomerCreate,
    CustomerUpdate,
)
from app.modules.client.services.partner.customer_service import CustomerService


def _unique_name(prefix="测试客户"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestCustomerCrud:
    async def test_create_auto_code_and_get(self, tenant_session):
        name = _unique_name()
        c = await CustomerService.create_customer(
            tenant_session, CustomerCreate(customerName=name, contactPhone="13800000000")
        )
        assert c.id is not None
        assert c.customer_code and c.customer_code.startswith("KH")
        assert c.status == 1  # 默认启用

        got = await CustomerService.get_customer(tenant_session, c.id)
        assert got.customer_name == name

    async def test_duplicate_name_rejected(self, tenant_session):
        name = _unique_name()
        await CustomerService.create_customer(
            tenant_session, CustomerCreate(customerName=name)
        )
        with pytest.raises(BizException):
            await CustomerService.create_customer(
                tenant_session, CustomerCreate(customerName=name)
            )

    async def test_custom_code_duplicate_rejected(self, tenant_session):
        code = f"KHTEST{uuid.uuid4().hex[:6].upper()}"
        await CustomerService.create_customer(
            tenant_session,
            CustomerCreate(customerName=_unique_name(), customerCode=code),
        )
        with pytest.raises(BizException):
            await CustomerService.create_customer(
                tenant_session,
                CustomerCreate(customerName=_unique_name(), customerCode=code),
            )

    async def test_update_customer(self, tenant_session):
        c = await CustomerService.create_customer(
            tenant_session, CustomerCreate(customerName=_unique_name())
        )
        updated = await CustomerService.update_customer(
            tenant_session, c.id, CustomerUpdate(contactPerson="张三", status=0)
        )
        assert updated.contact_person == "张三"
        assert updated.status == 0

    async def test_delete_then_get_raises(self, tenant_session):
        c = await CustomerService.create_customer(
            tenant_session, CustomerCreate(customerName=_unique_name())
        )
        await CustomerService.delete_customer(tenant_session, c.id)
        with pytest.raises(BizException):
            await CustomerService.get_customer(tenant_session, c.id)

    async def test_get_nonexistent_raises(self, tenant_session):
        with pytest.raises(BizException):
            await CustomerService.get_customer(tenant_session, 987_654_321)

    async def test_page_returns_created(self, tenant_session):
        name = _unique_name()
        await CustomerService.create_customer(
            tenant_session, CustomerCreate(customerName=name)
        )
        page = await CustomerService.page_customers(
            tenant_session, page=1, page_size=20, keyword=name
        )
        assert page["total"] >= 1
        assert any(item["customerName"] == name for item in page["list"])
