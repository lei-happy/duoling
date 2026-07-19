"""企业端 · 意见反馈（平台库，事务回滚不落库）测试

对应需求：doc/02.需求文档/01.运营后台/13.用户之声/01.意见反馈.md
对应用例：doc/06.测试用例体系/02.企业端/11.意见反馈.md（TC-CLI-FB-*）
对应代码：backend/app/modules/client/services/feedback_service.py
          backend/app/modules/client/api/feedback.py
"""

from __future__ import annotations

import uuid

import pytest

from app.common.enums import FeedbackStatusEnum, UserTypeEnum
from app.modules.client.schemas.feedback import FeedbackCreateIn
from app.modules.client.services.feedback_service import ClientFeedbackService
from app.modules.console.models.common.feedback import Feedback

TENANT_CODE = "1001"
OTHER_TENANT = "9999"


def _rand_user_id() -> int:
    return 900_000_000 + int(uuid.uuid4().hex[:6], 16)


async def _create_row(
    session,
    *,
    user_id: int,
    tenant_code: str = TENANT_CODE,
    title: str | None = None,
) -> Feedback:
    row = Feedback(
        tenant_code=tenant_code,
        user_id=user_id,
        user_name=f"user-{user_id}",
        contact_phone="13800000000",
        title=title or f"反馈-{uuid.uuid4().hex[:6]}",
        content="自动化测试反馈内容",
        feedback_type=0,
        status=int(FeedbackStatusEnum.PENDING),
        images="[]",
    )
    session.add(row)
    await session.flush()
    return row


class TestClientFeedbackService:
    async def test_create_pending(self, platform_session):
        """TC-CLI-FB-001：提交成功，status=待处理"""
        user_id = _rand_user_id()
        item = await ClientFeedbackService.create(
            platform_session,
            FeedbackCreateIn(
                feedback_type=0,
                title="希望增加导出",
                content="详情说明",
                images=[],
                contact_phone="13800000001",
            ),
            user_id=user_id,
            tenant_code=TENANT_CODE,
        )
        assert item.id > 0
        assert item.status == int(FeedbackStatusEnum.PENDING)
        assert item.tenant_code == TENANT_CODE
        assert item.user_id == user_id
        assert item.title == "希望增加导出"

    async def test_create_reject_too_many_images(self, platform_session):
        """TC-CLI-FB-006：图片超过 5 张拒绝"""
        with pytest.raises(Exception):
            FeedbackCreateIn(
                feedback_type=0,
                title="标题",
                content="内容",
                images=[f"/uploads/feedback/{i}.png" for i in range(6)],
            )

    async def test_list_scoped_to_self_for_normal_user(self, platform_session):
        """TC-CLI-FB-003：普通用户列表仅本人"""
        a, b = _rand_user_id(), _rand_user_id()
        fa = await _create_row(platform_session, user_id=a)
        await _create_row(platform_session, user_id=b)

        items, _ = await ClientFeedbackService.list_feedbacks(
            platform_session,
            user_id=a,
            user_type=UserTypeEnum.TENANT_USER,
            tenant_code=TENANT_CODE,
            page=1,
            limit=100,
        )
        ids = {x.id for x in items}
        assert fa.id in ids
        assert all(x.user_id == a for x in items if x.id in ids)

    async def test_admin_sees_tenant_all(self, platform_session):
        """TC-CLI-FB-004：管理员可见本租户他人"""
        a, b = _rand_user_id(), _rand_user_id()
        fa = await _create_row(platform_session, user_id=a)
        fb = await _create_row(platform_session, user_id=b)
        other = await _create_row(
            platform_session, user_id=_rand_user_id(), tenant_code=OTHER_TENANT
        )

        items, _ = await ClientFeedbackService.list_feedbacks(
            platform_session,
            user_id=a,
            user_type=UserTypeEnum.TENANT_ADMIN,
            tenant_code=TENANT_CODE,
            page=1,
            limit=200,
        )
        ids = {x.id for x in items}
        assert fa.id in ids
        assert fb.id in ids
        assert other.id not in ids

    async def test_detail_cross_tenant_denied(self, platform_session):
        """TC-CLI-FB-005：跨租户详情越权失败"""
        from app.common.exceptions import BizException

        row = await _create_row(
            platform_session, user_id=_rand_user_id(), tenant_code=OTHER_TENANT
        )
        with pytest.raises(BizException, match="找不到这条反馈"):
            await ClientFeedbackService.get_detail(
                platform_session,
                row.id,
                user_id=_rand_user_id(),
                user_type=UserTypeEnum.TENANT_ADMIN,
                tenant_code=TENANT_CODE,
            )


class TestClientFeedbackAuthGuard:
    async def test_missing_token_rejected(self, http_client):
        """TC-CLI-FB-007：未登录拒绝"""
        resp = await http_client.get("/api/client/feedback")
        assert resp.status_code in {400, 401, 403}
        assert resp.json().get("code") != 0
