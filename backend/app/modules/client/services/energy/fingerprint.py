"""消费原始数据去重指纹"""

from __future__ import annotations

import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Optional


def build_data_hash(
    *,
    supplier_id: Optional[int],
    external_transaction_id: Optional[str],
    card_no: Optional[str],
    transaction_time: Optional[datetime | str],
    amount: Optional[Decimal | str | float],
    quantity: Optional[Decimal | str | float],
    station: Optional[str],
) -> str:
    if external_transaction_id:
        raw = f"ext|{supplier_id or ''}|{external_transaction_id}"
    else:
        ts = transaction_time.isoformat(sep=" ") if isinstance(transaction_time, datetime) else (transaction_time or "")
        raw = "|".join([
            str(supplier_id or ""),
            (card_no or "").strip(),
            str(ts),
            str(amount or ""),
            str(quantity or ""),
            (station or "").strip(),
        ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
