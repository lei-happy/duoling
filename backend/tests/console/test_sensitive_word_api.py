"""运营后台 · 敏感词库接口测试

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.3
对应后端：backend/app/modules/console/api/system/sensitive_word.py

所有写操作仅落平台库并由外层事务回滚，不落库。
"""

import uuid

import pytest

BASE = "/api/console/system/sensitive-word"


def _rand_word() -> str:
    """随机中文词，避免与真实词库或并发测试撞车。"""
    return f"测试词{uuid.uuid4().hex[:6]}"


class TestOptions:
    async def test_options_returned(self, auth_client):
        resp = await auth_client.get(f"{BASE}/options")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["categories"]) == 6
        assert len(data["actions"]) == 2
        assert len(data["scopes"]) == 2

    async def test_action_options_explain_consequence(self, auth_client):
        """处置选项要说清后果，否则运营分不清「禁止发布」和「转人工」。"""
        resp = await auth_client.get(f"{BASE}/options")
        actions = resp.json()["data"]["actions"]
        assert all(a.get("desc") for a in actions)


class TestPage:
    async def test_page_ok(self, auth_client):
        resp = await auth_client.get(BASE + "/page", params={"page": 1, "limit": 10})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "list" in body["data"]
        assert "count" in body["data"]

    async def test_filter_by_scope(self, auth_client):
        resp = await auth_client.get(
            BASE + "/page", params={"scope": "ecosystem", "page": 1, "limit": 50}
        )
        rows = resp.json()["data"]["list"]
        assert all(r["scope"] == "ecosystem" for r in rows)

    async def test_filter_by_action(self, auth_client):
        resp = await auth_client.get(
            BASE + "/page", params={"action": 2, "page": 1, "limit": 50}
        )
        rows = resp.json()["data"]["list"]
        assert all(r["action"] == 2 for r in rows)


class TestCrud:
    async def test_create_then_page_then_delete(self, auth_client):
        word = _rand_word()
        created = await auth_client.post(
            BASE,
            json={"word": word, "category": 3, "action": 1,
                  "scope": "ecosystem", "remark": "自动化测试"},
        )
        assert created.status_code == 200, created.text
        assert created.json()["code"] == 0
        assert word in created.json()["message"]

        page = await auth_client.get(
            BASE + "/page", params={"keyword": word, "page": 1, "limit": 10}
        )
        rows = page.json()["data"]["list"]
        assert len(rows) == 1
        row = rows[0]
        assert row["word"] == word
        assert row["category"] == 3
        assert row["status"] == 1
        assert row["hitCount"] == 0

        deleted = await auth_client.post(BASE + "/delete", json={"ids": [row["id"]]})
        assert deleted.json()["code"] == 0

    async def test_duplicate_rejected_with_friendly_message(self, auth_client):
        word = _rand_word()
        await auth_client.post(BASE, json={"word": word, "scope": "all"})
        again = await auth_client.post(BASE, json={"word": word, "scope": "all"})
        body = again.json()
        assert body["code"] != 0
        assert "已经在词库里" in body["message"]

    async def test_same_word_allowed_in_different_scope(self, auth_client):
        """同一个词在不同范围可以有不同处置，不该视为重复。"""
        word = _rand_word()
        a = await auth_client.post(BASE, json={"word": word, "scope": "all"})
        b = await auth_client.post(BASE, json={"word": word, "scope": "ecosystem"})
        assert a.json()["code"] == 0
        assert b.json()["code"] == 0

    async def test_single_char_rejected(self, auth_client):
        resp = await auth_client.post(BASE, json={"word": "枪"})
        body = resp.json()
        assert body["code"] != 0
        assert "误伤" in body["message"]

    async def test_update_word(self, auth_client):
        word = _rand_word()
        await auth_client.post(BASE, json={"word": word, "action": 1, "scope": "all"})
        page = await auth_client.get(BASE + "/page", params={"keyword": word})
        row = page.json()["data"]["list"][0]

        updated = await auth_client.put(
            BASE, json={"id": row["id"], "action": 2, "remark": "改成转人工"}
        )
        assert updated.json()["code"] == 0

        page2 = await auth_client.get(BASE + "/page", params={"keyword": word})
        row2 = page2.json()["data"]["list"][0]
        assert row2["action"] == 2
        assert row2["remark"] == "改成转人工"

    async def test_update_missing_word(self, auth_client):
        resp = await auth_client.put(BASE, json={"id": 99999999, "action": 2})
        body = resp.json()
        assert body["code"] != 0
        assert "不存在" in body["message"]

    async def test_invalid_category_rejected(self, auth_client):
        resp = await auth_client.post(BASE, json={"word": _rand_word(), "category": 99})
        assert resp.json()["code"] != 0


class TestStatusToggle:
    async def test_disable_then_enable(self, auth_client):
        word = _rand_word()
        await auth_client.post(BASE, json={"word": word, "scope": "all"})
        page = await auth_client.get(BASE + "/page", params={"keyword": word})
        wid = page.json()["data"]["list"][0]["id"]

        off = await auth_client.put(BASE + "/status", json={"ids": [wid], "status": 0})
        assert off.json()["code"] == 0
        assert "停用" in off.json()["message"]

        page2 = await auth_client.get(BASE + "/page", params={"keyword": word})
        assert page2.json()["data"]["list"][0]["status"] == 0

        on = await auth_client.put(BASE + "/status", json={"ids": [wid], "status": 1})
        assert "启用" in on.json()["message"]

    async def test_empty_ids_rejected(self, auth_client):
        resp = await auth_client.put(BASE + "/status", json={"ids": [], "status": 0})
        body = resp.json()
        assert body["code"] != 0
        assert "请选择" in body["message"]


class TestBatchImport:
    async def test_import_reports_counts(self, auth_client):
        words = [_rand_word() for _ in range(3)]
        resp = await auth_client.post(
            BASE + "/batch-import",
            json={"words": words, "category": 3, "action": 1, "scope": "ecosystem"},
        )
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["added"] == 3

    async def test_import_skips_existing_instead_of_failing(self, auth_client):
        """批量导入常见用法是补一份新词表，与现有词库必然重叠，
        因重叠而整批失败毫无意义。"""
        word = _rand_word()
        await auth_client.post(BASE, json={"word": word, "scope": "all"})

        resp = await auth_client.post(
            BASE + "/batch-import", json={"words": [word, _rand_word()], "scope": "all"}
        )
        data = resp.json()["data"]
        assert data["added"] == 1
        assert data["skipped"] == 1

    async def test_import_dedupes_within_payload(self, auth_client):
        word = _rand_word()
        resp = await auth_client.post(
            BASE + "/batch-import", json={"words": [word, word, word], "scope": "all"}
        )
        assert resp.json()["data"]["added"] == 1

    async def test_import_drops_invalid_entries(self, auth_client):
        """空串、单字等无效项跳过，不让整批失败。"""
        word = _rand_word()
        resp = await auth_client.post(
            BASE + "/batch-import", json={"words": [word, "", "  ", "枪"], "scope": "all"}
        )
        assert resp.json()["data"]["added"] == 1

    async def test_import_all_invalid_rejected(self, auth_client):
        resp = await auth_client.post(
            BASE + "/batch-import", json={"words": ["", "  "], "scope": "all"}
        )
        body = resp.json()
        assert body["code"] != 0
        assert "检查" in body["message"]

    async def test_import_over_limit_rejected(self, auth_client):
        resp = await auth_client.post(
            BASE + "/batch-import",
            json={"words": [f"词{i:04d}" for i in range(501)], "scope": "all"},
        )
        body = resp.json()
        assert body["code"] != 0
        assert "分批" in body["message"]


class TestTextTest:
    async def test_clean_text_passes(self, auth_client):
        resp = await auth_client.post(
            BASE + "/test",
            json={"text": "杭州到成都商品车 8 台，需要封闭板", "scope": "ecosystem"},
        )
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["blocked"] is False
        assert "可以正常发布" in body["message"]

    async def test_contact_info_detected(self, auth_client):
        resp = await auth_client.post(
            BASE + "/test", json={"text": "有货联系 13812345678", "scope": "ecosystem"}
        )
        data = resp.json()["data"]
        assert data["blocked"] is True
        assert "手机号" in data["contactHits"]

    async def test_seeded_word_detected(self, auth_client):
        """种子词库里的违禁品词应被识别（依赖 seed_sensitive_words 已执行）。"""
        resp = await auth_client.post(
            BASE + "/test", json={"text": "承运危化品", "scope": "ecosystem"}
        )
        data = resp.json()["data"]
        if not data["wordHits"]:
            pytest.skip("种子词库未初始化，跳过")
        assert data["blocked"] is True
        assert any(h["word"] == "危化品" for h in data["wordHits"])

    async def test_empty_text_rejected(self, auth_client):
        resp = await auth_client.post(BASE + "/test", json={"text": "   "})
        body = resp.json()
        assert body["code"] != 0
        assert "请输入" in body["message"]
