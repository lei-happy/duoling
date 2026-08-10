"""任务状态事件一次性回填脚本（与时间流改造配套）

背景：
  ``biz_task_status_event`` 上线前的历史任务没有任何状态流水，详情页时间流会是空的。
  本脚本按 ``biz_task`` 上现存的时间戳倒推历史事件，全部标记 ``source=5``（历史回填），
  并同步回填 ``stage_entered_at``。

推断规则（按任务当前状态决定推断到哪一步为止）：
  created_at            → 创建（to_status=-1）
  assigned_at           → 分配承运（-1→0）
  dispatched_at         → 派车（0→1）
  actual_load_time      → 装车（1→2）
  actual_load_time      → 出发（2→3，无独立时间戳，取装车时间近似）
  actual_arrive_time    → 到达（3→4）
  MAX(item.signed_at)   → 交车（4→5）
  updated_at            → 关闭 / 取消（7 / 9，无独立时间戳）

缺失时间戳时按前一条事件时间顺延，保证时间轴单调递增。
已有事件的任务默认跳过（可用 --force 覆盖重建）。

用法：
    # 干跑（不写入），单个租户
    python scripts/fix/backfill_task_status_events.py <tenant_code> --dry-run

    # 实际写入
    python scripts/fix/backfill_task_status_events.py <tenant_code>

    # 全部租户
    python scripts/fix/backfill_task_status_events.py --all

可选参数：
    --limit N    仅处理前 N 条任务（按 id 升序）；调试用
    --force      已有事件的任务先删除回填事件（source=5）再重建

输出：
  - stdout 摘要（扫描 / 回填任务数 / 事件数 / 跳过 / 失败）
  - reports/task_status_event_backfill_<tenant>_<timestamp>.csv：任务级明细
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager

# 引入所有租户模型
from app.modules.client.models import *  # noqa: F401, F403
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_status_event import (
    TASK_EVENT_ARRIVE,
    TASK_EVENT_ASSIGN_CARRIER,
    TASK_EVENT_CANCEL,
    TASK_EVENT_CLOSE,
    TASK_EVENT_CREATE,
    TASK_EVENT_DELIVER,
    TASK_EVENT_DEPART,
    TASK_EVENT_DISPATCH,
    TASK_EVENT_LOAD,
    TASK_EVENT_SOURCE_BACKFILL,
    TaskStatusEvent,
)
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_ARRIVED,
    TASK_CANCELLED,
    TASK_CLOSED,
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_PENDING_ASSIGN,
    TASK_PENDING_DISPATCH,
    TASK_SIGNED,
)


REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")

# 主流程每一步：(到达状态, 事件类型, 取时间的字段名)
# 时间字段为 None 表示该步没有独立时间戳，由顺延逻辑兜底。
_MAIN_CHAIN: List[Tuple[int, int, Optional[str]]] = [
    (TASK_PENDING_DISPATCH, TASK_EVENT_ASSIGN_CARRIER, "assigned_at"),
    (TASK_DISPATCHED, TASK_EVENT_DISPATCH, "dispatched_at"),
    (TASK_LOADED, TASK_EVENT_LOAD, "actual_load_time"),
    (TASK_ON_WAY, TASK_EVENT_DEPART, "actual_load_time"),
    (TASK_ARRIVED, TASK_EVENT_ARRIVE, "actual_arrive_time"),
    (TASK_SIGNED, TASK_EVENT_DELIVER, "signed_at"),
]

# 终态：从主流程末尾再补一跳
_TERMINAL_EVENTS = {
    TASK_CLOSED: TASK_EVENT_CLOSE,
    TASK_CANCELLED: TASK_EVENT_CANCEL,
}

_BACKFILL_REASON = "历史数据回填（依据既有时间戳推断，非真实操作记录）"


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


async def _table_exists(db: AsyncSession, table: str) -> bool:
    r = await db.execute(text(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = :t"
    ), {"t": table})
    return int(r.scalar_one() or 0) > 0


def _build_events(
    task: Task, signed_at: Optional[datetime],
) -> List[dict]:
    """按当前状态倒推该任务应有的历史事件（时间轴单调递增）。"""
    cur = int(task.status)
    base = task.created_at or task.updated_at or datetime.now()
    events: List[dict] = [{
        "event_type": TASK_EVENT_CREATE,
        "from_status": None,
        "to_status": TASK_PENDING_ASSIGN,
        "event_time": base,
    }]
    last_time = base
    prev_status = TASK_PENDING_ASSIGN

    # 取消是从任意状态跳出的，主流程只能推到「取消前走到过哪一步」；
    # 无从判断时保守地只回填到已知时间戳覆盖的那一步。
    walk_to = cur if cur not in _TERMINAL_EVENTS else _reached_status(task, signed_at)

    for to_status, event_type, field in _MAIN_CHAIN:
        if to_status > walk_to:
            break
        raw = signed_at if field == "signed_at" else getattr(task, field, None)
        # 缺时间戳时顺延 1 秒，避免同一时刻堆叠导致时间流乱序
        happened = raw if raw and raw >= last_time else last_time + timedelta(seconds=1)
        events.append({
            "event_type": event_type,
            "from_status": prev_status,
            "to_status": to_status,
            "event_time": happened,
        })
        last_time = happened
        prev_status = to_status

    terminal = _TERMINAL_EVENTS.get(cur)
    if terminal is not None:
        happened = task.updated_at or last_time
        if happened < last_time:
            happened = last_time + timedelta(seconds=1)
        events.append({
            "event_type": terminal,
            "from_status": prev_status,
            "to_status": cur,
            "event_time": happened,
        })
        last_time = happened

    return events


def _reached_status(task: Task, signed_at: Optional[datetime]) -> int:
    """终态任务在进入终态前最远走到过的状态，按时间戳存在性判断。"""
    if signed_at is not None:
        return TASK_SIGNED
    if task.actual_arrive_time is not None:
        return TASK_ARRIVED
    if task.actual_load_time is not None:
        return TASK_ON_WAY
    if task.dispatched_at is not None:
        return TASK_DISPATCHED
    if task.assigned_at is not None:
        return TASK_PENDING_DISPATCH
    return TASK_PENDING_ASSIGN


async def _backfill_tenant(
    tenant_code: str,
    *,
    dry_run: bool,
    limit: Optional[int],
    force: bool,
) -> None:
    print(f"\n{'=' * 60}")
    print(f"[backfill_task_status_events] tenant={tenant_code} dry_run={dry_run}")
    print(f"{'=' * 60}")

    db_manager._get_or_create_tenant_engine(tenant_code)
    factory = db_manager._tenant_session_factories[tenant_code]

    async with factory() as db:
        if not await _table_exists(db, "biz_task_status_event"):
            print(f"  跳过：租户 {tenant_code} 未建 biz_task_status_event，请先跑迁移")
            return

        stmt = select(Task).where(Task.is_deleted == 0).order_by(Task.id.asc())
        if limit:
            stmt = stmt.limit(limit)
        tasks = list((await db.execute(stmt)).scalars().all())
        print(f"  扫描任务：{len(tasks)} 条")
        if not tasks:
            return

        task_ids = [int(t.id) for t in tasks]

        # 已有事件的任务
        r = await db.execute(
            select(TaskStatusEvent.task_id)
            .where(TaskStatusEvent.task_id.in_(task_ids))
            .group_by(TaskStatusEvent.task_id)
        )
        has_events = {int(i) for (i,) in r.all()}

        # 任务维度交车时间
        r = await db.execute(
            select(
                TaskWaybillItem.task_id,
                func.max(TaskWaybillItem.signed_at),
            )
            .where(
                TaskWaybillItem.task_id.in_(task_ids),
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.signed_at.isnot(None),
            )
            .group_by(TaskWaybillItem.task_id)
        )
        signed_map = {int(tid): dt for (tid, dt) in r.all()}

        done: list[dict] = []
        skipped = 0
        failed = 0
        total_events = 0

        for task in tasks:
            tid = int(task.id)
            try:
                if tid in has_events:
                    if not force:
                        skipped += 1
                        continue
                    if not dry_run:
                        await db.execute(
                            delete(TaskStatusEvent).where(
                                TaskStatusEvent.task_id == tid,
                                TaskStatusEvent.source == TASK_EVENT_SOURCE_BACKFILL,
                            )
                        )

                events = _build_events(task, signed_map.get(tid))
                if not dry_run:
                    for e in events:
                        db.add(TaskStatusEvent(
                            task_id=tid,
                            task_no=task.task_no,
                            source=TASK_EVENT_SOURCE_BACKFILL,
                            reason=_BACKFILL_REASON,
                            **e,
                        ))
                    task.stage_entered_at = events[-1]["event_time"]
                done.append({
                    "taskId": tid,
                    "taskNo": task.task_no,
                    "status": int(task.status),
                    "eventCount": len(events),
                    "stageEnteredAt": events[-1]["event_time"],
                })
                total_events += len(events)
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"  [失败] task_id={tid}: {e}")

        if dry_run:
            await db.rollback()
        else:
            await db.commit()

    print(
        f"  统计：回填任务={len(done)}  事件={total_events}  "
        f"跳过（已有事件）={skipped}  失败={failed}  "
        f"模式={'dry_run' if dry_run else 'write'}"
    )

    if done:
        os.makedirs(REPORT_DIR, exist_ok=True)
        path = os.path.join(
            REPORT_DIR,
            f"task_status_event_backfill_{tenant_code}_{_ts()}.csv",
        )
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["任务ID", "任务单号", "当前状态", "回填事件数", "阶段进入时间"])
            for it in done:
                w.writerow([
                    it["taskId"], it["taskNo"], it["status"],
                    it["eventCount"], it["stageEnteredAt"],
                ])
        print(f"  明细 CSV：{path}")


async def _list_all_tenants() -> List[str]:
    """从平台库枚举所有未删除的租户。"""
    from app.modules.console.models.tenant.tenant import Tenant
    await db_manager.init_platform_db()
    factory = db_manager._platform_session_factory
    async with factory() as db:
        r = await db.execute(
            select(Tenant.tenant_code).where(Tenant.is_deleted == 0)
        )
        return [str(c) for (c,) in r.all() if c]


async def main_async() -> None:
    p = argparse.ArgumentParser(description="一次性回填任务状态事件与阶段进入时间")
    p.add_argument("tenant_code", nargs="?", help="单租户 code（缺省时配合 --all）")
    p.add_argument("--all", action="store_true", help="处理全部租户")
    p.add_argument("--dry-run", action="store_true", help="只算不写")
    p.add_argument("--limit", type=int, default=None, help="每租户处理上限")
    p.add_argument(
        "--force", action="store_true",
        help="已有事件的任务也重建（仅删除 source=5 的回填事件）",
    )
    args = p.parse_args()

    if not args.all and not args.tenant_code:
        p.error("必须指定 tenant_code 或 --all")

    try:
        codes = await _list_all_tenants() if args.all else [args.tenant_code]
        for code in codes:
            await _backfill_tenant(
                code, dry_run=args.dry_run, limit=args.limit, force=args.force,
            )
    finally:
        # 脚本退出前释放连接池，避免 Windows 下 asyncio 事件循环关闭后
        # aiomysql Connection.__del__ 触发 RuntimeError: Event loop is closed
        await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main_async())
