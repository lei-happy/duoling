"""运营后台 · 服务平台审核接口测试

只覆盖「接口通不通、入参守不守得住、口径对不对」这三件事：业务规则本身已由
``test_ecosystem_audit_service`` / ``test_ecosystem_whitelist_service`` 穷举，
这里不再重复造数据。

写操作全部落在回滚事务里（见 tests/conftest.py），不落库。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §4.1 / §4.2
对应后端：backend/app/modules/console/api/ecosystem/
"""

POSTS = "/api/console/ecosystem/posts"
WHITELIST = "/api/console/ecosystem/audit-whitelist"


class TestOptions:
    async def test_reject_reasons_carry_templates(self, auth_client):
        """运营选原因时要能看到「不补充说明，租户会收到哪句话」"""
        resp = await auth_client.get(f"{POSTS}/options")
        assert resp.status_code == 200
        data = resp.json()["data"]
        reasons = {r["value"]: r for r in data["rejectReasons"]}
        assert reasons[3]["label"] == "联系方式违规"
        assert reasons[3]["template"]
        assert reasons[3]["reasonRequired"] is False

    async def test_other_reason_requires_text(self, auth_client):
        """「其他」没有模板，必须自己写说明，否则租户收到的是一句空话"""
        resp = await auth_client.get(f"{POSTS}/options")
        reasons = {r["value"]: r for r in resp.json()["data"]["rejectReasons"]}
        assert reasons[9]["reasonRequired"] is True

    async def test_enums_are_labelled(self, auth_client):
        resp = await auth_client.get(f"{POSTS}/options")
        data = resp.json()["data"]
        assert all(o["label"] for o in data["postStatuses"])
        assert all(o["label"] for o in data["auditStatuses"])
        assert data["batchApproveLimit"] > 0

    async def test_precheck_flags_are_labelled(self, auth_client):
        """队列行里的 precheckFlags 是编码，界面要靠这份字典显示人话

        判定时那句人话没有落库（content_guard 的 suspicious_notes 只用于当场提示），
        所以编码与措辞的对应关系必须由后端下发，否则前端会各写一套。
        """
        resp = await auth_client.get(f"{POSTS}/options")
        flags = {f["value"]: f["label"] for f in resp.json()["data"]["precheckFlags"]}
        assert flags["new_tenant"]
        assert flags["was_force_delisted"]
        assert flags["insurance_expired"]


class TestBacklog:
    async def test_five_numbers_and_thresholds(self, auth_client):
        """顶部数字卡的五个数决定运营先看哪一堆，缺一个界面就少一块"""
        resp = await auth_client.get(f"{POSTS}/backlog")
        assert resp.status_code == 200
        data = resp.json()["data"]
        for key in (
            "pending",
            "pendingOverdue",
            "pendingFlagged",
            "spotCheckPending",
            "spotCheckOverdue",
            "slaMinutes",
            "warnMinutes",
        ):
            assert key in data, f"积压统计缺少 {key}"


class TestQueues:
    async def test_pending_queue_shape(self, auth_client):
        resp = await auth_client.get(POSTS + "/pending", params={"limit": 5})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert "list" in data and "total" in data and "count" in data
        for row in data["list"]:
            # 时效字段由后端算好，前端不重算（凌晨提交的自然时长会虚高 7 小时）
            assert "waitedMinutes" in row and "urgencyLabel" in row
            assert row["post"]["auditStatus"] == 1

    async def test_spot_check_queue_only_whitelist_pass(self, auth_client):
        resp = await auth_client.get(POSTS + "/spot-check", params={"limit": 5})
        assert resp.status_code == 200
        for row in resp.json()["data"]["list"]:
            assert row["post"]["auditStatus"] == 4

    async def test_search_all_accepts_shared_filters(self, auth_client):
        """三个队列共用一套筛选条件，切页签时条件不该失效"""
        resp = await auth_client.get(
            POSTS,
            params={
                "postType": 1,
                "keyword": "不存在的挂牌编号ZZZ",
                "flaggedOnly": "true",
                "limit": 5,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["list"] == []

    async def test_page_size_is_capped(self, auth_client):
        resp = await auth_client.get(POSTS + "/pending", params={"limit": 500})
        assert resp.status_code == 422


class TestDetail:
    async def test_missing_post_returns_business_error(self, auth_client):
        """挂牌不存在是业务失败（HTTP 200 + code -1），不是 404 裸抛"""
        resp = await auth_client.get(f"{POSTS}/99999999")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == -1
        assert "没找到" in body["message"]


class TestActionValidation:
    async def test_reject_requires_reason_code(self, auth_client):
        """驳回必须选原因编码，否则做不了审核质量统计"""
        resp = await auth_client.post(f"{POSTS}/1/reject", json={"reason": "随便写写"})
        assert resp.status_code == 422

    async def test_force_delist_requires_reason(self, auth_client):
        """强制下架不给理由，租户只会反复重新发布同样的内容"""
        resp = await auth_client.post(f"{POSTS}/1/force-delist", json={"reason": ""})
        assert resp.status_code == 422

    async def test_batch_approve_rejects_empty_selection(self, auth_client):
        resp = await auth_client.post(f"{POSTS}/batch-approve", json={"postIds": []})
        assert resp.status_code == 422

    async def test_batch_approve_rejects_oversized_batch(self, auth_client):
        resp = await auth_client.post(
            f"{POSTS}/batch-approve", json={"postIds": list(range(1, 200))}
        )
        assert resp.status_code == 422

    async def test_approve_on_missing_post_is_business_error(self, auth_client):
        resp = await auth_client.post(f"{POSTS}/99999999/approve", json={})
        assert resp.status_code == 200
        assert resp.json()["code"] == -1


class TestWhitelist:
    async def test_page_members(self, auth_client):
        resp = await auth_client.get(WHITELIST, params={"limit": 5})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "list" in data and "total" in data
        for row in data["list"]:
            assert row["tenantCode"]
            assert "whitelistSourceLabel" in row

    async def test_eligibility_lists_every_condition(self, auth_client):
        """资格判定要逐条回，界面上直接告诉运营还差什么"""
        resp = await auth_client.get(f"{WHITELIST}/__not_exist__/eligibility")
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        codes = {i["code"] for i in data["eligibility"]["items"]}
        assert codes == {
            "hall_enabled",
            "license_verified",
            "publish_volume",
            "no_reject",
            "deal_record",
            "no_violation",
            "recover_period",
        }
        assert all(i["detail"] for i in data["eligibility"]["items"])

    async def test_eligibility_blocking_flags(self, auth_client):
        """只有大厅能力与企业认证是人工也不能豁免的硬条件"""
        resp = await auth_client.get(f"{WHITELIST}/__not_exist__/eligibility")
        items = {i["code"]: i for i in resp.json()["data"]["eligibility"]["items"]}
        assert items["license_verified"]["blocking"] is True
        assert items["hall_enabled"]["blocking"] is True
        assert items["publish_volume"]["blocking"] is False

    async def test_grant_blocked_when_not_certified(self, auth_client):
        """未认证的企业人工也不能授予，错误文案要说清差在哪儿"""
        resp = await auth_client.post(
            WHITELIST, json={"tenantCode": "__not_exist__"}
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["code"] == -1
        assert "认证" in body["message"]

    async def test_revoke_requires_reason(self, auth_client):
        resp = await auth_client.post(
            f"{WHITELIST}/__not_exist__/revoke", json={"reason": ""}
        )
        assert resp.status_code == 422
