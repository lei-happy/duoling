"""能源账户记账内核纯逻辑测试

覆盖：
  - compute_ledger_delta / compute_frozen_delta 符号
  - 冲正反向变动
  - 账户 available_balance / diff_amount 派生
  - 串行扣减后余额一致性（模拟 FOR UPDATE 串行化）
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.services.energy.constants import (
    ACCOUNT_POSTPAID,
    ACCOUNT_PREPAID,
    TXN_ADJUSTMENT,
    TXN_CONSUMPTION,
    TXN_FEE,
    TXN_FREEZE,
    TXN_RECHARGE,
    TXN_REFUND,
    TXN_REVERSAL,
    TXN_TRANSFER_IN,
    TXN_TRANSFER_OUT,
    TXN_UNFREEZE,
    compute_frozen_delta,
    compute_ledger_delta,
    reversal_deltas,
)


class TestComputeLedgerDelta:
    def test_recharge_increases(self):
        assert compute_ledger_delta(TXN_RECHARGE, Decimal("100")) == Decimal("100")

    def test_consumption_decreases(self):
        assert compute_ledger_delta(TXN_CONSUMPTION, Decimal("30.5")) == Decimal("-30.5")

    def test_refund_increases(self):
        assert compute_ledger_delta(TXN_REFUND, Decimal("10")) == Decimal("10")

    def test_transfer(self):
        assert compute_ledger_delta(TXN_TRANSFER_IN, Decimal("8")) == Decimal("8")
        assert compute_ledger_delta(TXN_TRANSFER_OUT, Decimal("8")) == Decimal("-8")

    def test_fee_decreases(self):
        assert compute_ledger_delta(TXN_FEE, Decimal("1.2")) == Decimal("-1.2")

    def test_adjustment_keeps_signed_amount(self):
        assert compute_ledger_delta(TXN_ADJUSTMENT, Decimal("-15")) == Decimal("-15")
        assert compute_ledger_delta(TXN_ADJUSTMENT, Decimal("15")) == Decimal("15")

    def test_freeze_does_not_change_ledger(self):
        assert compute_ledger_delta(TXN_FREEZE, Decimal("50")) == Decimal("0")
        assert compute_ledger_delta(TXN_UNFREEZE, Decimal("50")) == Decimal("0")

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError):
            compute_ledger_delta(99, Decimal("1"))


class TestComputeFrozenDelta:
    def test_freeze_increases(self):
        assert compute_frozen_delta(TXN_FREEZE, Decimal("20")) == Decimal("20")

    def test_unfreeze_decreases(self):
        assert compute_frozen_delta(TXN_UNFREEZE, Decimal("20")) == Decimal("-20")

    def test_others_zero(self):
        assert compute_frozen_delta(TXN_RECHARGE, Decimal("20")) == Decimal("0")
        assert compute_frozen_delta(TXN_CONSUMPTION, Decimal("20")) == Decimal("0")


class TestReversal:
    def test_reverse_consumption(self):
        ledger, frozen = reversal_deltas(Decimal("-80"), Decimal("0"))
        assert ledger == Decimal("80")
        assert frozen == Decimal("0")

    def test_reverse_freeze(self):
        ledger, frozen = reversal_deltas(Decimal("0"), Decimal("30"))
        assert ledger == Decimal("0")
        assert frozen == Decimal("-30")

    def test_reverse_adjustment(self):
        ledger, frozen = reversal_deltas(Decimal("12.5"), Decimal("0"))
        assert ledger == Decimal("-12.5")


class TestAccountDerivedBalance:
    def test_available_and_diff(self):
        acc = EnergyAccount()
        acc.ledger_balance = Decimal("1000")
        acc.frozen_amount = Decimal("200")
        acc.supplier_balance = Decimal("980")
        assert acc.available_balance == Decimal("800")
        assert acc.diff_amount == Decimal("20")

    def test_diff_none_when_no_supplier_balance(self):
        acc = EnergyAccount()
        acc.ledger_balance = Decimal("100")
        acc.frozen_amount = Decimal("0")
        acc.supplier_balance = None
        assert acc.diff_amount is None


def _apply(acc: SimpleNamespace, txn_type: int, amount: Decimal, signed=None):
    """模拟 FOR UPDATE 串行记账（无 DB）。"""
    if signed is not None:
        ledger_delta = Decimal(signed)
        frozen_delta = Decimal("0")
    else:
        ledger_delta = compute_ledger_delta(txn_type, amount)
        frozen_delta = compute_frozen_delta(txn_type, amount)
    after = acc.ledger + ledger_delta
    frozen_after = acc.frozen + frozen_delta
    if frozen_after < 0:
        raise ValueError("over-unfreeze")
    if after < 0 and acc.account_type not in {ACCOUNT_POSTPAID}:
        raise ValueError("insufficient")
    acc.ledger = after
    acc.frozen = frozen_after
    acc.txns.append((txn_type, ledger_delta, frozen_delta, after))
    return after


class TestSerialBalanceConsistency:
    def test_recharge_then_consume(self):
        acc = SimpleNamespace(ledger=Decimal("0"), frozen=Decimal("0"),
                              account_type=ACCOUNT_PREPAID, txns=[])
        _apply(acc, TXN_RECHARGE, Decimal("500"))
        _apply(acc, TXN_CONSUMPTION, Decimal("120"))
        _apply(acc, TXN_CONSUMPTION, Decimal("80"))
        assert acc.ledger == Decimal("300")
        assert sum(t[1] for t in acc.txns) == acc.ledger

    def test_concurrent_style_serial_deductions(self):
        acc = SimpleNamespace(ledger=Decimal("1000"), frozen=Decimal("0"),
                              account_type=ACCOUNT_PREPAID, txns=[])
        for _ in range(20):
            _apply(acc, TXN_CONSUMPTION, Decimal("10"))
        assert acc.ledger == Decimal("800")
        assert acc.ledger == Decimal("1000") + sum(t[1] for t in acc.txns)

    def test_prepaid_rejects_overdraft(self):
        acc = SimpleNamespace(ledger=Decimal("50"), frozen=Decimal("0"),
                              account_type=ACCOUNT_PREPAID, txns=[])
        with pytest.raises(ValueError, match="insufficient"):
            _apply(acc, TXN_CONSUMPTION, Decimal("80"))

    def test_postpaid_allows_negative(self):
        acc = SimpleNamespace(ledger=Decimal("50"), frozen=Decimal("0"),
                              account_type=ACCOUNT_POSTPAID, txns=[])
        _apply(acc, TXN_CONSUMPTION, Decimal("80"))
        assert acc.ledger == Decimal("-30")

    def test_reversal_restores_balance(self):
        acc = SimpleNamespace(ledger=Decimal("200"), frozen=Decimal("0"),
                              account_type=ACCOUNT_PREPAID, txns=[])
        _apply(acc, TXN_CONSUMPTION, Decimal("60"))
        origin_delta = acc.txns[-1][1]
        rev, _ = reversal_deltas(origin_delta, Decimal("0"))
        _apply(acc, TXN_REVERSAL, Decimal("60"), signed=rev)
        assert acc.ledger == Decimal("200")

    def test_freeze_then_unfreeze(self):
        acc = SimpleNamespace(ledger=Decimal("500"), frozen=Decimal("0"),
                              account_type=ACCOUNT_PREPAID, txns=[])
        _apply(acc, TXN_FREEZE, Decimal("100"))
        assert acc.ledger == Decimal("500")
        assert acc.frozen == Decimal("100")
        _apply(acc, TXN_UNFREEZE, Decimal("40"))
        assert acc.frozen == Decimal("60")
        with pytest.raises(ValueError, match="over-unfreeze"):
            _apply(acc, TXN_UNFREEZE, Decimal("80"))
