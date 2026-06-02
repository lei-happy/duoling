#!/usr/bin/env python3
"""
存量租户 biz_region 坐标回填：从平台 sys_regions 同步 longitude/latitude。

仅更新 source=0 且 level<=3 的系统地区，不覆盖企业自定义地区。

用法：
  cd backend
  python -m scripts.fix.backfill_tenant_region_coords
  python -m scripts.fix.backfill_tenant_region_coords --tenant-code demo001
  python -m scripts.fix.backfill_tenant_region_coords --dry-run
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import create_engine, text

from app.core.config import get_settings

# biz_region.code 为 utf8mb4_unicode_ci，平台库 CAST 默认为 utf8mb4_0900_ai_ci；
# 用数值比较避免跨库 JOIN 的 collation 冲突。
# 旧租户可能仍为 12 位国标 code（如 110000000000），平台高德数据为 6 位 adcode（110000）。
_REGION_CODE_MATCH = """
  sr.code = IF(
    CHAR_LENGTH(TRIM(br.code)) > 6,
    CAST(br.code AS UNSIGNED) DIV 1000000,
    CAST(br.code AS UNSIGNED)
  )
"""
_REGION_JOIN = _REGION_CODE_MATCH


def get_all_tenant_codes(engine) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT tenant_code FROM sys_tenant WHERE is_deleted = 0 ORDER BY tenant_code")
        )
        return [row[0] for row in rows]


def backfill_tenant(
    tenant_code: str,
    *,
    platform_db: str,
    settings,
    dry_run: bool,
) -> int:
    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)

    sql = text(
        f"""
        UPDATE biz_region br
        INNER JOIN `{platform_db}`.sys_regions sr
          ON {_REGION_JOIN}
        SET br.longitude = sr.longitude,
            br.latitude = sr.latitude,
            br.updated_at = NOW()
        WHERE br.source = 0
          AND br.level <= 3
          AND br.is_deleted = 0
          AND sr.is_deleted = 0
          AND sr.longitude IS NOT NULL
          AND sr.latitude IS NOT NULL
          AND (
            br.longitude IS NULL OR br.latitude IS NULL
            OR br.longitude <> sr.longitude OR br.latitude <> sr.latitude
          )
        """
    )

    count_sql = text(
        f"""
        SELECT COUNT(*)
        FROM biz_region br
        INNER JOIN `{platform_db}`.sys_regions sr
          ON {_REGION_JOIN}
        WHERE br.source = 0
          AND br.level <= 3
          AND br.is_deleted = 0
          AND sr.is_deleted = 0
          AND sr.longitude IS NOT NULL
          AND sr.latitude IS NOT NULL
          AND (
            br.longitude IS NULL OR br.latitude IS NULL
            OR br.longitude <> sr.longitude OR br.latitude <> sr.latitude
          )
        """
    )

    with engine.begin() as conn:
        affected = conn.execute(count_sql).scalar() or 0
        if dry_run:
            print(f"  [dry-run] {tenant_code}: 将更新 {affected} 条")
            return int(affected)
        if affected == 0:
            print(f"  [skip] {tenant_code}: 无需更新")
            return 0
        conn.execute(sql)
        print(f"  [ok] {tenant_code}: 已更新 {affected} 条")
        return int(affected)


def main() -> int:
    parser = argparse.ArgumentParser(description="回填租户 biz_region 坐标")
    parser.add_argument("--tenant-code", help="仅处理指定租户")
    parser.add_argument("--dry-run", action="store_true", help="仅统计，不写入")
    args = parser.parse_args()

    settings = get_settings()
    platform_url = settings.platform_db_url_sync
    platform_engine = create_engine(platform_url)
    platform_db = settings.platform_database_name

    if args.tenant_code:
        tenant_codes = [args.tenant_code]
    else:
        tenant_codes = get_all_tenant_codes(platform_engine)
        if not tenant_codes:
            print("未找到活跃租户")
            return 1

    print(
        f"平台库: {platform_db} | 租户数: {len(tenant_codes)} | "
        f"模式: {'dry-run' if args.dry_run else 'write'}"
    )

    total = 0
    for code in tenant_codes:
        try:
            total += backfill_tenant(
                code,
                platform_db=platform_db,
                settings=settings,
                dry_run=args.dry_run,
            )
        except Exception as exc:
            print(f"  [error] {code}: {exc}")

    print(f"\n完成，共影响 {total} 条记录")
    return 0


if __name__ == "__main__":
    sys.exit(main())
