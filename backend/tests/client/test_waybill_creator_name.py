"""计划列表「创建人」：序列化与展示名解析（纯逻辑，零 DB）

对应代码：
  - backend/app/modules/client/schemas/waybill/waybill.py
  - backend/app/modules/client/services/waybill/waybill_service.py
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from app.modules.client.schemas.waybill.waybill import WaybillOut
from app.modules.client.services.waybill.waybill_service import WaybillService


def _waybill(**overrides) -> SimpleNamespace:
    base = dict(
        id=1,
        waybill_no="JH001",
        customer_id=1,
        customer_name="客户A",
        enterprise_id=None,
        origin="成都",
        origin_code=None,
        origin_region_id=None,
        destination="重庆",
        destination_code=None,
        destination_region_id=None,
        vehicle_brand="比亚迪",
        vehicle_model="汉",
        quantity=1,
        plan_issue_time=None,
        required_load_time=None,
        required_deliver_time=None,
        dealer_name=None,
        dealer_contact=None,
        dealer_phone=None,
        dealer_address=None,
        freight_amount=None,
        freight_source=None,
        contract_id=None,
        rate_id=None,
        status=0,
        receipt_at=None,
        calc_status=None,
        is_locked=0,
        waybill_version=1,
        last_calc_at=None,
        last_result_id=None,
        remark=None,
        created_by=12,
        created_at=datetime(2026, 8, 16, 10, 0, 0),
    )
    base.update(overrides)
    return SimpleNamespace(**base)


class TestWaybillOutCreatorName:
    def test_from_model_includes_created_by_name(self):
        out = WaybillOut.from_model(_waybill(), created_by_name="张三")
        assert out.createdBy == 12
        assert out.createdByName == "张三"

    def test_from_model_created_by_name_optional(self):
        out = WaybillOut.from_model(_waybill(created_by=None))
        assert out.createdBy is None
        assert out.createdByName is None


class TestUserDisplayName:
    def test_prefers_real_name(self):
        u = SimpleNamespace(real_name="张三", nickname="小张", phone="13800000000")
        assert WaybillService._user_display_name(u) == "张三"

    def test_falls_back_to_nickname(self):
        u = SimpleNamespace(real_name=None, nickname="小张", phone="13800000000")
        assert WaybillService._user_display_name(u) == "小张"

    def test_falls_back_to_phone(self):
        u = SimpleNamespace(real_name="  ", nickname=None, phone="13800000000")
        assert WaybillService._user_display_name(u) == "13800000000"

    def test_empty_when_all_blank(self):
        u = SimpleNamespace(real_name=None, nickname="", phone=None)
        assert WaybillService._user_display_name(u) is None
