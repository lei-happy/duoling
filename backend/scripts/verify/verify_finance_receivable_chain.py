"""客户侧应收链路写验证（文档 02 客户侧-对账与结算与发票）

覆盖：
  A 客户对账 → 只改调整额不掉分位残差 → 改数量单价按乘积重算 → 确认 → 回签 → 运单锁定
  B 客户结算 → 关联对账 → 提交 → 审批
  C 收款单 → 认领核销 → 已收妥拦截 → 撤销收款 → 撤销核销
  D 账龄与信用：账龄分桶可查、逾期口径可单独筛

重点回归 ``adjust_line`` 的基数口径：运费 1000 元 / 3 台派生单价 333.33，
只改调整额时不得回落到乘积（否则每次调整都会凭空少掉 0.01）。

安全性：脚本自行把少量运单改成可对账状态作为候选池，全部写操作在单个事务内
执行，跑完即 ``rollback``，不污染租户库。

用法：
    python scripts/verify/verify_finance_receivable_chain.py [tenant_code]

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

from app.common.exceptions import BizException
from app.core.database import db_manager
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
    global ok, bad
    try:
        r = await coro
        print(f"  [OK]   {name}")
        ok += 1
        return r
    except Exception as e:  # noqa: BLE001
        print(f"  [FAIL] {name}: {type(e).__name__}: {e}")
        bad += 1
        fails.append(f"{name}: {e}")
        traceback.print_exc()
        return None


async def expect_biz(name, coro, keyword=None):
    global ok, bad
    try:
        await coro
    except BizException as e:
        if keyword and keyword not in str(e):
            print(f"  [FAIL] {name}: 拦截文案不含「{keyword}」，实际：{e}")
            bad += 1
            fails.append(f"{name}: 文案不符")
            return
        print(f"  [OK]   {name}（已拦截：{e}）")
        ok += 1
        return
    except Exception as e:  # noqa: BLE001
        print(f"  [FAIL] {name}: 期望 BizException，实际 {type(e).__name__}: {e}")
        bad += 1
        fails.append(f"{name}: 异常类型不符")
        return
    print(f"  [FAIL] {name}: 未拦截，动作被放过")
    bad += 1
    fails.append(f"{name}: 未拦截")


async def prepare(db):
    """挑 3 张已签收运单，运费凑成 1000 / 3 台（单价除不尽，专治分位残差）。"""
    print("\n=== 0. 准备候选数据（事务内，最后回滚）===")
    signed = datetime.now() - timedelta(days=5)
    # 候选池按「已交车挂接明细」的 signed_at 过滤周期，故只取有该明细的运单
    r = await db.execute(
        text(
            "SELECT w.id, w.customer_id FROM biz_waybill w "
            "JOIN biz_task_waybill_item i ON i.waybill_id = w.id "
            "AND i.is_deleted = 0 AND i.status = 3 "
            "WHERE w.is_deleted = 0 AND w.customer_id IS NOT NULL "
            "GROUP BY w.id, w.customer_id ORDER BY w.customer_id, w.id LIMIT 3"
        )
    )
    rows = [tuple(x) for x in r.fetchall()]
    if not rows:
        return None, [], signed
    customer_id = rows[0][1]
    rows = [x for x in rows if x[1] == customer_id]
    ids = [x[0] for x in rows]
    await db.execute(
        text(
            "UPDATE biz_waybill SET status = 5, is_locked = 0, is_recon_bound = 0, "
            "freight_amount = 1000.00, quantity = 3 WHERE id IN :ids"
        ),
        {"ids": tuple(ids)},
    )
    # 已交车台数取挂接明细 quantity 合计：置 3 台，配 1000 元运费即得除不尽的单价
    await db.execute(
        text(
            "UPDATE biz_task_waybill_item SET signed_at = :t, quantity = 3 "
            "WHERE waybill_id IN :ids AND status = 3"
        ).bindparams(**{"t": signed}),
        {"ids": tuple(ids)},
    )
    await db.flush()
    print(f"  客户 {customer_id} 的运单候选：{ids}（各 1000 元 / 3 台）")
    return customer_id, ids, signed


async def flow_recon(db, customer_id, waybill_ids, signed):
    print("\n=== A. 客户对账单 ===")
    from app.modules.client.services.finance.customer import CustomerReconService

    cands = await CustomerReconService.list_candidates(db, customer_id=customer_id)
    check("候选池能捞到已签收运单", len(cands) >= len(waybill_ids),
          f"(候选 {len(cands)} 条)")

    recon = await step(
        "建对账单（2 张运单）",
        CustomerReconService.create_from_candidates(
            db,
            customer_id=customer_id,
            period_start=signed - timedelta(days=30),
            period_end=signed + timedelta(days=1),
            waybill_ids=waybill_ids[:2],
            operator_id=OP,
        ),
    )
    if recon is None:
        return None
    await db.flush()
    check("对账单初始为草稿", int(recon.status) == 0, f"status={recon.status}")
    check("应收合计按运单运费汇总",
          Decimal(str(recon.planned_amount)) == Decimal("2000.00"),
          f"planned={recon.planned_amount}")

    if len(waybill_ids) > 2:
        await step(
            "追加第 3 张运单",
            CustomerReconService.add_waybills(
                db, recon.id, [waybill_ids[2]], operator_id=OP,
            ),
        )
        await db.flush()
        await db.refresh(recon)

    lines = await CustomerReconService.list_lines(db, recon.id)
    check("行数与运单数一致", len(lines) == len(waybill_ids),
          f"(行 {len(lines)} 条)")
    check("派生单价除不尽（用于验残差）",
          Decimal(str(lines[0].unit_price)) == Decimal("333.33"),
          f"unit_price={lines[0].unit_price}")

    base = Decimal(str(lines[0].amount))
    await step(
        "只改调整额 -50（不动数量单价）",
        CustomerReconService.adjust_line(
            db, recon.id, lines[0].id,
            adjust_amount=Decimal("-50.00"), adjust_reason="货损扣款",
            operator_id=OP,
        ),
    )
    await db.flush()
    lines = await CustomerReconService.list_lines(db, recon.id)
    check(
        "行金额 = 原运费 - 50，未回落到乘积",
        Decimal(str(lines[0].amount)) == base - Decimal("50.00"),
        f"{base} → {lines[0].amount}（乘积口径会是 949.99）",
    )

    await step(
        "改数量为 2 台（此时才按乘积重算）",
        CustomerReconService.adjust_line(
            db, recon.id, lines[0].id, quantity=Decimal("2"), operator_id=OP,
        ),
    )
    await db.flush()
    lines = await CustomerReconService.list_lines(db, recon.id)
    check(
        "改数量后按 2×333.33-50 重算",
        Decimal(str(lines[0].amount)) == Decimal("616.66"),
        f"amount={lines[0].amount}",
    )

    await expect_biz(
        "有调整额但无原因被拦截",
        CustomerReconService.adjust_line(
            db, recon.id, lines[1].id, adjust_amount=Decimal("-30.00"),
            operator_id=OP,
        ),
        keyword="原因",
    )

    await step("确认对账单", CustomerReconService.confirm(db, recon.id, operator_id=OP))
    await db.flush()
    await db.refresh(recon)
    check("确认后状态转已确认", int(recon.status) == 2, f"status={recon.status}")

    r = await db.execute(
        text(
            "SELECT COUNT(*) FROM biz_waybill WHERE id IN :ids AND is_recon_bound = 1"
        ),
        {"ids": tuple(waybill_ids)},
    )
    n = r.scalar()
    check("运单已打对账挂接标记", n == len(waybill_ids), f"(标记 {n} 条)")

    await step(
        "登记客户回签",
        CustomerReconService.record_customer_sign(
            db, recon.id, signer_name="汇通-李经理",
            signed_at=datetime.now(), operator_id=OP,
        ),
    )
    await db.flush()
    return recon


async def flow_settle(db, customer_id, recon):
    print("\n=== B. 客户结算单 ===")
    from app.modules.client.services.finance.customer import CustomerSettlementService

    cands = await CustomerSettlementService.list_recon_candidates(
        db, customer_id=customer_id,
    )
    mine = next((c for c in cands if int(c["reconId"]) == recon.id), None)
    check("已确认对账单进入结算候选", mine is not None, f"(候选 {len(cands)} 条)")
    if mine is None:
        return None

    amount = Decimal(str(mine["availableAmount"]))
    settle = await step(
        "建结算单（全额关联）",
        CustomerSettlementService.create_from_recons(
            db,
            customer_id=customer_id,
            recons=[{"reconId": recon.id, "amount": amount}],
            due_date=date.today() + timedelta(days=30),
            invoice_required=1,
            operator_id=OP,
        ),
    )
    if settle is None:
        return None
    await db.flush()
    check("结算金额 = 对账可结额",
          Decimal(str(settle.planned_amount)) == amount,
          f"{settle.planned_amount} vs {amount}")

    await step("提交结算单", CustomerSettlementService.submit(db, settle.id, OP))
    await db.flush()
    await step("审批结算单", CustomerSettlementService.approve(db, settle.id, OP))
    await db.flush()
    await db.refresh(settle)
    check("审批后状态为已审批", int(settle.status) == 2, f"status={settle.status}")
    return settle


async def flow_receipt(db, customer_id, settle, waybill_ids):
    print("\n=== C. 收款单与核销 ===")
    from app.modules.client.services.finance.customer import ReceiptVoucherService

    total = Decimal(str(settle.planned_amount))
    receipt = await step(
        "登记收款到账（全额）",
        ReceiptVoucherService.create(
            db, amount=total, received_at=datetime.now(), receive_method=1,
            customer_id=customer_id, payer_name="汇通大宗股份有限公司",
            bank_serial_no="SN20260814001", operator_id=OP,
        ),
    )
    if receipt is None:
        return None
    await db.flush()

    cands = await ReceiptVoucherService.list_claim_candidates(
        db, receipt_id=receipt.id,
    )
    check("待核销结算单进入候选", any(
        int(c.get("settleId", 0)) == settle.id for c in cands
    ), f"(候选 {len(cands)} 条)")

    await expect_biz(
        "核销额超过收款额被拦截",
        ReceiptVoucherService.claim(
            db, receipt.id,
            [{"settleId": settle.id, "amount": total + Decimal("100.00")}],
            operator_id=OP,
        ),
    )

    await step(
        "认领核销到结算单（满额）",
        ReceiptVoucherService.claim(
            db, receipt.id,
            [{"settleId": settle.id, "amount": total}],
            operator_id=OP,
        ),
    )
    await db.flush()
    await db.refresh(receipt)
    await db.refresh(settle)
    check("收款单转已核销", int(receipt.status) == 5, f"status={receipt.status}")
    check("满额核销驱动结算单转已收款", int(settle.status) == 3,
          f"status={settle.status}")
    r = await db.execute(
        text("SELECT COUNT(*) FROM biz_waybill WHERE id IN :ids AND is_locked = 1"),
        {"ids": tuple(waybill_ids)},
    )
    n = r.scalar()
    check("收款后运单被锁定", n == len(waybill_ids), f"(锁定 {n} 条)")

    links = await ReceiptVoucherService.list_links(db, receipt.id)
    if links:
        from app.modules.client.services.finance.customer import (
            CustomerSettlementService,
        )

        await expect_biz(
            "已收妥时直接撤销核销被拦截",
            ReceiptVoucherService.unclaim(
                db, receipt.id, int(links[0].settle_id), operator_id=OP,
            ),
            keyword="先在结算单上撤销收款",
        )
        await step(
            "先在结算单上撤销收款",
            CustomerSettlementService.cancel_receive(
                db, settle.id, "客户退款，收款作废重录", OP,
            ),
        )
        await db.flush()
        await db.refresh(settle)
        check("撤销收款后结算单退回已审批", int(settle.status) == 2,
              f"status={settle.status}")
        r = await db.execute(
            text("SELECT COUNT(*) FROM biz_waybill WHERE id IN :ids AND is_locked = 1"),
            {"ids": tuple(waybill_ids)},
        )
        n = r.scalar()
        check("撤销收款后运单解锁", n == 0, f"(仍锁定 {n} 条)")

        await step(
            "撤销核销",
            ReceiptVoucherService.unclaim(
                db, receipt.id, int(links[0].settle_id), operator_id=OP,
            ),
        )
        await db.flush()
        await db.refresh(receipt)
        check("撤销核销后收款单退回待认领",
              int(receipt.status) in (0, 3), f"status={receipt.status}")
        check("撤销核销后已核销额归零",
              Decimal(str(receipt.settled_amount or 0)) == 0,
              f"settled={receipt.settled_amount}")
    return receipt


async def flow_aging(db, customer_id):
    print("\n=== D. 账龄与信用 ===")
    from app.modules.client.services.finance.customer import AgingService

    page = await step("账龄分页", AgingService.customer_page(db, page=1, page_size=10))
    check("账龄返回分桶与合计", bool(page) and "list" in (page or {}),
          f"keys={sorted((page or {}).keys())[:6]}")
    overdue = await step(
        "只看逾期", AgingService.customer_page(db, page=1, page_size=10, only_overdue=True),
    )
    check("逾期口径可单独筛", overdue is not None,
          f"(逾期 {len((overdue or {}).get('list', []))} 户)")


async def main():
    db_manager._get_or_create_tenant_engine(TENANT)
    factory = db_manager._tenant_session_factories[TENANT]
    async with factory() as db:
        try:
            customer_id, waybill_ids, signed = await prepare(db)
            if not waybill_ids:
                print("  [SKIP] 库里没有可用运单，无法跑客户侧流程")
            else:
                recon = await flow_recon(db, customer_id, waybill_ids, signed)
                settle = await flow_settle(db, customer_id, recon) if recon else None
                if settle:
                    await flow_receipt(db, customer_id, settle, waybill_ids)
                await flow_aging(db, customer_id)
        finally:
            await db.rollback()
            print("\n（事务已回滚，未落任何数据）")
    await db_manager.close_all()
    print("=" * 56)
    print(f"通过 {ok} 项，失败 {bad} 项")
    if fails:
        print("失败明细：")
        for x in fails:
            print(f"  - {x}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
