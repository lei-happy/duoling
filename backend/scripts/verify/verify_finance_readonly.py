"""财务结算模块只读冒烟（文档 07 财务结算模块第 0~4 期）

覆盖：24 张表存在性 → 10 类单据状态机登记 → 194 条路由注册 → 各服务只读查询
→ 核算导出。全程只读并在结束时回滚，不落任何数据。

用法：
    python scripts/verify/verify_finance_readonly.py [tenant_code] [period]

退出码：全部通过 0；存在失败 1。
"""

import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import text

from app.core.database import db_manager
from app.modules.client.models import *  # noqa: F401,F403

TENANT = sys.argv[1] if len(sys.argv) > 1 else "1001"
PERIOD = sys.argv[2] if len(sys.argv) > 2 else "2026-08"

ok = 0
bad = 0
fails = []


def mark(name, passed, detail=""):
    global ok, bad
    if passed:
        print(f"[OK]   {name} {detail}")
        ok += 1
    else:
        print(f"[FAIL] {name} {detail}")
        bad += 1
        fails.append(f"{name} {detail}")


async def probe(name, coro):
    global ok, bad
    try:
        r = await coro
        if isinstance(r, dict) and "list" in r:
            n = f"(rows={len(r['list'])}, total={r.get('total')})"
        elif (
            isinstance(r, tuple) and len(r) >= 2
            and isinstance(r[0], list) and isinstance(r[1], int)
        ):
            # page_list 统一返回 (rows, total)，别把元组长度当行数报出去
            n = f"(rows={len(r[0])}, total={r[1]})"
        elif isinstance(r, (list, tuple)):
            n = f"(rows={len(r)})"
        elif isinstance(r, (bytes, bytearray)):
            n = f"({len(r)} bytes)"
        else:
            n = ""
        print(f"[OK]   {name} {n}")
        ok += 1
        return r
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")
        traceback.print_exc(limit=4)
        bad += 1
        fails.append(f"{name}: {type(e).__name__}: {e}")
        return None


FINANCE_TABLES = [
    "biz_finance_doc_event",
    "biz_recon_diff",
    "biz_customer_recon",
    "biz_customer_recon_waybill_link",
    "biz_customer_settlement",
    "biz_customer_settle_recon_link",
    "biz_receipt_voucher",
    "biz_receipt_settle_link",
    "biz_carrier_recon",
    "biz_carrier_recon_task_link",
    "biz_carrier_settlement_doc",
    "biz_carrier_settle_recon_link",
    "biz_driver_payroll",
    "biz_driver_payroll_task_link",
    "biz_driver_payroll_item",
    "biz_vendor_invoice",
    "biz_vendor_invoice_item",
    "biz_vendor_invoice_settle_link",
    "biz_customer_invoice",
    "biz_customer_invoice_item",
    "biz_customer_invoice_settle_link",
    "biz_bank_account",
    "biz_payment_batch",
    "biz_payment_batch_item",
]

EXPECTED_DOC_KINDS = [
    "task_finance",
    "customer_recon",
    "customer_settle",
    "customer_invoice",
    "carrier_recon",
    "carrier_settle",
    "driver_payroll",
    "receipt_voucher",
    "vendor_invoice",
    "payment_batch",
]


async def check_tables(db):
    print("\n=== 1. 财务表存在性（租户库 1001）===")
    rows = await db.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
    )
    exist = {r[0] for r in rows.fetchall()}
    missing = [t for t in FINANCE_TABLES if t not in exist]
    mark("24 张财务表齐全", not missing, f"缺失={missing}" if missing else f"({len(FINANCE_TABLES)} 张)")


def check_state_machine():
    print("\n=== 2. 状态机与事件类型登记 ===")
    from app.modules.client.services.finance.base import finance_state_machine as fsm
    from app.modules.client.services.finance.base.finance_doc_event_writer import (
        FinanceEventType,
    )

    states = fsm.DOC_KIND_STATES
    missing = [k for k in EXPECTED_DOC_KINDS if k not in states]
    mark("10 类 doc_kind 已登记状态集", not missing, f"缺失={missing}" if missing else "")

    vals = {
        v
        for k, v in vars(FinanceEventType).items()
        if not k.startswith("_") and isinstance(v, int)
    }
    gaps = [v for v in range(1, 29) if v not in vals]
    mark("事件类型 1~28 连续无缺口", not gaps, f"缺失={gaps}" if gaps else "")

    labels = fsm.DOC_KIND_STATUS_LABELS
    mark(
        "对账 / 应收 / 应付 / 收款单的状态 3 文案已分化",
        len({labels.get(k, {}).get(3) for k in ("customer_recon", "customer_settle", "carrier_settle", "receipt_voucher")}) >= 3,
    )


def check_routes():
    print("\n=== 3. 路由注册 ===")
    from app.modules.client.api import router as client_router

    paths = [r.path for r in client_router.routes if getattr(r, "methods", None)]
    fin = [p for p in paths if "/finance/" in p]
    mark("财务路由已注册", len(fin) >= 180, f"({len(fin)} 条)")

    prefixes = [
        "customer-recon",
        "customer-settlement",
        "receipt",
        "ar-aging",
        "recon-workbench",
        "carrier-recon",
        "carrier-settlement",
        "driver-payroll",
        "vendor-invoice",
        "customer-invoice",
        "bank-account",
        "payment-batch",
        "profit",
    ]
    miss = [p for p in prefixes if not any(f"/finance/{p}" in x for x in fin)]
    mark("13 个财务模块前缀齐全", not miss, f"缺失={miss}" if miss else "")

    dup = {p for p in fin if fin.count(p) > 1}
    # 同路径不同方法属正常，按 (method, path) 判重
    pairs = [(m, r.path) for r in client_router.routes if getattr(r, "methods", None)
             for m in r.methods if "/finance/" in r.path]
    real_dup = {x for x in pairs if pairs.count(x) > 1}
    mark("无重复的方法+路径组合", not real_dup, f"重复={sorted(real_dup)[:5]}" if real_dup else f"(同路径多方法 {len(dup)} 组，正常)")

    mark("出纳台三个读接口挂在 payment-batch 下",
         all(any(f"/finance/payment-batch/workbench/{s}" in p for p in fin)
             for s in ("overview", "flow", "calendar")))


async def check_phase2(db):
    print("\n=== 4. 第 2 期：客户侧应收 ===")
    from app.modules.client.services.finance.customer import (
        AgingService,
        CustomerReconService,
        CustomerSettlementService,
        ReceiptVoucherService,
    )
    from app.modules.client.services.finance.recon.workbench_service import (
        ReconWorkbenchService,
    )

    await probe("recon.page_list", CustomerReconService.page_list(db, page=1, page_size=5))
    await probe(
        "recon.candidates(customer_id=1)",
        CustomerReconService.list_candidates(db, customer_id=1, limit=10),
    )
    await probe("settle.page_list", CustomerSettlementService.page_list(db, page=1, page_size=5))
    await probe("receipt.page_list", ReceiptVoucherService.page_list(db, page=1, page_size=5))
    await probe("receipt.cashier_stats", ReceiptVoucherService.cashier_stats(db))
    await probe("aging.summary", AgingService.summary(db))
    await probe("aging.customer_page", AgingService.customer_page(db, page=1, page_size=5))
    await probe("aging.export", AgingService.build_export_workbook(db))
    await probe("workbench.summary", ReconWorkbenchService.summary(db))
    await probe(
        "workbench.pending_waybill_groups",
        ReconWorkbenchService.pending_waybill_groups(db, limit=10),
    )


async def check_phase3(db):
    print("\n=== 5. 第 3 期：应付三线 ===")
    from app.modules.client.services.finance.carrier import (
        CarrierReconService,
        CarrierSettlementDocService,
    )
    from app.modules.client.services.finance.driver import DriverPayrollService
    from app.modules.client.services.finance.invoice import VendorInvoiceService

    await probe("carrier_recon.page_list", CarrierReconService.page_list(db, page=1, page_size=5))
    await probe(
        "carrier_recon.candidates(carrier_id=1)",
        CarrierReconService.list_candidates(db, carrier_id=1, limit=10),
    )
    await probe(
        "carrier_settle.page_list",
        CarrierSettlementDocService.page_list(db, page=1, page_size=5),
    )
    await probe(
        "carrier_settle.recon_candidates",
        CarrierSettlementDocService.list_recon_candidates(db, carrier_id=1),
    )
    await probe(
        "carrier_settle.accounts", CarrierSettlementDocService.list_accounts(db, carrier_id=1)
    )
    await probe("payroll.page_list", DriverPayrollService.page_list(db, page=1, page_size=5))
    await probe(
        "payroll.candidates(driver_id=1)",
        DriverPayrollService.list_candidates(db, driver_id=1, limit=10),
    )
    await probe("vendor_invoice.page_list", VendorInvoiceService.page_list(db, page=1, page_size=5))
    await probe(
        "vendor_invoice.pending_settles", VendorInvoiceService.pending_settles(db)
    )
    await probe(
        "vendor_invoice.deduct_summary", VendorInvoiceService.deduct_summary(db, group_by="period")
    )


async def check_phase4(db):
    print("\n=== 6. 第 4 期：票据与资金 + 经营核算 ===")
    from app.modules.client.services.finance.accounting import ProfitAccountingService
    from app.modules.client.services.finance.accounting.accounting_constants import (
        DIMENSIONS,
    )
    from app.modules.client.services.finance.cashier import (
        BankAccountService,
        CashierService,
        PaymentBatchService,
    )
    from app.modules.client.services.finance.customer import CustomerInvoiceService

    await probe("cust_invoice.page_list", CustomerInvoiceService.page_list(db, page=1, page_size=5))
    await probe("cust_invoice.pending_settles", CustomerInvoiceService.pending_settles(db, limit=5))
    await probe("bank.page_list", BankAccountService.page_list(db, page=1, page_size=5))
    await probe("bank.options", BankAccountService.options(db))
    await probe("bank.balance_summary", BankAccountService.balance_summary(db))
    await probe("batch.page_list", PaymentBatchService.page_list(db, page=1, page_size=5))
    await probe("batch.candidates", PaymentBatchService.list_candidates(db, limit=20))
    await probe("cashier.overview", CashierService.overview(db))
    await probe("cashier.flow_list", CashierService.flow_list(db, page=1, page_size=5))
    await probe("cashier.pay_calendar", CashierService.pay_calendar(db, days=14))
    await probe("profit.kpi", ProfitAccountingService.kpi(db, period=PERIOD))
    for dim in DIMENSIONS:
        await probe(
            f"profit.by_dimension[{dim}]",
            ProfitAccountingService.by_dimension(db, dimension=dim, period=PERIOD),
        )
    await probe(
        "profit.drill_down",
        ProfitAccountingService.drill_down(
            db, dimension="customer", dimension_value="0", period=PERIOD
        ),
    )
    await probe("profit.inter_entity", ProfitAccountingService.inter_entity(db, period=PERIOD))
    await probe("profit.export", ProfitAccountingService.build_export_workbook(db, period=PERIOD))


def check_cost_allocator():
    print("\n=== 7. 台数分摊纯函数 ===")
    from decimal import Decimal

    from app.modules.client.services.finance.accounting.cost_allocator import (
        allocate_task_cost_to_waybills,
        split_doc_amount_by_task,
    )

    alloc, un = allocate_task_cost_to_waybills(
        {1: Decimal("1000.00")},
        {1: [(11, Decimal("1")), (12, Decimal("1")), (13, Decimal("1"))]},
    )
    mark(
        "除不尽时分摊无损（1000 / 3 台）",
        sum(alloc.values()) == Decimal("1000.00") and un == 0,
        f"{[str(v) for v in alloc.values()]}",
    )

    alloc2, un2 = allocate_task_cost_to_waybills(
        {1: Decimal("100.00")}, {1: [(11, Decimal("3")), (12, Decimal("1"))]}
    )
    mark(
        "按台数比例分摊",
        alloc2 == {11: Decimal("75.00"), 12: Decimal("25.00")},
        f"{ {k: str(v) for k, v in alloc2.items()} }",
    )

    alloc3, un3 = allocate_task_cost_to_waybills({1: Decimal("500.00")}, {1: []})
    mark("无挂接行时成本进未分摊而非丢弃", not alloc3 and un3 == Decimal("500.00"), f"未分摊={un3}")

    alloc4, un4 = allocate_task_cost_to_waybills(
        {1: Decimal("500.00")}, {1: [(11, Decimal("0"))]}
    )
    mark("台数合计为 0 时进未分摊", not alloc4 and un4 == Decimal("500.00"), f"未分摊={un4}")

    s1 = split_doc_amount_by_task(Decimal("1000.00"), [(1, Decimal("0")), (2, Decimal("0"))])
    mark(
        "单据金额按任务权重全 0 时平均且不丢分",
        sum(v for _, v in s1) == Decimal("1000.00"),
        f"{[str(v) for _, v in s1]}",
    )

    s2 = split_doc_amount_by_task(Decimal("100.00"), [])
    mark("无任务可摊时返回空列表", s2 == [], f"{s2}")


async def main():
    db_manager._get_or_create_tenant_engine(TENANT)
    factory = db_manager._tenant_session_factories[TENANT]
    async with factory() as db:
        await check_tables(db)
        check_state_machine()
        check_routes()
        check_cost_allocator()
        await check_phase2(db)
        await check_phase3(db)
        await check_phase4(db)
        await db.rollback()
    await db_manager.close_all()
    print("\n" + "=" * 56)
    print(f"通过 {ok} 项，失败 {bad} 项")
    if fails:
        print("失败明细：")
        for f in fails:
            print("  -", f)
    return 1 if bad else 0


sys.exit(asyncio.run(main()))
