"""应付与资金链路写验证（文档 03 / 04 / 10 / 11 / 02 §销项票）

覆盖：
  A 承运商对账 → 行调整 → 大额审批门槛 → 确认 → 回签 → 任务锁定
  B 承运商结算 → 关联对账 → 提交 → 审批 → 付款 → 撤销付款（末态停在已审批）
  C 司机工资单 → 任务提成 → 工资项（应发/扣减/抵账）→ 提交审批发放
  D 进项票登记 → 票款核销 → 撤销核销 → 作废
  E 银行账户 → 余额校准 → 打款批次（多类单据混批）→ 审批 → 逐笔成败执行
  F 销项票 → 关联结算单 → 提交 → 开票 → 红冲
  G 反向闸口：锁定任务禁改、越额核销、重复票号、状态越级
  H 事件留痕：本次事务内新增的审计事件按单据大类与类型汇总

安全性：脚本自行把少量任务改成可结算状态作为候选池，全部写操作在单个事务内
执行，跑完即 ``rollback``，不污染租户库。

用法：
    python scripts/verify/verify_finance_payable_chain.py [tenant_code]

退出码：全部通过 0；存在失败 1。
"""

import asyncio
import os
import sys
import traceback
from datetime import date, datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import text

from app.core.database import db_manager
from app.common.exceptions import BizException
from app.modules.client.models import *  # noqa: F401,F403

TENANT = sys.argv[1] if len(sys.argv) > 1 else "1001"
OP = 1

ok = 0
bad = 0
fails = []


def check(name, cond, detail=""):
    global ok, bad
    if cond:
        print(f"  [OK]   {name} {detail}")
        ok += 1
    else:
        print(f"  [FAIL] {name} {detail}")
        bad += 1
        fails.append(f"{name} {detail}")


async def step(name, coro):
    global bad
    try:
        r = await coro
        print(f"  [OK]   {name}")
        globals()["ok"] = globals()["ok"] + 1
        return r
    except Exception as e:  # noqa: BLE001
        print(f"  [FAIL] {name}: {type(e).__name__}: {e}")
        traceback.print_exc(limit=3)
        bad += 1
        fails.append(f"{name}: {type(e).__name__}: {e}")
        return None


async def expect_biz(name, coro, keyword=None):
    """断言必须抛业务异常（反向闸口）。"""
    global ok, bad
    try:
        await coro
    except BizException as e:
        if keyword and keyword not in str(e):
            print(f"  [FAIL] {name}: 文案未命中「{keyword}」，实际：{e}")
            bad += 1
            fails.append(f"{name}: 文案不符 {e}")
            return
        print(f"  [OK]   {name}（已拦截：{e}）")
        ok += 1
        return
    except Exception as e:  # noqa: BLE001
        print(f"  [FAIL] {name}: 期望 BizException，实际 {type(e).__name__}: {e}")
        bad += 1
        fails.append(f"{name}: 异常类型不符 {type(e).__name__}")
        return
    print(f"  [FAIL] {name}: 未拦截，动作被放过")
    bad += 1
    fails.append(f"{name}: 未拦截")


async def prepare(db):
    """在事务内把少量任务改成可结算状态，作为候选池数据源。"""
    print("\n=== 0. 准备候选数据（事务内，最后回滚）===")
    arrive = datetime.now() - timedelta(days=3)

    r = await db.execute(
        text(
            "SELECT id FROM biz_task WHERE is_deleted = 0 AND carrier_type = 2 "
            "AND carrier_id = 100 ORDER BY id LIMIT 4"
        )
    )
    carrier_tasks = [x[0] for x in r.fetchall()]
    await db.execute(
        text(
            "UPDATE biz_task SET status = 5, is_locked = 0, is_recon_bound = 0, "
            "carrier_cost_amount = 3000.00, total_quantity = 3, "
            "actual_arrive_time = :t WHERE id IN :ids"
        ).bindparams(**{"t": arrive}),
        {"ids": tuple(carrier_tasks)},
    )
    print(f"  承运商任务候选：{carrier_tasks}")

    # 工资单校验任务的 capacity 必须挂在这位司机名下，故按 biz_capacity.driver_id 取
    r = await db.execute(
        text(
            "SELECT t.id, c.driver_id FROM biz_task t "
            "JOIN biz_capacity c ON c.id = t.capacity_id AND c.is_deleted = 0 "
            "WHERE t.is_deleted = 0 AND t.carrier_type = 1 AND c.driver_id IS NOT NULL "
            "ORDER BY c.driver_id, t.id LIMIT 3"
        )
    )
    self_rows = [tuple(x) for x in r.fetchall()]
    if self_rows:
        first_driver = self_rows[0][1]
        self_rows = [x for x in self_rows if x[1] == first_driver]
    self_tasks = [x[0] for x in self_rows]
    if self_tasks:
        await db.execute(
            text(
                "UPDATE biz_task SET status = 5, is_payroll_bound = 0, payroll_settled = 0, "
                "carrier_cost_amount = 1500.00, total_quantity = 2, "
                "actual_arrive_time = :t WHERE id IN :ids"
            ).bindparams(**{"t": arrive}),
            {"ids": tuple(self_tasks)},
        )
    print(f"  自有车任务候选：{self_rows}")

    # 打款批次要验「多类单据混批 + 逐笔成败」，借一张任务费用单退回已审批态凑第二笔
    r = await db.execute(
        text(
            "SELECT id FROM biz_task_finance_doc WHERE is_deleted = 0 "
            "AND planned_amount > 0 ORDER BY id LIMIT 1"
        )
    )
    tf_id = r.scalar()
    if tf_id:
        await db.execute(
            text("UPDATE biz_task_finance_doc SET status = 2 WHERE id = :i"),
            {"i": tf_id},
        )
    print(f"  任务费用单候选：{tf_id}")
    await db.flush()
    return carrier_tasks, self_rows, arrive


async def flow_carrier(db, carrier_tasks, arrive):
    print("\n=== A. 承运商对账单 ===")
    from app.modules.client.services.finance.carrier import CarrierReconService

    cands = await CarrierReconService.list_candidates(db, carrier_id=100, limit=10)
    check("候选池能捞到已交车任务", len(cands) >= 3, f"(候选 {len(cands)} 条)")

    recon = await step(
        "建对账单（3 条任务）",
        CarrierReconService.create_from_candidates(
            db,
            carrier_id=100,
            period_start=arrive - timedelta(days=30),
            period_end=arrive + timedelta(days=1),
            task_ids=carrier_tasks[:3],
            operator_id=OP,
        ),
    )
    if recon is None:
        return None
    await db.flush()
    check("对账单初始为草稿", int(recon.status) == 0, f"status={recon.status}")
    check(
        "毛额已按任务成本汇总",
        Decimal(str(recon.gross_amount_total)) > 0,
        f"gross={recon.gross_amount_total}",
    )

    lines = await CarrierReconService.list_lines(db, recon.id)
    check("对账行数与任务数一致", len(lines) == 3, f"(行 {len(lines)} 条)")

    await step(
        "追加第 4 条任务",
        CarrierReconService.add_tasks(db, recon.id, [carrier_tasks[3]], operator_id=OP),
    )
    await db.flush()
    lines = await CarrierReconService.list_lines(db, recon.id)
    check("追加后行数为 4", len(lines) == 4, f"(行 {len(lines)} 条)")

    # 净应付 = planned_amount（毛额已含行调整，再减预付扣减），结算单按它付钱
    def recon_net(m):
        return Decimal(str(m.planned_amount or 0))

    await db.refresh(recon)
    before = recon_net(recon)
    await step(
        "行调整 -200（小额，免审批）",
        CarrierReconService.adjust_line(
            db, recon.id, lines[0].id,
            adjust_amount=Decimal("-200.00"), adjust_reason="路损扣款",
            operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(recon)
    check(
        "净额随调整下降 200",
        recon_net(recon) == before - Decimal("200.00"),
        f"{before} → {recon_net(recon)}",
    )

    await step(
        "行调整 -8000（大额，触发审批门槛）",
        CarrierReconService.adjust_line(
            db, recon.id, lines[1].id,
            adjust_amount=Decimal("-8000.00"), adjust_reason="重大质损索赔",
            operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(recon)
    await expect_biz(
        "大额调整未审批时确认被拦截",
        CarrierReconService.confirm(db, recon.id, operator_id=OP),
    )
    await step("审批大额调整", CarrierReconService.approve_adjust(db, recon.id, operator_id=OP))
    await db.flush()

    await step("确认对账单", CarrierReconService.confirm(db, recon.id, operator_id=OP))
    await db.flush()
    await db.refresh(recon)
    check("确认后状态转已确认", int(recon.status) == 2, f"status={recon.status}")

    r = await db.execute(
        text("SELECT COUNT(*) FROM biz_task WHERE id IN :ids AND is_recon_bound = 1"),
        {"ids": tuple(carrier_tasks[:4])},
    )
    n = r.scalar()
    check("四条任务已打对账挂接标记", n == 4, f"(标记 {n} 条)")

    await step(
        "登记承运商回签",
        CarrierReconService.record_carrier_sign(
            db, recon.id, signer_name="德信-王经理", signed_at=datetime.now(), operator_id=OP
        ),
    )
    await db.flush()

    await expect_biz(
        "已确认对账单的任务禁止业务侧改成本",
        _assert_task_unbound(db, carrier_tasks[0]),
        keyword="对账单",
    )
    return recon


async def _assert_task_unbound(db, task_id):
    from app.modules.client.services.finance.linkage.task_to_finance import TaskToFinance

    await TaskToFinance.assert_unbound(db, task_id, action="update")


async def flow_carrier_settle(db, recon):
    print("\n=== B. 承运商结算单 ===")
    from app.modules.client.services.finance.carrier import CarrierSettlementDocService

    cands = await CarrierSettlementDocService.list_recon_candidates(db, carrier_id=100)
    mine = next((c for c in cands if int(c["reconId"]) == recon.id), None)
    check("已确认对账单进入结算候选", mine is not None, f"(候选 {len(cands)} 条)")
    if mine is None:
        return None

    accounts = await CarrierSettlementDocService.list_accounts(db, carrier_id=100)
    acct_id = accounts[0]["accountId"] if accounts else None
    check("承运商结算账户可选", acct_id is not None, f"(账户 {len(accounts)} 个)")

    net = Decimal(str(recon.planned_amount))
    check("候选可结金额 = 对账净额",
          Decimal(str(mine["availableAmount"])) == net,
          f"{mine['availableAmount']} vs {net}")
    settle = await step(
        "建结算单（关联对账单，全额）",
        CarrierSettlementDocService.create_from_recons(
            db,
            carrier_id=100,
            recons=[{"reconId": recon.id, "amount": net}],
            settlement_account_id=acct_id,
            due_date=date.today() + timedelta(days=15),
            operator_id=OP,
        ),
    )
    if settle is None:
        return None
    await db.flush()
    check("结算金额 = 对账净额", Decimal(str(settle.planned_amount)) == net,
          f"{settle.planned_amount} vs {net}")

    await expect_biz(
        "草稿态不能直接付款",
        CarrierSettlementDocService.pay(
            db, settle.id, actual_amount=net, settlement_account_id=acct_id, operator_id=OP
        ),
    )
    await step("提交结算单", CarrierSettlementDocService.submit(db, settle.id, OP))
    await db.flush()
    await step("审批结算单", CarrierSettlementDocService.approve(db, settle.id, OP))
    await db.flush()
    await db.refresh(settle)
    check("审批后状态为已审批", int(settle.status) == 2, f"status={settle.status}")

    await step(
        "付款登记",
        CarrierSettlementDocService.pay(
            db, settle.id, actual_amount=net, paid_at=datetime.now(),
            pay_method=1, settlement_account_id=acct_id, operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(settle)
    check("付款后状态为已支付", int(settle.status) == 3, f"status={settle.status}")

    r = await db.execute(
        text(
            "SELECT COUNT(*) FROM biz_task t JOIN biz_carrier_recon_task_link l "
            "ON l.task_id = t.id WHERE l.recon_id = :rid AND t.is_locked = 1"
        ),
        {"rid": recon.id},
    )
    n = r.scalar()
    check("付款后任务被锁定", n == 4, f"(锁定 {n} 条)")

    await step(
        "撤销付款",
        CarrierSettlementDocService.cancel_payment(db, settle.id, "付错账户，重新付", OP),
    )
    await db.flush()
    await db.refresh(settle)
    check("撤销付款回到已审批", int(settle.status) == 2, f"status={settle.status}")
    r = await db.execute(
        text(
            "SELECT COUNT(*) FROM biz_task t JOIN biz_carrier_recon_task_link l "
            "ON l.task_id = t.id WHERE l.recon_id = :rid AND t.is_locked = 1"
        ),
        {"rid": recon.id},
    )
    n = r.scalar()
    check("撤销付款后任务解锁", n == 0, f"(仍锁定 {n} 条)")

    # 停在已审批：进项票核销接受已审批单，真正付款交给 E 的打款批次执行
    return settle


async def flow_payroll(db, self_rows, arrive):
    print("\n=== C. 司机工资单 ===")
    from app.modules.client.services.finance.driver import DriverPayrollService

    if not self_rows:
        print("  [SKIP] 库里没有自有车任务，跳过工资单流程")
        return None

    driver_id = self_rows[0][1]
    task_ids = [t for t, _ in self_rows]

    payroll = await step(
        "建工资单（周期 + 任务提成，单价 300）",
        DriverPayrollService.create_from_candidates(
            db,
            driver_id=driver_id,
            period_start=arrive - timedelta(days=30),
            period_end=arrive + timedelta(days=1),
            task_ids=task_ids,
            unit_price=Decimal("300.00"),
            operator_id=OP,
        ),
    )
    if payroll is None:
        return None
    await db.flush()
    check("工资单初始为草稿", int(payroll.status) == 0, f"status={payroll.status}")

    await step(
        "加应发项：底薪 5000",
        DriverPayrollService.add_item(
            db, payroll.id, item_type="base_salary", amount=Decimal("5000.00"),
            item_name="底薪", category=1, operator_id=OP,
        ),
    )
    await step(
        "加扣减项：社保 800",
        DriverPayrollService.add_item(
            db, payroll.id, item_type="social_insurance", amount=Decimal("800.00"),
            item_name="社保个人部分", category=2, operator_id=OP,
        ),
    )
    await step(
        "加抵账项：油气款 1200",
        DriverPayrollService.add_item(
            db, payroll.id, item_type="fuel_offset", amount=Decimal("1200.00"),
            item_name="油气款抵账", category=3, operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(payroll)
    items = await DriverPayrollService.list_items(db, payroll.id)
    types = {x.item_type for x in items}
    check("三类工资项都已入库",
          {"base_salary", "social_insurance", "fuel_offset"} <= types,
          f"(工资项 {len(items)} 条：{sorted(types)})")

    gross = Decimal(str(payroll.gross_amount or 0))
    deduct = Decimal(str(payroll.total_deduction_amount or 0))
    offset = Decimal(str(payroll.total_prepaid_offset_amount or 0))
    net = Decimal(str(payroll.net_amount or 0))
    check("实发 = 应发 - 扣减 - 抵账", net == gross - deduct - offset,
          f"{gross} - {deduct} - {offset} = {net}")

    payslip = await step("生成工资条", DriverPayrollService.payslip(db, payroll.id))
    check(
        "工资条含应发 / 扣减 / 抵账三段",
        bool(payslip)
        and {"additions", "deductions", "offsets"} <= set(payslip or {})
        and len(payslip["additions"]) >= 1
        and len(payslip["deductions"]) >= 1,
        f"应发 {len((payslip or {}).get('additions', []))} 项 / "
        f"扣减 {len((payslip or {}).get('deductions', []))} 项 / "
        f"抵账 {len((payslip or {}).get('offsets', []))} 项",
    )

    r = await db.execute(
        text("SELECT COUNT(*) FROM biz_task WHERE id IN :ids AND is_payroll_bound = 1"),
        {"ids": tuple(task_ids)},
    )
    n = r.scalar()
    check("任务已打发薪挂接标记", n == len(task_ids), f"(标记 {n} 条)")

    await step("提交工资单", DriverPayrollService.submit(db, payroll.id, OP))
    await db.flush()
    await step("审批工资单", DriverPayrollService.approve(db, payroll.id, OP))
    await db.flush()
    accounts = await DriverPayrollService.list_accounts(db, driver_id)
    await step(
        "发放登记",
        DriverPayrollService.pay(
            db, payroll.id, actual_amount=net, paid_at=datetime.now(), pay_method=1,
            account_id=(accounts[0]["accountId"] if accounts else None), operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(payroll)
    check("发放后状态为已发放", int(payroll.status) == 3, f"status={payroll.status}")
    r = await db.execute(
        text("SELECT COUNT(*) FROM biz_task WHERE id IN :ids AND payroll_settled = 1"),
        {"ids": tuple(task_ids)},
    )
    n = r.scalar()
    check("任务已标记发薪完成", n == len(task_ids), f"(标记 {n} 条)")
    return payroll


async def flow_vendor_invoice(db, settle):
    print("\n=== D. 进项发票 ===")
    from app.modules.client.services.finance.invoice import VendorInvoiceService

    total = Decimal(str(settle.planned_amount))
    # 票面三项任填两项即可（文档 11 §7），这里给含税 + 税额，让服务反推不含税
    tax = (total / (1 + Decimal("0.09"))* Decimal("0.09")).quantize(Decimal("0.01"))
    inv = await step(
        "登记进项票（含税 + 税额，税率 9%）",
        VendorInvoiceService.register(
            db,
            invoice_no="04412345",
            invoice_code="044001900111",
            amount_incl_tax=total,
            tax_amount=tax,
            tax_rate=Decimal("9"),
            invoice_date=date.today(),
            vendor_type=1,
            vendor_id=100,
            seller_title="上海德信货运服务部",
            buyer_entity_id=1,
            operator_id=OP,
        ),
    )
    if inv is None:
        return None
    await db.flush()
    check(
        "不含税 + 税额 = 含税额",
        Decimal(str(inv.amount_excl_tax)) + Decimal(str(inv.tax_amount))
        == Decimal(str(inv.amount_incl_tax)),
        f"{inv.amount_excl_tax} + {inv.tax_amount} = {inv.amount_incl_tax}",
    )

    await expect_biz(
        "同票号 + 票代重复登记被拦截",
        VendorInvoiceService.register(
            db, invoice_no="04412345", invoice_code="044001900111",
            amount_incl_tax=Decimal("109.00"), tax_amount=Decimal("9.00"),
            tax_rate=Decimal("9"), vendor_id=100, operator_id=OP,
        ),
    )

    await expect_biz(
        "核销额超过票面被拦截",
        VendorInvoiceService.match(
            db, inv.id,
            [{"settleId": settle.id, "appliedAmount": total + Decimal("1000.00")}],
            operator_id=OP,
        ),
    )

    links = await step(
        "票款核销到承运商结算单",
        VendorInvoiceService.match(
            db, inv.id, [{"settleId": settle.id, "appliedAmount": total}], operator_id=OP
        ),
    )
    await db.flush()
    await db.refresh(inv)
    check("核销后票面已核销额 = 票面额", Decimal(str(inv.settled_amount)) == total,
          f"settled={inv.settled_amount}")
    check("待核销额归零", Decimal(str(inv.unsettled_amount or 0)) == 0,
          f"unsettled={inv.unsettled_amount}")
    await db.refresh(settle)
    check("结算单被标记票款已齐", int(settle.invoice_matched or 0) == 1,
          f"invoice_matched={settle.invoice_matched}")

    if links:
        await step("撤销核销", VendorInvoiceService.unmatch(db, inv.id, links[0].id, operator_id=OP))
        await db.flush()
        await db.refresh(inv)
        check("撤销后已核销额归零", Decimal(str(inv.settled_amount or 0)) == 0,
              f"settled={inv.settled_amount}")
        await db.refresh(settle)
        check("结算单票款标记回退", int(settle.invoice_matched or 0) == 0,
              f"invoice_matched={settle.invoice_matched}")

    await step("作废进项票", VendorInvoiceService.void(db, inv.id, "承运商开错税率，退票重开", OP))
    await db.flush()
    await db.refresh(inv)
    check("作废后状态为已作废", int(inv.status) == 9, f"status={inv.status}")
    return inv


async def flow_cashier(db, settle, payroll):
    print("\n=== E. 银行账户与打款批次 ===")
    from app.modules.client.services.finance.cashier import (
        BankAccountService,
        CashierService,
        PaymentBatchService,
    )

    acct = await step(
        "建银行账户（初始余额 100 万）",
        BankAccountService.create(
            db, enterprise_id=1, account_name="北京朵灵-基本户",
            account_no="110900200100999", bank_name="工商银行",
            account_type=1, usage_scope=3, balance=Decimal("1000000.00"),
            is_default_pay=1, operator_id=OP,
        ),
    )
    if acct is None:
        return None
    await db.flush()

    await expect_biz(
        "同账号重复建账被拦截",
        BankAccountService.create(
            db, enterprise_id=1, account_name="重复户", account_no="110900200100999",
            operator_id=OP,
        ),
    )

    await step(
        "余额校准（必填原因）",
        BankAccountService.calibrate(
            db, acct.id, balance=Decimal("980000.00"), reason="与银行对账差 2 万，按银行为准", operator_id=OP
        ),
    )
    await db.flush()
    await db.refresh(acct)
    check("校准后余额已改写", Decimal(str(acct.balance)) == Decimal("980000.00"),
          f"balance={acct.balance}")
    events = await BankAccountService.list_events(db, acct.id)
    check("校准已留痕（事件 27）", any(int(e.event_type) == 27 for e in events),
          f"(事件 {len(events)} 条)")

    cands = await PaymentBatchService.list_candidates(db, limit=50)
    kinds = {c.get("docKind") for c in cands}
    check("候选池能捞到已审批应付单", len(cands) >= 1, f"(候选 {len(cands)} 条，类型 {kinds})")
    if not cands:
        return acct

    docs = [{"docKind": c["docKind"], "docId": c["docId"], "amount": c["amount"]}
            for c in cands[:2]]
    batch = await step(
        "建打款批次",
        PaymentBatchService.create_batch(
            db, docs=docs, bank_account_id=acct.id, enterprise_id=1,
            plan_pay_date=date.today(), operator_id=OP,
        ),
    )
    if batch is None:
        return acct
    await db.flush()
    check("批次笔数与明细一致", int(batch.item_count) == len(docs), f"item_count={batch.item_count}")

    await step("提交批次", PaymentBatchService.submit(db, batch.id, OP))
    await db.flush()
    await step("审批批次", PaymentBatchService.approve(db, batch.id, OP))
    await db.flush()

    items = await PaymentBatchService.list_items(db, batch.id)
    # 让承运商结算单那笔成功（后面要验任务被锁），另一类单据那笔走失败分支
    results = []
    for it in items:
        if len(items) > 1 and it.doc_kind != "carrier_settle":
            results.append({"itemId": it.id, "success": False, "failReason": "收款账号不存在，银行退回"})
        else:
            results.append({"itemId": it.id, "success": True})
    await step("执行批次（首笔失败、其余成功）", PaymentBatchService.execute(
        db, batch.id, results, paid_at=datetime.now(), operator_id=OP,
    ))
    await db.flush()
    await db.refresh(batch)
    if len(items) > 1:
        check("批次进部分失败", int(batch.status) == 6, f"status={batch.status}")
        check("失败笔计数正确", int(batch.fail_count) == 1, f"fail_count={batch.fail_count}")
        r = await db.execute(
            text(
                "SELECT COUNT(*) FROM biz_finance_doc_event "
                "WHERE doc_kind = 'payment_batch' AND doc_id = :i AND event_type = 28"
            ),
            {"i": batch.id},
        )
        n = r.scalar()
        check("失败笔已记事件 28", n >= 1, f"(事件 {n} 条)")
    else:
        check("单笔全成功时批次转已支付", int(batch.status) == 3, f"status={batch.status}")

    if settle is not None:
        await db.refresh(settle)
        check("批次成功笔把结算单推到已支付", int(settle.status) == 3,
              f"status={settle.status}")
        r = await db.execute(
            text(
                "SELECT COUNT(*) FROM biz_task t JOIN biz_carrier_recon_task_link l "
                "ON l.task_id = t.id AND l.is_deleted = 0 "
                "JOIN biz_carrier_settle_recon_link s ON s.recon_id = l.recon_id "
                "AND s.is_deleted = 0 AND s.settle_id = :s WHERE t.is_locked = 1"
            ),
            {"s": settle.id},
        )
        n = r.scalar()
        check("批次付款后任务被锁定", n and n > 0, f"(锁定 {n} 条)")
        r = await db.execute(
            text(
                "SELECT balance FROM biz_bank_account WHERE id = :i"
            ),
            {"i": acct.id},
        )
        bal = Decimal(str(r.scalar()))
        check("付款已扣减银行账户余额", bal < Decimal("980000.00"), f"balance={bal}")

    ov = await step("出纳台概览", CashierService.overview(db))
    check("概览含账面余额", bool(ov), f"keys={sorted((ov or {}).keys())[:6]}")
    flow = await step("资金流水", CashierService.flow_list(db, page=1, page_size=10))
    rows, total, totals = flow if flow else ([], 0, {})
    check("流水能查到刚才的付款",
          any(x.get("docKind") == "carrier_settle" for x in rows),
          f"(流水 {total} 行，合计 {totals})")
    return acct


async def flow_customer_invoice(db):
    print("\n=== F. 销项发票 ===")
    from app.modules.client.services.finance.customer import (
        CustomerInvoiceService,
        CustomerSettlementService,
    )

    settles, _ = await CustomerSettlementService.page_list(db, page=1, page_size=5)
    if not settles:
        print("  [SKIP] 没有客户结算单，跳过销项票流程")
        return None
    cust_id = settles[0].customer_id
    cands = await CustomerInvoiceService.list_candidates(db, customer_id=cust_id)
    check("可开票结算单进入候选", len(cands) >= 1, f"(候选 {len(cands)} 条)")
    if not cands:
        return None

    amt = Decimal(str(cands[0]["availableAmount"]))
    inv = await step(
        "建开票申请（关联 1 张结算单）",
        CustomerInvoiceService.create_from_settles(
            db,
            customer_id=cust_id,
            allocations=[{"settleId": cands[0]["settleId"], "amount": amt}],
            invoice_type=2,
            seller_entity_id=1,
            tax_rate=Decimal("9"),
            operator_id=OP,
        ),
    )
    if inv is None:
        return None
    await db.flush()
    check("票面含税额 = 关联金额", Decimal(str(inv.amount_incl_tax)) == amt,
          f"{inv.amount_incl_tax} vs {amt}")

    await expect_biz(
        "草稿态不能直接登记开票",
        CustomerInvoiceService.issue(db, inv.id, invoice_no="12345678", operator_id=OP),
    )
    await step("提交开票申请", CustomerInvoiceService.submit_apply(db, inv.id, OP))
    await db.flush()
    await step(
        "登记开票",
        CustomerInvoiceService.issue(
            db, inv.id, invoice_no="12345678", invoice_code="011002000311",
            invoice_date=date.today(), operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(inv)
    check("开票后状态为已开票", int(inv.status) == 3, f"status={inv.status}")

    r = await db.execute(
        text("SELECT is_locked FROM biz_customer_settlement WHERE id = :i"),
        {"i": cands[0]["settleId"]},
    )
    check("已开票的结算单被锁定", int(r.scalar() or 0) == 1)

    orig, red = await step("红冲（生成红字票）", CustomerInvoiceService.red_flush(
        db, inv.id, "客户名称开错，红冲重开", OP
    )) or (None, None)
    await db.flush()
    if red is not None:
        check("红字票金额为负", Decimal(str(red.amount_incl_tax)) < 0,
              f"red={red.amount_incl_tax}")
        check("红字票回指原票", int(red.red_flush_from_id or 0) == inv.id,
              f"from={red.red_flush_from_id}")
        await db.refresh(inv)
        check("原票转已作废", int(inv.status) == 9, f"status={inv.status}")
    return inv


async def audit_events(db):
    print("\n=== H. 事件留痕汇总（本次事务内新增）===")
    r = await db.execute(
        text(
            "SELECT doc_kind, COUNT(*), COUNT(DISTINCT event_type) "
            "FROM biz_finance_doc_event GROUP BY doc_kind ORDER BY 2 DESC"
        )
    )
    rows = [tuple(x) for x in r.fetchall()]
    for kind, c, t in rows:
        print(f"  {kind:<20} {c:>4} 条，{t} 种类型")
    r = await db.execute(
        text(
            "SELECT event_type, COUNT(*) FROM biz_finance_doc_event "
            "GROUP BY event_type ORDER BY event_type"
        )
    )
    used = [(t, c) for t, c in r.fetchall()]
    print("  事件类型分布：" + ", ".join(f"{t}({c})" for t, c in used))
    check("已覆盖 12 种以上事件类型", len(used) >= 12, f"(实际 {len(used)} 种)")


async def main():
    db_manager._get_or_create_tenant_engine(TENANT)
    factory = db_manager._tenant_session_factories[TENANT]
    async with factory() as db:
        try:
            carrier_tasks, self_rows, arrive = await prepare(db)
            recon = await flow_carrier(db, carrier_tasks, arrive)
            settle = await flow_carrier_settle(db, recon) if recon else None
            payroll = await flow_payroll(db, self_rows, arrive)
            if settle is not None:
                await flow_vendor_invoice(db, settle)
                await flow_cashier(db, settle, payroll)
            await flow_customer_invoice(db)
            await audit_events(db)
        finally:
            await db.rollback()
            print("\n（事务已回滚，未落任何数据）")
    await db_manager.close_all()
    print("=" * 56)
    print(f"通过 {ok} 项，失败 {bad} 项")
    if fails:
        print("失败明细：")
        for f in fails:
            print("  -", f)
    return 1 if bad else 0


sys.exit(asyncio.run(main()))
