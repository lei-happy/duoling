"""驾驶员回单服务测试（落表版）

分两层：
1. 纯逻辑：``_to_dict`` 的 file_urls JSON 解析与容错；
2. 集成：连租户库 ``1001``，创建/列表/删除回单，并校验按 driver_id 的越权保护。

对应需求：doc/02.需求文档/03.移动端/02.驾驶员H5端/04.回单签收与凭证上传.md
覆盖用例：TC-DRV-RECEIPT-001/002/003/006/007
"""

import pytest

from app.common.exceptions import BizException
from app.modules.driver.services.driver_receipt_service import DriverReceiptService


# =====================================================================
# 1) 纯逻辑：_to_dict
# =====================================================================
class TestToDict:
    class _FakeReceipt:
        def __init__(self, file_urls):
            self.id = 10
            self.task_id = 100
            self.dispatch_order_id = None
            self.item_id = None
            self.driver_id = 5
            self.receipt_type = 1
            self.file_urls = file_urls
            self.remark = None
            self.uploader_name = "张三"
            self.created_at = None

    def test_parse_valid_json_urls(self):
        r = self._FakeReceipt('["a.jpg", "b.jpg"]')
        d = DriverReceiptService._to_dict(r)
        assert d["fileUrls"] == ["a.jpg", "b.jpg"]
        assert d["taskId"] == 100

    def test_broken_json_falls_back_to_empty(self):
        r = self._FakeReceipt("not-a-json")
        d = DriverReceiptService._to_dict(r)
        assert d["fileUrls"] == []

    def test_null_urls_empty(self):
        r = self._FakeReceipt(None)
        assert DriverReceiptService._to_dict(r)["fileUrls"] == []


# =====================================================================
# 2) 集成（真实租户库，事务回滚）
# =====================================================================
class TestReceiptIntegration:
    async def test_create_and_list(self, driver_ctx):
        session, ctx = driver_ctx
        data = await DriverReceiptService.create_receipt(
            session, ctx, task_id=1001, file_urls=["u1.jpg"], remark="第一张回单"
        )
        assert data["driverId"] == ctx.driver_id
        assert data["fileUrls"] == ["u1.jpg"]

        items, total = await DriverReceiptService.list_my_receipts(
            session, ctx, task_id=1001
        )
        assert total == 1
        assert items[0]["id"] == data["id"]

    async def test_empty_files_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        with pytest.raises(BizException):
            await DriverReceiptService.create_receipt(
                session, ctx, task_id=1001, file_urls=[]
            )

    async def test_over_9_files_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        with pytest.raises(BizException):
            await DriverReceiptService.create_receipt(
                session, ctx, task_id=1001,
                file_urls=[f"u{i}.jpg" for i in range(10)],
            )

    async def test_delete_own_receipt(self, driver_ctx):
        session, ctx = driver_ctx
        data = await DriverReceiptService.create_receipt(
            session, ctx, task_id=1001, file_urls=["u1.jpg"]
        )
        await DriverReceiptService.delete_receipt(session, ctx, data["id"])
        items, total = await DriverReceiptService.list_my_receipts(session, ctx)
        assert total == 0

    async def test_delete_others_receipt_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        data = await DriverReceiptService.create_receipt(
            session, ctx, task_id=1001, file_urls=["u1.jpg"]
        )
        # 伪造另一名司机上下文（同库，不同 driver_id）—— 用轻量假 driver 避免污染 ctx
        from types import SimpleNamespace

        from app.modules.driver.services.driver_context import DriverContext

        fake_driver = SimpleNamespace(id=ctx.driver_id + 999999, name="别的司机")
        other = DriverContext(
            user_id=990002,
            phone="19900005678",
            tenant_code=ctx.tenant_code,
            driver=fake_driver,
        )
        with pytest.raises(BizException):
            await DriverReceiptService.delete_receipt(session, other, data["id"])
