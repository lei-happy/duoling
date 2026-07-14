"""运营后台端 - 产品版本升级说明（更新记录）测试

对应需求：doc/02.需求文档/01.运营后台/12.版本升级说明/01.产品版本升级说明.md
对应用例：doc/06.测试用例体系/01.运营后台端/06.版本升级说明管理.md（TC-CON-CHLOG-*）
对应后端：backend/app/modules/console/api/changelog/changelog.py
          backend/app/modules/console/services/changelog/changelog_service.py

本次重点覆盖新增字段 is_popup（是否弹框）的读写链路。
所有写操作仅落平台库并由外层事务回滚，不落库。
"""

from __future__ import annotations

import uuid

import pytest


def _changelog_payload(**override) -> dict:
    """构造一条最小合法的更新记录入参（version 唯一，避免脏数据干扰断言）。"""
    data = {
        "version": f"vt-{uuid.uuid4().hex[:8]}",
        "title": "自动化测试更新记录",
        "content": "# 更新内容\n- 修复若干问题",
        "release_date": "2026-07-14",
        "sort_order": 10,
    }
    data.update(override)
    return data


class TestChangelogCrud:
    async def test_create_default_not_popup(self, auth_client):
        """TC-CON-CHLOG-001：新建更新记录，默认 is_popup=0、status=1"""
        resp = await auth_client.post(
            "/api/console/changelog", json=_changelog_payload()
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["is_popup"] == 0
        assert data["status"] == 1

    async def test_create_with_popup(self, auth_client):
        """TC-CON-CHLOG-002：新建时开启弹框提醒 → is_popup=1"""
        resp = await auth_client.post(
            "/api/console/changelog", json=_changelog_payload(is_popup=1)
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["data"]["is_popup"] == 1

    async def test_update_toggle_popup(self, auth_client):
        """TC-CON-CHLOG-003：修改切换弹框提醒开关"""
        created = await auth_client.post(
            "/api/console/changelog", json=_changelog_payload(is_popup=0)
        )
        cid = created.json()["data"]["id"]

        on = await auth_client.put(
            f"/api/console/changelog/{cid}", json={"is_popup": 1}
        )
        assert on.status_code == 200
        assert on.json()["data"]["is_popup"] == 1

        off = await auth_client.put(
            f"/api/console/changelog/{cid}", json={"is_popup": 0}
        )
        assert off.json()["data"]["is_popup"] == 0

    async def test_detail_contains_is_popup(self, auth_client):
        """TC-CON-CHLOG-004：详情返回包含 is_popup 字段"""
        created = await auth_client.post(
            "/api/console/changelog", json=_changelog_payload(is_popup=1)
        )
        cid = created.json()["data"]["id"]
        detail = await auth_client.get(f"/api/console/changelog/{cid}")
        assert detail.status_code == 200
        body = detail.json()
        assert body["code"] == 0
        assert body["data"]["is_popup"] == 1

    async def test_list_with_status_filter(self, auth_client):
        """TC-CON-CHLOG-005：分页列表结构 + 状态过滤 + 含 is_popup"""
        payload = _changelog_payload()
        await auth_client.post("/api/console/changelog", json=payload)

        resp = await auth_client.get(
            "/api/console/changelog", params={"page": 1, "limit": 20, "status": 1}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert {"list", "total", "page", "limit"}.issubset(data.keys())
        assert all(item["status"] == 1 for item in data["list"])
        assert all("is_popup" in item for item in data["list"])

    async def test_delete_changelog(self, auth_client):
        """TC-CON-CHLOG-007：软删除记录 → 详情不再可查"""
        created = await auth_client.post(
            "/api/console/changelog", json=_changelog_payload()
        )
        cid = created.json()["data"]["id"]

        deleted = await auth_client.delete(f"/api/console/changelog/{cid}")
        assert deleted.status_code == 200
        assert deleted.json()["code"] == 0

        detail = await auth_client.get(f"/api/console/changelog/{cid}")
        assert detail.json()["code"] != 0

    async def test_delete_not_exist(self, auth_client):
        """TC-CON-CHLOG-008：删除不存在记录 → 业务失败，不抛 500"""
        resp = await auth_client.delete("/api/console/changelog/99999999")
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    @pytest.mark.parametrize(
        "bad",
        [
            {"title": "缺版本号", "release_date": "2026-07-14"},
            {"version": "v1", "release_date": "2026-07-14"},
            {"version": "v1", "title": "缺发布日期"},
        ],
    )
    async def test_create_missing_field_422(self, auth_client, bad):
        """TC-CON-CHLOG-009：缺失必填字段 → HTTP 422"""
        resp = await auth_client.post("/api/console/changelog", json=bad)
        assert resp.status_code == 422

    async def test_requires_auth(self, client):
        """TC-CON-CHLOG-010：未认证访问 → HTTP 401"""
        resp = await client.get("/api/console/changelog")
        assert resp.status_code == 401
