"""企业端 · 工作台版本升级说明（平台库，事务回滚不落库）测试

对应需求：doc/02.需求文档/01.运营后台/12.版本升级说明/01.产品版本升级说明.md
对应用例：doc/06.测试用例体系/02.企业端/10.工作台版本升级说明.md（TC-CLI-CHLOG-*）
对应代码：backend/app/modules/client/services/changelog_service.py
          backend/app/modules/client/api/workbench/changelog.py

- Service 层用例直连平台库 session（外层事务回滚，不落库），构造 sys_changelog
  记录后验证「已发布过滤 / 弹框未读 / 标记已读只弹一次 / 按用户隔离 / 幂等」。
- HTTP 鉴权门槛用例走 http_client（不触发 lifespan、不落库）。
"""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from sqlalchemy import func, select

from app.modules.client.services.changelog_service import ClientChangelogService
from app.modules.console.models.changelog.changelog import Changelog, ChangelogRead

TENANT_CODE = "1001"


def _rand_user_id() -> int:
    """生成一个几乎不会与现有已读记录冲突的测试 user_id。"""
    return 900_000_000 + int(uuid.uuid4().hex[:6], 16)


async def _new_changelog(session, *, status: int = 1, is_popup: int = 0) -> Changelog:
    """在回滚事务内插入一条更新记录并返回（含自增 id）。"""
    cl = Changelog(
        version=f"vt-{uuid.uuid4().hex[:8]}",
        title="自动化测试版本说明",
        content="# 标题\n- 内容",
        release_date=date(2026, 7, 14),
        sort_order=10,
        status=status,
        is_popup=is_popup,
    )
    session.add(cl)
    await session.flush()
    return cl


class TestClientChangelogService:
    async def test_list_published_filters_status(self, platform_session):
        """TC-CLI-CHLOG-001：历史列表仅返回已发布记录"""
        pub = await _new_changelog(platform_session, status=1)
        stopped = await _new_changelog(platform_session, status=0)

        items, total = await ClientChangelogService.list_published(
            platform_session, page=1, limit=100
        )
        ids = {c.id for c in items}
        assert pub.id in ids
        assert stopped.id not in ids
        assert total >= 1

    async def test_unread_popup_then_mark_read(self, platform_session):
        """TC-CLI-CHLOG-005：弹框未读 → 标记已读 → 不再弹（核心链路）"""
        user_id = _rand_user_id()
        popup = await _new_changelog(platform_session, status=1, is_popup=1)

        before = await ClientChangelogService.list_unread_popups(
            platform_session, user_id
        )
        assert popup.id in {c.id for c in before}

        added = await ClientChangelogService.mark_read(
            platform_session, [popup.id], user_id=user_id, tenant_code=TENANT_CODE
        )
        assert added == 1

        after = await ClientChangelogService.list_unread_popups(
            platform_session, user_id
        )
        assert popup.id not in {c.id for c in after}

    async def test_non_popup_excluded(self, platform_session):
        """TC-CLI-CHLOG-004：非弹框 / 未发布记录不进入弹框接口"""
        user_id = _rand_user_id()
        non_popup = await _new_changelog(platform_session, status=1, is_popup=0)
        stopped_popup = await _new_changelog(platform_session, status=0, is_popup=1)

        popups = await ClientChangelogService.list_unread_popups(
            platform_session, user_id
        )
        ids = {c.id for c in popups}
        assert non_popup.id not in ids
        assert stopped_popup.id not in ids

    async def test_read_isolated_per_user(self, platform_session):
        """TC-CLI-CHLOG-006：已读按用户维度隔离，不影响他人"""
        u1, u2 = _rand_user_id(), _rand_user_id()
        popup = await _new_changelog(platform_session, status=1, is_popup=1)

        await ClientChangelogService.mark_read(
            platform_session, [popup.id], user_id=u1, tenant_code=TENANT_CODE
        )

        u1_after = await ClientChangelogService.list_unread_popups(platform_session, u1)
        u2_after = await ClientChangelogService.list_unread_popups(platform_session, u2)
        assert popup.id not in {c.id for c in u1_after}
        assert popup.id in {c.id for c in u2_after}

    async def test_mark_read_idempotent(self, platform_session):
        """TC-CLI-CHLOG-007：重复标记已读幂等，唯一约束下仅一条"""
        user_id = _rand_user_id()
        popup = await _new_changelog(platform_session, status=1, is_popup=1)

        first = await ClientChangelogService.mark_read(
            platform_session, [popup.id], user_id=user_id
        )
        second = await ClientChangelogService.mark_read(
            platform_session, [popup.id], user_id=user_id
        )
        assert first == 1
        assert second == 0

        cnt = (
            await platform_session.execute(
                select(func.count()).select_from(ChangelogRead).where(
                    ChangelogRead.changelog_id == popup.id,
                    ChangelogRead.user_id == user_id,
                    ChangelogRead.is_deleted == 0,
                )
            )
        ).scalar()
        assert cnt == 1

    async def test_mark_read_ignores_invalid(self, platform_session):
        """TC-CLI-CHLOG-008/009：不存在的 id 与空数组被忽略，无副作用"""
        user_id = _rand_user_id()
        assert await ClientChangelogService.mark_read(
            platform_session, [99999999], user_id=user_id
        ) == 0
        assert await ClientChangelogService.mark_read(
            platform_session, [], user_id=user_id
        ) == 0


class TestClientChangelogAuthGuard:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/client/workbench/changelog",
            "/api/client/workbench/changelog/popup",
        ],
    )
    async def test_missing_token_rejected(self, http_client, path):
        """TC-CLI-CHLOG-010：未登录访问版本升级说明接口 → 被拦截"""
        resp = await http_client.get(path)
        assert resp.status_code in {400, 401, 403}
        assert resp.json().get("code") != 0
