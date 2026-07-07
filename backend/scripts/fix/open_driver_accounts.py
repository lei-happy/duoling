"""存量驾驶员登录账号一次性开通脚本。

背景：
  在「创建驾驶员即自动开通 H5 登录账号」上线前创建的 biz_driver，只有租户库
  记录，没有平台库 sys_user / sys_user_tenant(user_type=3)，也没有回填
  biz_driver.user_id，导致司机无法登录 H5。本脚本按手机号为存量驾驶员批量
  开通登录账号。

用法：
    # 干跑（不写入），单个租户
    python scripts/fix/open_driver_accounts.py <tenant_code> --dry-run

    # 实际写入
    python scripts/fix/open_driver_accounts.py <tenant_code>

    # 全部已初始化租户
    python scripts/fix/open_driver_accounts.py --all

可选参数：
    --limit N      仅处理前 N 条（按 id 升序）；调试用
    --only-active  仅处理在职（status=1）驾驶员

说明：
  - 新建的 sys_user 默认密码为 123456，force_change_pwd=1（首次登录强制改密）
  - 手机号已是本企业员工/管理员的驾驶员会被跳过（唯一约束冲突），并在输出中标记
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager

from app.modules.client.models import *  # noqa: F401, F403
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.services.capacity.self_capacity.driver.driver_account_sync import (
    DriverPlatformAccountSync,
)


async def _table_exists(db: AsyncSession, table: str) -> bool:
    r = await db.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :t"
        ),
        {"t": table},
    )
    return int(r.scalar_one() or 0) > 0


async def _open_tenant(
    tenant_code: str,
    *,
    dry_run: bool,
    limit: Optional[int],
    only_active: bool,
) -> None:
    print(f"\n{'=' * 60}")
    print(f"[open_driver_accounts] tenant={tenant_code} dry_run={dry_run}")
    print(f"{'=' * 60}")

    db_manager._get_or_create_tenant_engine(tenant_code)
    tenant_factory = db_manager._tenant_session_factories[tenant_code]
    platform_factory = db_manager._platform_session_factory

    async with tenant_factory() as tdb:
        if not await _table_exists(tdb, "biz_driver"):
            print(f"  跳过：租户 {tenant_code} 未初始化（biz_driver 不存在）")
            return
        stmt = select(Driver.id).where(Driver.is_deleted == 0)
        if only_active:
            stmt = stmt.where(Driver.status == 1)
        stmt = stmt.order_by(Driver.id.asc())
        if limit:
            stmt = stmt.limit(limit)
        driver_ids = [int(r) for r in (await tdb.execute(stmt)).scalars().all()]

    print(f"  扫描驾驶员：{len(driver_ids)} 条")
    if not driver_ids:
        return

    opened = 0
    conflict = 0
    failed = 0

    async with tenant_factory() as tdb, platform_factory() as pdb:
        for did in driver_ids:
            try:
                res = await DriverPlatformAccountSync.sync_account(
                    pdb, tdb, tenant_code, did
                )
                if res.conflict:
                    conflict += 1
                    print(f"  [冲突] driver_id={did}: {res.message}")
                elif res.opened:
                    opened += 1
                else:
                    print(f"  [跳过] driver_id={did}: {res.message}")
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"  [失败] driver_id={did}: {e}")

        if dry_run:
            await pdb.rollback()
            await tdb.rollback()
        else:
            await pdb.commit()
            await tdb.commit()

    print(
        f"  统计：开通={opened}  冲突={conflict}  失败={failed}  "
        f"模式={'dry_run' if dry_run else 'write'}"
    )


async def _list_all_tenants() -> List[str]:
    from app.modules.console.models.tenant.tenant import Tenant

    await db_manager.init_platform_db()
    factory = db_manager._platform_session_factory
    async with factory() as db:
        r = await db.execute(
            select(Tenant.tenant_code).where(Tenant.is_deleted == 0)
        )
        return [str(c) for (c,) in r.all() if c]


async def main_async() -> None:
    p = argparse.ArgumentParser(description="存量驾驶员登录账号批量开通")
    p.add_argument("tenant_code", nargs="?", help="单租户 code（缺省时配合 --all）")
    p.add_argument("--all", action="store_true", help="处理全部租户")
    p.add_argument("--dry-run", action="store_true", help="只算不写")
    p.add_argument("--limit", type=int, default=None, help="每租户处理上限")
    p.add_argument("--only-active", action="store_true", help="仅处理在职驾驶员")
    args = p.parse_args()

    if not args.all and not args.tenant_code:
        p.error("必须指定 tenant_code 或 --all")

    await db_manager.init_platform_db()

    try:
        if args.all:
            codes = await _list_all_tenants()
            for code in codes:
                await _open_tenant(
                    code,
                    dry_run=args.dry_run,
                    limit=args.limit,
                    only_active=args.only_active,
                )
        else:
            await _open_tenant(
                args.tenant_code,
                dry_run=args.dry_run,
                limit=args.limit,
                only_active=args.only_active,
            )
    finally:
        await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main_async())
