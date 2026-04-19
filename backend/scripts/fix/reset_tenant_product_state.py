"""
重置指定租户的产品授权（sys_tenant_product）为干净状态。

适用场景（基于本次定位的真实问题）：
    在测试 / 排错 / 直连 DB 改 sys_tenant_product 后，
    出现「standard 已过期 + pro 被软删」等垃圾状态，
    `_get_tenant_feature_codes` 拿到空集合 → 菜单接口降级返回全量，
    `get_enterprise_info` 拿不到记录 → 企业管理页空。

本脚本会：
    1. 软删该租户当前所有 sys_tenant_product 记录；
    2. 按指定 version_code 创建一条新的有效授权（开始=now，
       结束=None 永久；也可指定 days 参数）；
    3. 同步把 sys_tenant.menu_version + 1，触发客户端重新拉取菜单。

用法：
    python backend/scripts/fix/reset_tenant_product_state.py \
        --tenant 1001 --version pro

    # 指定有效期天数（默认 None 永久）
    python backend/scripts/fix/reset_tenant_product_state.py \
        --tenant 1001 --version pro --days 90

    # 仅预览
    python backend/scripts/fix/reset_tenant_product_state.py \
        --tenant 1001 --version pro --dry-run
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


def reset(tenant_code: str, version_code: str, days: int, dry_run: bool) -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)

    now = datetime.now()
    end_time = now + timedelta(days=days) if days > 0 else None

    with engine.connect() as conn:
        # 1. 拿到 tenant_id 与 version_id
        t_row = conn.execute(
            text(
                "SELECT id, tenant_code, COALESCE(menu_version, 0) AS mv "
                "FROM sys_tenant WHERE tenant_code = :tc AND is_deleted = 0"
            ),
            {"tc": tenant_code},
        ).mappings().first()
        if not t_row:
            print(f"[ERR] 租户不存在或已删除: tenant_code={tenant_code}")
            return
        tenant_id = t_row["id"]
        cur_mv = t_row["mv"]

        v_row = conn.execute(
            text(
                "SELECT id, version_code, version_name "
                "FROM sys_product_version "
                "WHERE version_code = :vc AND is_deleted = 0 AND status = 1"
            ),
            {"vc": version_code},
        ).mappings().first()
        if not v_row:
            print(f"[ERR] 产品版本不存在或未启用: version_code={version_code}")
            return
        version_id = v_row["id"]

        # 2. 当前所有授权
        existing = conn.execute(
            text(
                "SELECT id, version_code, start_time, end_time, status, is_deleted "
                "FROM sys_tenant_product WHERE tenant_id = :tid"
            ),
            {"tid": tenant_id},
        ).mappings().all()

        print(f"[INFO] 租户 {tenant_code}（id={tenant_id}）当前授权 {len(existing)} 条：")
        for r in existing:
            print(
                f"  - id={r['id']} {r['version_code']} "
                f"{r['start_time']} ~ {r['end_time']} "
                f"status={r['status']} is_deleted={r['is_deleted']}"
            )

        if dry_run:
            print(
                f"\n[DRY-RUN] 将执行：\n"
                f"  1) UPDATE sys_tenant_product SET is_deleted=1 WHERE tenant_id={tenant_id} AND is_deleted=0\n"
                f"  2) INSERT 新授权 version={version_code}(id={version_id}) "
                f"start={now} end={end_time}\n"
                f"  3) UPDATE sys_tenant SET menu_version={cur_mv + 1}, "
                f"expire_time={end_time} WHERE id={tenant_id}"
            )
            return

        # 3. 软删全部历史授权
        conn.execute(
            text(
                "UPDATE sys_tenant_product "
                "SET is_deleted = 1, updated_at = NOW() "
                "WHERE tenant_id = :tid AND is_deleted = 0"
            ),
            {"tid": tenant_id},
        )

        # 4. 新建干净的授权
        conn.execute(
            text(
                "INSERT INTO sys_tenant_product "
                "(tenant_id, tenant_code, version_id, version_code, "
                "start_time, end_time, status, grant_type, grant_remark, "
                "created_at, updated_at, is_deleted) "
                "VALUES (:tid, :tc, :vid, :vc, :st, :et, 1, 'manual_reset', "
                "'reset_tenant_product_state.py 重置', NOW(), NOW(), 0)"
            ),
            {
                "tid": tenant_id,
                "tc": tenant_code,
                "vid": version_id,
                "vc": version_code,
                "st": now,
                "et": end_time,
            },
        )

        # 5. 同步 sys_tenant.menu_version 与 expire_time
        conn.execute(
            text(
                "UPDATE sys_tenant "
                "SET menu_version = COALESCE(menu_version, 0) + 1, "
                "    expire_time = :et, "
                "    status = CASE WHEN status = 3 THEN 1 ELSE status END, "
                "    updated_at = NOW() "
                "WHERE id = :tid"
            ),
            {"tid": tenant_id, "et": end_time},
        )

        conn.commit()
        print(
            f"\n[OK] 已重置租户 {tenant_code} 授权为 {version_code}"
            f"（{now} ~ {end_time or '永久'}），menu_version 递增为 {cur_mv + 1}"
        )

    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", required=True, help="目标 tenant_code，如 1001")
    parser.add_argument(
        "--version",
        default="pro",
        help="目标 version_code，默认 pro，可选 basic/standard/pro/enterprise",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=0,
        help="授权有效期天数。0 或不传表示 end_time=NULL 永久有效。",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅预览不执行")
    args = parser.parse_args()

    reset(
        tenant_code=args.tenant,
        version_code=args.version,
        days=args.days,
        dry_run=args.dry_run,
    )
    print("\n完成！")
