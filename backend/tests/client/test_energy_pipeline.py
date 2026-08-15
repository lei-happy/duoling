"""能源消费管线纯逻辑：指纹、标准化、风控判定"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.modules.client.services.energy.fingerprint import build_data_hash
from app.modules.client.services.energy.normalizer import json_safe_record, normalize_record
from app.modules.client.services.energy.risk_engine import (
    evaluate_over_tank,
    evaluate_price_deviation,
)


class TestFingerprint:
    def test_external_id_stable(self):
        a = build_data_hash(
            supplier_id=1, external_transaction_id="X1",
            card_no=None, transaction_time=None, amount=None, quantity=None, station=None,
        )
        b = build_data_hash(
            supplier_id=1, external_transaction_id="X1",
            card_no="other", transaction_time=None, amount=99, quantity=None, station=None,
        )
        assert a == b

    def test_business_fingerprint_differs(self):
        t = datetime(2026, 8, 1, 10, 0, 0)
        a = build_data_hash(
            supplier_id=1, external_transaction_id=None,
            card_no="C1", transaction_time=t, amount=100, quantity=10, station="S1",
        )
        b = build_data_hash(
            supplier_id=1, external_transaction_id=None,
            card_no="C1", transaction_time=t, amount=101, quantity=10, station="S1",
        )
        assert a != b


class TestNormalizer:
    def test_chinese_headers(self):
        std = normalize_record({
            "卡号": "CARD001",
            "金额": "2163.6",
            "数量": "300.5",
            "消费时间": "2026-08-10 15:30:00",
            "能源类型": "柴油",
            "车牌号": "沪A12345",
        })
        assert std["cardNo"] == "CARD001"
        assert std["amount"] == Decimal("2163.6")
        assert std["quantity"] == Decimal("300.5")
        assert std["energyType"] == "OIL"
        assert std["vehicleNo"] == "沪A12345"
        assert std["transactionTime"].year == 2026

    def test_custom_mapping(self):
        std = normalize_record(
            {"oil_card": "C9", "fee": "12.5"},
            field_mapping={"cardNo": "oil_card", "amount": "fee"},
        )
        assert std["cardNo"] == "C9"
        assert std["amount"] == Decimal("12.5")

    def test_json_safe_datetime(self):
        t = datetime(2026, 8, 10, 15, 30, 0)
        safe = json_safe_record({"消费时间": t, "金额": Decimal("12.5")})
        assert safe["消费时间"] == "2026-08-10 15:30:00"
        assert safe["金额"] == "12.5"
        std = normalize_record(safe)
        assert std["transactionTime"] == t
        assert std["amount"] == Decimal("12.5")


class TestRiskEvaluate:
    def test_over_tank(self):
        assert evaluate_over_tank(Decimal("700"), Decimal("600"), Decimal("1"))
        assert not evaluate_over_tank(Decimal("500"), Decimal("600"), Decimal("1"))
        assert not evaluate_over_tank(None, Decimal("600"), Decimal("1"))

    def test_price_deviation(self):
        assert evaluate_price_deviation(Decimal("9"), Decimal("7"), Decimal("0.15"))
        assert not evaluate_price_deviation(Decimal("7.2"), Decimal("7"), Decimal("0.15"))
