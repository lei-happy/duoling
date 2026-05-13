"""
双引擎回归对比脚本（Phase 8）

用途：
  在切换到新计费引擎之前，把历史已计算运单（biz_waybill.freight_amount IS NOT NULL）
  在新 FreightMatcher 上重新跑一遍 dry_run，与历史金额做差异对比，输出报表。

输出：
  - stdout 摘要（总数 / identical / minor_diff / major_diff / new_unmatched / old_missing）
  - reports/freight_regression_<tenant>_<timestamp>.json：完整报表
  - reports/freight_regression_<tenant>_<timestamp>.csv：每行差异明细，便于运营核对

用法：
    # 单租户，限制 200 单
    python scripts/fix/dual_engine_regression.py <tenant_code> --limit 200

    # 全部已初始化租户
    python scripts/fix/dual_engine_regression.py --all --limit 100
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import sys
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.config import get_settings
from app.core.database import db_manager

# 引入所有租户模型
from app.modules.client.models import *  # noqa: F401, F403
from app.modules.client.services.billing.dual_engine_compare_service import (
    DualEngineCompareService,
)


REPORT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "reports"
)


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_report_dir() -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)


def _write_report(report: dict, tenant_code: str) -> tuple[str, str]:
    _ensure_report_dir()
    ts = _ts()
    base = os.path.join(REPORT_DIR, f"freight_regression_{tenant_code}_{ts}")
    json_path = base + ".json"
    csv_path = base + ".csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "运单ID", "运单号", "客户ID", "客户", "出发地", "目的地",
            "旧金额", "新金额", "差异", "差异%", "状态", "新引擎状态",
            "错误类型", "错误信息", "明细数",
        ])
        for it in report.get("items", []):
            writer.writerow([
                it.get("waybillId"), it.get("waybillNo"),
                it.get("customerId"), it.get("customerName"),
                it.get("origin"), it.get("destination"),
                it.get("oldAmount"), it.get("newAmount"),
                it.get("diff"),
                f"{(it.get('diffPct') or 0) * 100:.2f}%" if it.get("diffPct") is not None else "",
                it.get("status"),
                it.get("newCalcStatus"),
                it.get("newErrorType") or "",
                it.get("newError") or "",
                it.get("cargoCount"),
            ])
    return json_path, csv_path


async def regression_for_tenant(tenant_code: str, limit: int) -> None:
    print(f"\n{'=' * 60}")
    print(f"[regression] tenant_code={tenant_code} limit={limit}")
    print(f"{'=' * 60}")

    db_manager._get_or_create_tenant_engine(tenant_code)
    factory = db_manager._tenant_session_factories[tenant_code]

    # 先探测目标库是否已经建过 biz_waybill 表，避免库未初始化抛长 traceback
    async with factory() as db:
        from sqlalchemy import text as _text
        try:
            r = await db.execute(_text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name = 'biz_waybill'"
            ))
            exists = int(r.scalar_one() or 0)
        except Exception as e:  # noqa
            print(f"  租户 {tenant_code} 检测库失败：{e}")
            return
        if exists == 0:
            print(f"  跳过：租户 {tenant_code} 数据库未初始化（biz_waybill 不存在）")
            return

    async with factory() as db:
        report = await DualEngineCompareService.compare_batch(
            db,
            customer_id=None,
            date_from=None,
            date_to=None,
            only_calculated=True,
            limit=limit,
            minor_threshold=Decimal("1"),
        )
        await db.rollback()  # 不提交任何东西

    payload = DualEngineCompareService.report_to_dict(report)

    print(
        f"  total={payload['total']} | identical={payload['identical']} | "
        f"minorDiff={payload['minorDiff']} | majorDiff={payload['majorDiff']} | "
        f"newUnmatched={payload['newUnmatched']} | oldMissing={payload['oldMissing']}"
    )
    if payload["total"]:
        ratio = (payload["identical"] + payload["minorDiff"]) / payload["total"]
        print(f"  通过率（identical + minor）= {ratio * 100:.1f}%")

    json_path, csv_path = _write_report(payload, tenant_code)
    print(f"  报表已生成：")
    print(f"    {json_path}")
    print(f"    {csv_path}")


async def main_async() -> None:
    settings = get_settings()
    args = sys.argv[1:]

    limit = 200
    if "--limit" in args:
        idx = args.index("--limit")
        try:
            limit = int(args[idx + 1])
            args.pop(idx + 1)
            args.remove("--limit")
        except (ValueError, IndexError):
            print("--limit 后必须跟一个整数")
            sys.exit(1)

    positional = [a for a in args if not a.startswith("--")]
    run_all = "--all" in args

    tenants: list[str]
    if run_all:
        from sqlalchemy import create_engine as _create_engine
        from sqlalchemy import text as _text
        url = (
            f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
            f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
            f"/{settings.platform_database_name}?charset=utf8mb4"
        )
        eng = _create_engine(url)
        with eng.connect() as conn:
            r = conn.execute(_text(
                "SELECT tenant_code FROM sys_tenant "
                "WHERE is_deleted = 0 AND db_initialized = 1"
            ))
            tenants = [row[0] for row in r]
        eng.dispose()
    elif positional:
        tenants = [positional[0]]
    else:
        print("用法： dual_engine_regression.py <tenant_code> [--limit N]")
        print("       dual_engine_regression.py --all [--limit N]")
        sys.exit(1)

    if not tenants:
        print("没有可处理的租户")
        return

    for tc in tenants:
        try:
            await regression_for_tenant(tc, limit)
        except Exception as e:  # noqa
            print(f"租户 {tc} 处理失败：{e}")

    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main_async())
