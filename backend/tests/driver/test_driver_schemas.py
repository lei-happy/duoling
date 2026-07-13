"""驾驶员端请求/响应 Schema 校验（纯逻辑，零 DB 依赖）

覆盖司机动作请求体的必填 / 长度 / 数量边界，以及回单上传请求的图片数量约束，
这些约束是接口反向用例（参数校验）的第一道防线。

对应需求：doc/02.需求文档/03.移动端/02.驾驶员H5端/02.任务流转与司机动作.md
        doc/02.需求文档/03.移动端/02.驾驶员H5端/04.回单签收与凭证上传.md
        doc/02.需求文档/03.移动端/02.驾驶员H5端/05.个人中心与资质.md
覆盖用例：TC-DRV-TASK-006/007、TC-DRV-RECEIPT-004/005、TC-DRV-PROFILE-003
"""

import pytest
from pydantic import ValidationError

from app.modules.driver.api.task_receipt import ReceiptUploadRequest
from app.modules.driver.schemas.profile import DriverProfileUpdate
from app.modules.driver.schemas.task import (
    DriverConfirmLoadRequest,
    DriverRejectTaskRequest,
    DriverRevertSignRequest,
    DriverSignItemRequest,
)


# =====================================================================
# 拒单 / 撤销签收：reason 必填且 >= 1 字符
# =====================================================================
class TestReasonRequired:
    def test_reject_reason_required(self):
        with pytest.raises(ValidationError):
            DriverRejectTaskRequest()

    def test_reject_reason_empty_rejected(self):
        with pytest.raises(ValidationError):
            DriverRejectTaskRequest(reason="")

    def test_reject_reason_ok(self):
        req = DriverRejectTaskRequest(reason="车辆故障无法承运")
        assert req.reason == "车辆故障无法承运"

    def test_revert_sign_reason_required(self):
        with pytest.raises(ValidationError):
            DriverRevertSignRequest()

    def test_revert_sign_reason_too_long(self):
        with pytest.raises(ValidationError):
            DriverRevertSignRequest(reason="x" * 256)

    def test_revert_sign_reason_ok(self):
        assert DriverRevertSignRequest(reason="签收信息有误").reason


# =====================================================================
# 确认装车 / 签收：照片数量与备注长度边界
# =====================================================================
class TestLoadAndSign:
    def test_confirm_load_defaults(self):
        req = DriverConfirmLoadRequest()
        assert req.photoUrls == []
        assert req.actualLoadTime is None

    def test_confirm_load_photo_max_9(self):
        DriverConfirmLoadRequest(photoUrls=[f"u{i}" for i in range(9)])
        with pytest.raises(ValidationError):
            DriverConfirmLoadRequest(photoUrls=[f"u{i}" for i in range(10)])

    def test_confirm_load_remark_max_255(self):
        with pytest.raises(ValidationError):
            DriverConfirmLoadRequest(remark="备" * 256)

    def test_sign_item_optional(self):
        req = DriverSignItemRequest()
        assert req.signedAt is None
        assert req.remark is None


# =====================================================================
# 回单上传：fileUrls 1~9 张，taskId >= 1
# =====================================================================
class TestReceiptUpload:
    def test_empty_files_rejected(self):
        with pytest.raises(ValidationError):
            ReceiptUploadRequest(taskId=1, fileUrls=[])

    def test_over_9_files_rejected(self):
        with pytest.raises(ValidationError):
            ReceiptUploadRequest(taskId=1, fileUrls=[f"u{i}" for i in range(10)])

    def test_task_id_must_be_positive(self):
        with pytest.raises(ValidationError):
            ReceiptUploadRequest(taskId=0, fileUrls=["u1"])

    def test_valid_payload(self):
        req = ReceiptUploadRequest(taskId=5, fileUrls=["u1", "u2"])
        assert req.receiptType == 1  # 默认签收回单
        assert req.itemId is None


# =====================================================================
# 个人资料更新：白名单字段长度约束
# =====================================================================
class TestProfileUpdate:
    def test_all_optional(self):
        req = DriverProfileUpdate()
        assert req.emergencyContact is None

    def test_emergency_contact_max_50(self):
        with pytest.raises(ValidationError):
            DriverProfileUpdate(emergencyContact="人" * 51)

    def test_home_address_max_255(self):
        with pytest.raises(ValidationError):
            DriverProfileUpdate(homeAddress="址" * 256)

    def test_no_name_or_phone_field(self):
        """白名单不含 name / phone / idCard —— 多余字段应被忽略而非写入。"""
        req = DriverProfileUpdate(homeAddress="某市某区")
        dumped = req.model_dump()
        assert "name" not in dumped
        assert "phone" not in dumped
        assert "idCard" not in dumped
