"""账号与组织 · 员工管理（租户库，事务回滚不落库）集成测试

对应需求：doc/02.需求文档/02.企业端/01.账号与组织/**
对应代码：backend/app/modules/client/services/user/user_service.py
覆盖用例：TC-CLI-USER-001
"""

from __future__ import annotations

import uuid

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.user.user import BizUserCreate, BizUserUpdate
from app.modules.client.services.user.user_service import BizUserService
from tests.client.conftest import unique_phone


class TestBizUserCrud:
    async def test_create_get_update_delete(self, tenant_session):
        phone = unique_phone()
        user = await BizUserService.create_user(
            tenant_session,
            BizUserCreate(
                phone=phone,
                nickname=f"测试员工_{uuid.uuid4().hex[:6]}",
                status=1,
            ),
        )
        assert user.id is not None
        assert user.phone == phone

        detail = await BizUserService.get_user(tenant_session, user.id)
        assert detail["phone"] == phone

        updated = await BizUserService.update_user(
            tenant_session,
            user.id,
            BizUserUpdate(userId=user.id, nickname="更新昵称", status=0),
        )
        assert updated.nickname == "更新昵称"
        assert updated.status == 0

        await BizUserService.update_status(tenant_session, user.id, 1)
        again = await BizUserService.get_user(tenant_session, user.id)
        assert again["status"] == 1

        await BizUserService.delete_user(tenant_session, user.id)
        with pytest.raises(BizException):
            await BizUserService.get_user(tenant_session, user.id)

    async def test_duplicate_phone_rejected(self, tenant_session):
        phone = unique_phone()
        await BizUserService.create_user(
            tenant_session, BizUserCreate(phone=phone, nickname="A")
        )
        with pytest.raises(BizException):
            await BizUserService.create_user(
                tenant_session, BizUserCreate(phone=phone, nickname="B")
            )

    async def test_check_existence(self, tenant_session):
        phone = unique_phone()
        assert await BizUserService.check_existence(tenant_session, "phone", phone) is False
        user = await BizUserService.create_user(
            tenant_session, BizUserCreate(phone=phone, nickname="C")
        )
        assert await BizUserService.check_existence(tenant_session, "phone", phone) is True
        assert (
            await BizUserService.check_existence(
                tenant_session, "phone", phone, exclude_id=user.id
            )
            is False
        )
