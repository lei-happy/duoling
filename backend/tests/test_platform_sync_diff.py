"""platform_sync 对比/校验：快照墓碑不得让 deploy 自检永远失败。"""

from scripts.platform_sync.diff_utils import (
    KEY_FUNCS,
    active_snapshot_rows,
    diff_list,
)
from scripts.platform_sync.validators import validate_snapshots


def _menu(*, code: str, name: str, deleted: int = 0) -> dict:
    return {
        "menu_code": code,
        "menu_name": name,
        "path": f"/{code.replace(':', '/')}",
        "parent_id": 196,
        "is_deleted": deleted,
        "visible": 1,
        "status": 1,
        "app_type": "client",
    }


def test_active_snapshot_rows_drops_tombstones():
    rows = [
        _menu(code="finance:cust-recon", name="客户对账单"),
        _menu(code="finance:receivable", name="应收管理", deleted=1),
    ]
    active = active_snapshot_rows(rows)
    assert [r["menu_code"] for r in active] == ["finance:cust-recon"]


def test_tombstone_in_snapshot_is_not_a_live_diff():
    """复现：快照留 is_deleted=1，线上 export 没有该条 → 曾被当成「新增」。"""
    snapshot = [
        _menu(code="finance:cust-recon", name="客户对账单"),
        _menu(code="finance:receivable", name="应收管理", deleted=1),
    ]
    live = [_menu(code="finance:cust-recon", name="客户对账单")]
    d = diff_list(
        active_snapshot_rows(snapshot),
        active_snapshot_rows(live),
        KEY_FUNCS["client_menu"],
    )
    assert d.is_empty


def test_validator_rejects_deleted_menu_rows():
    report = validate_snapshots(
        {
            "client_menu": [_menu(code="finance:invoice", name="发票管理", deleted=1)],
            "platform_menu": [],
            "product_version": [],
            "product_feature": [],
            "version_feature": {},
        }
    )
    assert not report.ok
    assert any("is_deleted=1" in e for e in report.errors)
