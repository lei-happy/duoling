"""运单状态一次性回填脚本（与状态机改造配套）

背景：
  在《02.运单与任务单状态机联动设计.md》落地之前，运单状态完全由人工/旧逻辑维护，
  与任务挂接 (TaskWaybillItem) 的真实进度脱节。改造完成后，需要做一次性回填：
  按新的聚合规则重算 Waybill.status，把历史数据拉齐。

用法：
    # 干跑（不写入），单个租户
    python scripts/fix/backfill_waybill_status.py <tenant_code> --dry-run

    # 实际写入（事务）
    python scripts/fix/backfill_waybill_status.py <tenant_code>

    # 全部已初始化租户
    python scripts/fix/backfill_waybill_status.py --all

可选参数：
    --limit N      仅处理前 N 条（按 id 升序）；调试用
    --statuses A,B 仅处理这些当前状态的运单（默认全量）

输出：
  - stdout 摘要（扫描数 / 变更数 / 跳过数 / 失败数）
  - reports/waybill_status_backfill_<tenant>_<timestamp>.csv：变更明细

注意：
  - 已关闭（status=6）和草稿（status=0）的运单不会被聚合器修改
  - 处理过程中会按 id 升序加锁（with_for_update）避免与在线请求冲突
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import sys
from datetime import datetime
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import db_manager

# 引入所有租户模型
from app.modules.client.models import *  # noqa: F401, F403
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.services.waybill.waybill_status_aggregator import (
    WaybillStatusAggregator,
)


REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_report_dir() -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)


async def _table_exists(db: AsyncSession, table: str) -> bool:
    r = await db.execute(text(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = :t"
    ), {"t": table})
    return int(r.scalar_one() or 0) > 0


async def _backfill_tenant(
    tenant_code: str,
    *,
    dry_run: bool,
    limit: Optional[int],
    statuses: Optional[List[int]],
) -> None:
    print(f"\n{'=' * 60}")
    print(f"[backfill_waybill_status] tenant={tenant_code} dry_run={dry_run}")
    print(f"{'=' * 60}")

    db_manager._get_or_create_tenant_engine(tenant_code)
    factory = db_manager._tenant_session_factories[tenant_code]

    async with factory() as db:
        if not await _table_exists(db, "biz_waybill"):
            print(f"  跳过：租户 {tenant_code} 数据库未初始化（biz_waybill 不存在）")
            return

        stmt = select(Waybill.id, Waybill.status).where(Waybill.is_deleted == 0)
        if statuses:
            stmt = stmt.where(Waybill.status.in_(statuses))
        stmt = stmt.order_by(Waybill.id.asc())
        if limit:
            stmt = stmt.limit(limit)
        rows = list((await db.execute(stmt)).all())

    print(f"  扫描运单：{len(rows)} 条")
    if not rows:
        return

    changed: list[dict] = []
    skipped = 0
    failed = 0

    async with factory() as db:
        for (wid, old_status) in rows:
            try:
                target, metrics = await WaybillStatusAggregator.derive_target_status(
                    db, int(wid),
                )
                if target == int(old_status or 0):
                    skipped += 1
                    continue
                if not dry_run:
                    await WaybillStatusAggregator.recompute(
                        db, int(wid), allow_downgrade=True,
                    )
                changed.append({
                    "waybillId": int(wid),
                    "oldStatus": int(old_status or 0),
                    "newStatus": int(target),
                    "totalCargoQty": metrics["total_cargo_quantity"],
                    "activeQty": metrics["active_quantity"],
                    "signedQty": metrics["signed_quantity"],
                })
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"  [失败] waybill_id={wid}: {e}")

        if not dry_run:
            await db.commit()
        else:
            await db.rollback()

    print(
        f"  统计：变更={len(changed)}  跳过={skipped}  失败={failed}  "
        f"模式={'dry_run' if dry_run else 'write'}"
    )

    if changed:
        _ensure_report_dir()
        path = os.path.join(
            REPORT_DIR,
            f"waybill_status_backfill_{tenant_code}_{_ts()}.csv",
        )
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "运单ID", "原状态", "新状态",
                "Cargo 总台数", "活跃挂接台数", "已签收台数",
            ])
            for it in changed:
                w.writerow([
                    it["waybillId"], it["oldStatus"], it["newStatus"],
                    it["totalCargoQty"], it["activeQty"], it["signedQty"],
                ])
        print(f"  明细 CSV：{path}")


async def _list_all_tenants() -> List[str]:
    """从平台库枚举所有未删除的租户。"""
    from app.modules.console.models.tenant.tenant import Tenant
    db_manager._get_or_create_platform_engine()
    factory = db_manager._platform_session_factory
    async with factory() as db:
        r = await db.execute(
            select(Tenant.tenant_code).where(Tenant.is_deleted == 0)
        )
        return [str(c) for (c,) in r.all() if c]


async def main_async() -> None:
    p = argparse.ArgumentParser(description="一次性回填运单状态")
    p.add_argument("tenant_code", nargs="?", help="单租户 code（缺省时配合 --all）")
    p.add_argument("--all", action="store_true", help="处理全部租户")
    p.add_argument("--dry-run", action="store_true", help="只算不写")
    p.add_argument("--limit", type=int, default=None, help="每租户处理上限")
    p.add_argument(
        "--statuses", type=str, default=None,
        help="逗号分隔的当前状态过滤（如 1,2,3）",
    )
    args = p.parse_args()

    if not args.all and not args.tenant_code:
        p.error("必须指定 tenant_code 或 --all")

    statuses = None
    if args.statuses:
        statuses = [int(s) for s in args.statuses.split(",") if s.strip()]

    if args.all:
        codes = await _list_all_tenants()
        for code in codes:
            await _backfill_tenant(
                code, dry_run=args.dry_run, limit=args.limit, statuses=statuses,
            )
    else:
        await _backfill_tenant(
            args.tenant_code,
            dry_run=args.dry_run,
            limit=args.limit,
            statuses=statuses,
        )


if __name__ == "__main__":
    asyncio.run(main_async())
