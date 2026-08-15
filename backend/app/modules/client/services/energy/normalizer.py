"""外部字段 → 内部标准消费 DTO"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


_DEFAULT_MAP = {
    "externalTransactionId": ["externalTransactionId", "external_transaction_id", "txnId", "流水号"],
    "accountNo": ["accountNo", "account_no", "账号"],
    "cardNo": ["cardNo", "card_no", "卡号"],
    "vehicleNo": ["vehicleNo", "plateNumber", "plate_number", "车牌号"],
    "stationCode": ["stationCode", "station_code", "站点编码"],
    "stationName": ["stationName", "station_name", "站点", "油站"],
    "energyType": ["energyType", "energy_type", "能源类型"],
    "productName": ["productName", "product_name", "商品", "油品"],
    "quantity": ["quantity", "qty", "数量", "升数"],
    "unit": ["unit", "单位"],
    "unitPrice": ["unitPrice", "unit_price", "单价"],
    "amount": ["amount", "金额"],
    "transactionTime": ["transactionTime", "transaction_time", "消费时间", "时间"],
    "mileage": ["mileage", "里程"],
    "odometer": ["odometer", "表显里程"],
    "driverName": ["driverName", "driver_name", "司机"],
}


def _pick(raw: dict, keys: list[str]) -> Any:
    for k in keys:
        if k in raw and raw[k] not in (None, ""):
            return raw[k]
        # 大小写不敏感
        for rk, rv in raw.items():
            if str(rk).strip().lower() == str(k).strip().lower() and rv not in (None, ""):
                return rv
    return None


def _to_decimal(v) -> Optional[Decimal]:
    if v is None or v == "":
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None


def _to_dt(v) -> Optional[datetime]:
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v
    s = str(v).strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19] if len(s) >= 19 else s, fmt)
        except ValueError:
            continue
    return None


def json_safe_value(v: Any) -> Any:
    """把 Excel / 外部记录里的 datetime、Decimal 收成 JSON 可落库的值。"""
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, dict):
        return {k: json_safe_value(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [json_safe_value(x) for x in v]
    return v


def json_safe_record(raw: Optional[dict]) -> dict:
    return {k: json_safe_value(v) for k, v in (raw or {}).items()}


def normalize_record(raw: dict, field_mapping: Optional[dict] = None) -> dict:
    """把一条外部记录转成内部标准字段。

    field_mapping 形如 ``{"cardNo": "oil_card", "amount": "fee"}``，
    优先于默认别名。
    """
    mapping = dict(_DEFAULT_MAP)
    if field_mapping:
        for dest, src in field_mapping.items():
            if dest in mapping:
                mapping[dest] = [src] + list(mapping[dest])
            else:
                mapping[dest] = [src]

    energy_type = str(_pick(raw, mapping.get("energyType", [])) or "OIL").upper()
    if energy_type in ("油", "柴油", "汽油", "OIL"):
        energy_type = "OIL"
    elif energy_type in ("气", "LNG", "CNG", "GAS"):
        energy_type = "GAS"
    elif energy_type in ("电", "充电", "ELECTRIC", "ELECTRICITY"):
        energy_type = "ELECTRIC"

    return {
        "externalTransactionId": _pick(raw, mapping.get("externalTransactionId", [])),
        "accountNo": _pick(raw, mapping.get("accountNo", [])),
        "cardNo": _pick(raw, mapping.get("cardNo", [])),
        "vehicleNo": _pick(raw, mapping.get("vehicleNo", [])),
        "stationCode": _pick(raw, mapping.get("stationCode", [])),
        "stationName": _pick(raw, mapping.get("stationName", [])),
        "energyType": energy_type,
        "productName": _pick(raw, mapping.get("productName", [])),
        "quantity": _to_decimal(_pick(raw, mapping.get("quantity", []))),
        "unit": _pick(raw, mapping.get("unit", [])),
        "unitPrice": _to_decimal(_pick(raw, mapping.get("unitPrice", []))),
        "amount": _to_decimal(_pick(raw, mapping.get("amount", []))),
        "transactionTime": _to_dt(_pick(raw, mapping.get("transactionTime", []))),
        "mileage": _to_decimal(_pick(raw, mapping.get("mileage", []))),
        "odometer": _to_decimal(_pick(raw, mapping.get("odometer", []))),
        "driverName": _pick(raw, mapping.get("driverName", [])),
    }
