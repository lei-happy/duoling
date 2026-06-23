"""任务单全链路状态机验证脚本（正向 + 逆向，端到端）

针对开发租户库，用真实 Service 串起《02.运单与任务单状态机联动设计.md》
§10 的关键用例，逐步断言 Task / Item / Waybill 三态联动与
``cargo.allocated_quantity`` 占用/释放/回滚，最后输出一份对照设计文档
§10.1（正向）/ §10.2（逆向）的用例勾选清单，作为回归基线。

安全性：
- 默认 **dry-run**：所有写操作在单个事务内执行，跑完即 ``rollback``，
  不会污染租户库；加 ``--commit`` 才真正落库（一般不需要）。
- 所有 fixtures（运单 + 货物明细）由脚本自建，台数干净、互不干扰。

用法：
    # 干跑（推荐）
    python scripts/verify/verify_task_state_chain.py <tenant_code>

    # 真正写库
    python scripts/verify/verify_task_state_chain.py <tenant_code> --commit

退出码：全部用例通过 0；存在失败 1。
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager

# 引入全部租户模型，确保 relationship/表元数据可用
from app.modules.client.models import *  # noqa: F401, F403
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.task.task import TaskCarrierInfo, TaskCreate, TaskStatusUpdate
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemIn,
    TaskWaybillItemStatusUpdate,
)
from app.modules.client.services.task.task_service import TaskService
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)


# =====================================================================
# 结果记录器
# =====================================================================
@dataclass
class Recorder:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    lines: List[Tuple[str, str, str]] = field(default_factory=list)  # (mark, case, detail)

    def ok(self, case: str, detail: str = "") -> None:
        self.passed += 1
        self.lines.append(("PASS", case, detail))
        print(f"  [PASS] {case}  {detail}")

    def fail(self, case: str, detail: str = "") -> None:
        self.failed += 1
        self.lines.append(("FAIL", case, detail))
        print(f"  [FAIL] {case}  {detail}")

    def skip(self, case: str, detail: str = "") -> None:
        self.skipped += 1
        self.lines.append(("SKIP", case, detail))
        print(f"  [SKIP] {case}  {detail}")

    def expect(self, case: str, actual, expected) -> None:
        if actual == expected:
            self.ok(case, f"= {actual}")
        else:
            self.fail(case, f"期望 {expected}，实际 {actual}")


# =====================================================================
# Fixtures
# =====================================================================
_UNIQ = datetime.now().strftime("%Y%m%d%H%M%S")
_seq = 0


def _next_no(prefix: str) -> str:
    global _seq
    _seq += 1
    return f"{prefix}-VERIFY-{_UNIQ}-{_seq:03d}"


async def _make_waybill_with_cargo(
    db: AsyncSession, qty: int
) -> Tuple[Waybill, WaybillCargo]:
    """新建一张「待调度(1)」运单 + 单条货物明细，返回 (waybill, cargo)。"""
    wb = Waybill(
        waybill_no=_next_no("WB"),
        customer_name="状态机验证客户",
        origin="上海",
        destination="北京",
        vehicle_brand="测试品牌",
        vehicle_model="测试车型",
        quantity=qty,
        status=1,  # 待调度（可挂接）
    )
    db.add(wb)
    await db.flush()
    cargo = WaybillCargo(
        waybill_id=wb.id,
        sort_order=0,
        vehicle_brand="测试品牌",
        vehicle_model="测试车型",
        quantity=qty,
        allocated_quantity=0,
    )
    db.add(cargo)
    await db.flush()
    return wb, cargo


def _self_owned_carrier() -> TaskCarrierInfo:
    return TaskCarrierInfo(
        carrierType=1,
        mainDriverName="验证司机",
        mainDriverPhone="13800000000",
        plateNumber=f"沪A{_UNIQ[-5:]}",
    )


async def _create_dispatched_task(
    db: AsyncSession, qty: int
) -> Tuple[Task, Waybill, WaybillCargo]:
    """建一张已派车(1) 任务，挂接 1 张运单（qty 台）。"""
    wb, cargo = await _make_waybill_with_cargo(db, qty)
    payload = TaskCreate(
        taskName="状态机全链路验证",
        carrier=_self_owned_carrier(),
        segments=[],
        waybillItems=[
            TaskWaybillItemIn(waybillId=wb.id, waybillCargoId=cargo.id, quantity=qty)
        ],
    )
    task = await TaskService.create_task(db, payload)
    return task, wb, cargo


# =====================================================================
# 取数 / 断言辅助
# =====================================================================
async def _task_status(db: AsyncSession, task_id: int) -> int:
    r = await db.execute(select(Task.status).where(Task.id == task_id))
    return int(r.scalar_one())


async def _waybill_status(db: AsyncSession, wb_id: int) -> int:
    r = await db.execute(select(Waybill.status).where(Waybill.id == wb_id))
    return int(r.scalar_one())


async def _cargo_allocated(db: AsyncSession, cargo_id: int) -> int:
    r = await db.execute(
        select(WaybillCargo.allocated_quantity).where(WaybillCargo.id == cargo_id)
    )
    return int(r.scalar_one() or 0)


async def _item_statuses(db: AsyncSession, task_id: int) -> List[int]:
    items = await TaskWaybillItemService.list_items_of_task(db, task_id)
    return [int(it.status) for it in items]


async def _drive_items(
    db: AsyncSession, task_id: int, target: int, *, when: Optional[datetime] = None
) -> None:
    """把任务下所有 active item 推进到 target（装/卸/签/撤），逐条走 service。"""
    items = await TaskWaybillItemService.list_items_of_task(db, task_id)
    when = when or datetime.now()
    for it in items:
        if int(it.status) == 9 or int(it.status) == target:
            continue
        await TaskWaybillItemService.update_item_status(
            db,
            it.id,
            TaskWaybillItemStatusUpdate(
                status=target,
                loadedAt=when if target == 1 else None,
                unloadedAt=when if target == 2 else None,
                signedAt=when if target == 3 else None,
                remark="状态机验证",
            ),
        )


# =====================================================================
# 场景 A：正向全链路 + 撤销签收(5→4) + 再签收
# =====================================================================
async def scenario_forward_and_unsign(db: AsyncSession, rec: Recorder) -> None:
    print("\n[场景 A] 正向全链路 → 撤销签收(5→4) → 再签收（设计文档 §10.1 / §4.5.2）")
    qty = 3
    task, wb, cargo = await _create_dispatched_task(db, qty)
    tid, wid, cid = task.id, wb.id, cargo.id

    rec.expect("A0 建单已派车 task=1", await _task_status(db, tid), 1)
    rec.expect("A0 挂接占用 allocated=qty", await _cargo_allocated(db, cid), qty)

    # 装车：item 0→1，聚合 task 1→2
    await _drive_items(db, tid, 1)
    rec.expect("A1 装车后 task=2", await _task_status(db, tid), 2)
    rec.expect("A1 运单升档 waybill=3 运输中", await _waybill_status(db, wid), 3)

    # 出发：2→3
    await TaskService.update_status(db, tid, TaskStatusUpdate(status=3))
    rec.expect("A2 出发后 task=3 在途", await _task_status(db, tid), 3)

    # 卸车：item 1→2，聚合 task 3→4
    await _drive_items(db, tid, 2)
    rec.expect("A3 卸车后 task=4 已到达", await _task_status(db, tid), 4)
    rec.expect("A3 运单 waybill=4 待签收", await _waybill_status(db, wid), 4)

    # 签收：item 2→3，聚合 task 4→5；签收为完结态，释放占用
    await _drive_items(db, tid, 3)
    rec.expect("A4 全签收后 task=5 已签收", await _task_status(db, tid), 5)
    rec.expect("A4 运单 waybill=5 已签收", await _waybill_status(db, wid), 5)
    rec.expect("A4 完结释放 allocated=0", await _cargo_allocated(db, cid), 0)

    # 撤销签收：item 3→2，聚合 task 5→4；重新占用台数
    await _drive_items(db, tid, 2)
    rec.expect("A5 撤销签收 task 5→4", await _task_status(db, tid), 4)
    rec.expect("A5 运单回退 waybill 5→4", await _waybill_status(db, wid), 4)
    rec.expect("A5 重新占用 allocated=qty", await _cargo_allocated(db, cid), qty)

    # 再签收：item 2→3，回到 5
    await _drive_items(db, tid, 3)
    rec.expect("A6 再签收 task=5", await _task_status(db, tid), 5)
    rec.expect("A6 运单 waybill=5", await _waybill_status(db, wid), 5)

    # 关闭：5→7
    await TaskService.update_status(db, tid, TaskStatusUpdate(status=7))
    rec.expect("A7 关闭 task 5→7", await _task_status(db, tid), 7)


# =====================================================================
# 场景 B：逐级反向（撤回到达/出发/装车/派车）
# =====================================================================
async def scenario_reverse_chain(db: AsyncSession, rec: Recorder) -> None:
    print("\n[场景 B] 逐级反向：撤回到达(4→3)/出发(3→2)/装车(2→1)/派车(1→0)（§10.2 / §4.5.1）")
    qty = 2
    task, wb, cargo = await _create_dispatched_task(db, qty)
    tid, wid, cid = task.id, wb.id, cargo.id

    # 推到已到达(4)
    await _drive_items(db, tid, 1)
    await TaskService.update_status(db, tid, TaskStatusUpdate(status=3))
    await _drive_items(db, tid, 2)
    rec.expect("B0 预置到已到达 task=4", await _task_status(db, tid), 4)

    # 撤回到达 4→3：item 2→1
    await TaskService.revert_status(db, tid, 3, reason="到货确认有误（验证）")
    rec.expect("B1 撤回到达 task 4→3", await _task_status(db, tid), 3)
    rec.expect("B1 item 反向回 1 已装车", await _item_statuses(db, tid), [1] * 1)

    # 撤回出发 3→2
    await TaskService.revert_status(db, tid, 2, reason="误点出发（验证）")
    rec.expect("B2 撤回出发 task 3→2", await _task_status(db, tid), 2)

    # 撤销装车 2→1：item 1→0，未完结台数仍占用
    await TaskService.revert_status(db, tid, 1, reason="装车员误确认（验证）")
    rec.expect("B3 撤销装车 task 2→1", await _task_status(db, tid), 1)
    rec.expect("B3 item 回退 0 待装车", await _item_statuses(db, tid), [0] * 1)
    rec.expect("B3 未完结仍占用 allocated=qty", await _cargo_allocated(db, cid), qty)

    # 撤回派车 1→0
    await TaskService.revert_status(db, tid, 0, reason="承运资源变更（验证）")
    rec.expect("B4 撤回派车 task 1→0", await _task_status(db, tid), 0)
    rec.expect("B4 运单回退 waybill=2 调度中", await _waybill_status(db, wid), 2)

    # 非法反向应被拒：5→4 不允许走 revert_status（撤销签收必须走 item 级）
    try:
        await TaskService.revert_status(db, tid, 4, reason="非法路径（验证）")
        rec.fail("B5 非法 revert(0→4) 应抛异常", "未抛异常")
    except Exception as e:  # noqa: BLE001
        rec.ok("B5 非法 revert 被状态机拒绝", type(e).__name__)


# =====================================================================
# 场景 C：强制取消(3→9) 释放台数 + 撤未支付费用单
# =====================================================================
async def scenario_force_cancel(db: AsyncSession, rec: Recorder) -> None:
    print("\n[场景 C] 强制取消(在途 3→9)：释放台数 + 撤销未支付费用单（§10.2 / §4.5.3）")
    qty = 4
    task, wb, cargo = await _create_dispatched_task(db, qty)
    tid, wid, cid = task.id, wb.id, cargo.id

    # 推到在途(3)
    await _drive_items(db, tid, 1)
    await TaskService.update_status(db, tid, TaskStatusUpdate(status=3))
    rec.expect("C0 预置到在途 task=3", await _task_status(db, tid), 3)
    rec.expect("C0 在途占用 allocated=qty", await _cargo_allocated(db, cid), qty)

    # 可选：建一张未支付费用单，验证强制取消时被一并撤销
    fin_doc_id: Optional[int] = None
    try:
        from app.modules.client.services.task.task_finance_service import (
            TaskFinanceService,
        )
        from app.modules.client.schemas.task.task_finance_doc import (
            TaskFinanceDocCreate,
        )

        doc = await TaskFinanceService.create_doc(
            db,
            tid,
            TaskFinanceDocCreate(
                docType=1,
                isFinal=0,
                payeeType=1,
                payeeName="验证收款人",
                plannedAmount=100.0,
            ),
        )
        await db.flush()
        fin_doc_id = doc.id
    except Exception as e:  # noqa: BLE001
        rec.skip("C1 预置未支付费用单", f"建单失败/字段不匹配，跳过：{type(e).__name__}")

    # 强制取消 3→9
    await TaskService.force_cancel(db, tid, reason="客户临时退单（验证）")
    rec.expect("C2 强制取消 task 3→9", await _task_status(db, tid), 9)
    rec.expect("C2 item 全部置 9 已取消", set(await _item_statuses(db, tid)), {9})
    rec.expect("C2 释放占用 allocated=0", await _cargo_allocated(db, cid), 0)
    # 运单下无活跃挂接 → 回退到待调度(1)
    rec.expect("C2 运单回退 waybill=1 待调度", await _waybill_status(db, wid), 1)

    if fin_doc_id is not None:
        from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc

        r = await db.execute(
            select(TaskFinanceDoc.status).where(TaskFinanceDoc.id == fin_doc_id)
        )
        rec.expect("C3 未支付费用单被撤销 status=4", int(r.scalar_one()), 4)


# =====================================================================
# 主流程
# =====================================================================
async def _table_exists(db: AsyncSession, table: str) -> bool:
    r = await db.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :t"
        ),
        {"t": table},
    )
    return int(r.scalar_one() or 0) > 0


async def run(tenant_code: str, commit: bool) -> int:
    print("=" * 64)
    print(f"[verify_task_state_chain] tenant={tenant_code} commit={commit}")
    print("=" * 64)

    db_manager._get_or_create_tenant_engine(tenant_code)
    factory = db_manager._tenant_session_factories[tenant_code]

    rec = Recorder()
    async with factory() as db:
        try:
            has_table = await _table_exists(db, "biz_task")
        except Exception as e:  # noqa: BLE001
            print(
                f"无法连接租户库或数据库不存在：{type(e).__name__}: {e}\n"
                f"请确认租户 {tenant_code} 的业务库已初始化"
                f"（参考 scripts/init/init_dev_env.py）。"
            )
            return 1
        if not has_table:
            print(f"租户 {tenant_code} 未初始化（biz_task 不存在），无法验证。")
            return 1
        try:
            await scenario_forward_and_unsign(db, rec)
            await scenario_reverse_chain(db, rec)
            await scenario_force_cancel(db, rec)
        except Exception as e:  # noqa: BLE001
            rec.fail("场景执行中断（未捕获异常）", f"{type(e).__name__}: {e}")
        finally:
            if commit:
                await db.commit()
                print("\n>>> 已提交事务（--commit）")
            else:
                await db.rollback()
                print("\n>>> 已回滚事务（dry-run，库未变更）")

    # 用例勾选清单
    print("\n" + "=" * 64)
    print("用例勾选清单（对照《02.运单与任务单状态机联动设计.md》§10）")
    print("=" * 64)
    for mark, case, detail in rec.lines:
        sym = {"PASS": "✓", "FAIL": "✗", "SKIP": "-"}[mark]
        print(f"  [{sym}] {case}" + (f"  ({detail})" if detail else ""))
    print("-" * 64)
    print(f"合计：通过 {rec.passed} / 失败 {rec.failed} / 跳过 {rec.skipped}")
    return 0 if rec.failed == 0 else 1


async def main_async() -> int:
    p = argparse.ArgumentParser(description="任务单全链路状态机验证（正向+逆向）")
    p.add_argument("tenant_code", help="租户 code（开发租户）")
    p.add_argument(
        "--commit",
        action="store_true",
        help="真正写库（默认 dry-run，跑完回滚）",
    )
    args = p.parse_args()
    try:
        return await run(args.tenant_code, args.commit)
    finally:
        await db_manager.close_all()


if __name__ == "__main__":
    sys.exit(asyncio.run(main_async()))
