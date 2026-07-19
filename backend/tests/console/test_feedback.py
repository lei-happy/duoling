"""运营后台端 · 意见反馈处理（平台库，事务回滚不落库）测试

对应需求：doc/02.需求文档/01.运营后台/13.用户之声/01.意见反馈.md
对应用例：doc/06.测试用例体系/01.运营后台端/07.意见反馈处理.md（TC-CON-FB-*）
对应后端：backend/app/modules/console/api/feedback/
          backend/app/modules/console/services/feedback/
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from app.common.enums import FeedbackStatusEnum
from app.modules.client.services.feedback_service import ClientFeedbackService
from app.modules.console.models.common.feedback import Feedback
from app.modules.console.schemas.feedback.feedback import FeedbackHandleIn
from app.modules.console.services.feedback.feedback_service import FeedbackService

TENANT_CODE = "1001"


def _rand_user_id() -> int:
    return 900_000_000 + int(uuid.uuid4().hex[:6], 16)


async def _seed_feedback(
    session,
    *,
    title: str | None = None,
    status: int = int(FeedbackStatusEnum.PENDING),
    feedback_type: int = 0,
    tenant_code: str = TENANT_CODE,
    is_deleted: int = 0,
) -> Feedback:
    row = Feedback(
        tenant_code=tenant_code,
        user_id=_rand_user_id(),
        user_name="测试用户",
        contact_phone="13900000000",
        title=title or f"运营反馈-{uuid.uuid4().hex[:6]}",
        content="需要处理的反馈内容",
        feedback_type=feedback_type,
        status=status,
        images="[]",
        is_deleted=is_deleted,
    )
    session.add(row)
    await session.flush()
    return row


class TestConsoleFeedbackService:
    async def test_list_contains_submitter(self, platform_db):
        """TC-CON-FB-001：分页列表含提交人等信息"""
        row = await _seed_feedback(platform_db)
        items, total = await FeedbackService.list_feedbacks(
            platform_db, page=1, limit=50
        )
        assert total >= 1
        hit = next((x for x in items if x.id == row.id), None)
        assert hit is not None
        assert hit.user_name == "测试用户"
        assert hit.tenant_code == TENANT_CODE
        assert hit.title == row.title

    async def test_filter_by_status_type_keyword(self, platform_db):
        """TC-CON-FB-002：按状态/类型/关键词筛选"""
        unique = uuid.uuid4().hex[:8]
        row = await _seed_feedback(
            platform_db,
            title=f"关键词{unique}标题",
            status=int(FeedbackStatusEnum.PROCESSING),
            feedback_type=1,
        )
        items, _ = await FeedbackService.list_feedbacks(
            platform_db,
            page=1,
            limit=50,
            status=int(FeedbackStatusEnum.PROCESSING),
            feedback_type=1,
            keyword=unique,
        )
        ids = {x.id for x in items}
        assert row.id in ids

    async def test_handle_with_reply(self, platform_db):
        """TC-CON-FB-003：改状态+回复，写 handler/replied_at"""
        row = await _seed_feedback(platform_db)
        out = await FeedbackService.handle_feedback(
            platform_db,
            row.id,
            FeedbackHandleIn(status=int(FeedbackStatusEnum.RESOLVED), reply="已安排优化"),
            handler_id=1,
            handler_name="平台管理员",
        )
        assert out.status == int(FeedbackStatusEnum.RESOLVED)
        assert out.reply == "已安排优化"
        assert out.handler_id == 1
        assert out.handler_name == "平台管理员"
        assert out.replied_at is not None

    async def test_handle_status_only_keeps_replied_at_empty(self, platform_db):
        """TC-CON-FB-004：仅改状态不回复，replied_at 保持为空"""
        row = await _seed_feedback(platform_db)
        out = await FeedbackService.handle_feedback(
            platform_db,
            row.id,
            FeedbackHandleIn(status=int(FeedbackStatusEnum.PROCESSING), reply=None),
            handler_id=1,
            handler_name="平台管理员",
        )
        assert out.status == int(FeedbackStatusEnum.PROCESSING)
        assert out.replied_at is None

    async def test_client_sees_console_reply(self, platform_db):
        """TC-CON-FB-005：租户端详情可见最新 reply/status"""
        from app.common.enums import UserTypeEnum

        row = await _seed_feedback(platform_db)
        await FeedbackService.handle_feedback(
            platform_db,
            row.id,
            FeedbackHandleIn(status=int(FeedbackStatusEnum.RESOLVED), reply="跨端可见回复"),
            handler_id=1,
            handler_name="运营",
        )
        detail = await ClientFeedbackService.get_detail(
            platform_db,
            row.id,
            user_id=row.user_id,
            user_type=UserTypeEnum.TENANT_USER,
            tenant_code=TENANT_CODE,
        )
        assert detail.status == int(FeedbackStatusEnum.RESOLVED)
        assert detail.reply == "跨端可见回复"
        assert detail.replied_at is not None

    async def test_soft_deleted_hidden(self, platform_db):
        """TC-CON-FB-006：软删记录不出现"""
        row = await _seed_feedback(platform_db, is_deleted=1)
        items, _ = await FeedbackService.list_feedbacks(
            platform_db, page=1, limit=200
        )
        assert row.id not in {x.id for x in items}


class TestConsoleFeedbackApi:
    async def test_list_api(self, auth_client, platform_db):
        """HTTP：列表接口可用"""
        await _seed_feedback(platform_db, title=f"api-{uuid.uuid4().hex[:6]}")
        resp = await auth_client.get("/api/console/feedback", params={"page": 1, "limit": 20})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"]

    async def test_handle_api(self, auth_client, platform_db):
        """HTTP：处理接口写入回复"""
        row = await _seed_feedback(platform_db)
        resp = await auth_client.put(
            f"/api/console/feedback/{row.id}/handle",
            json={"status": 2, "reply": f"HTTP回复-{datetime.now().timestamp()}"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["status"] == 2
        assert body["data"]["reply"]
        assert body["message"] == "已更新处理结果"
