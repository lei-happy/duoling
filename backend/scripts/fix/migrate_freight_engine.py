"""
运费匹配引擎升级 - 数据迁移脚本

执行内容：
  1) 给 4 张已有业务表追加新字段（biz_waybill / biz_waybill_cargo /
     biz_freight_rate / biz_freight_contract）。
     已存在的列会被忽略（基于 information_schema 检查），可重复执行。
  2) 通过 SQLAlchemy metadata 创建 8 张新表（如不存在）。
  3) 回填 origin_region_id / destination_region_id（match by code）。
  4) 回填 brand_id / series_id（精确匹配 brand_name_cn + series_name）。
  5) 回填 biz_waybill.calc_status：已有 freight_amount 的标记为 calculated，
     其它保持 pending。

用法：
    python scripts/fix/migrate_freight_engine.py [tenant_code]
不传 tenant_code 则迁移全部已初始化的租户库。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect

from app.core.config import get_settings
from app.core.database import TenantBase, DatabaseManager

# 引入所有租户模型，确保 metadata 已包含所有 8 张新表
from app.modules.client.models import *  # noqa: F401, F403


# ---- 4 张已有表的列升级清单 ----
# 每条 = (table_name, column_name, ddl_fragment)
ALTER_COLUMNS: list[tuple[str, str, str]] = [
    # biz_waybill
    ("biz_waybill", "origin_region_id",
        "ADD COLUMN `origin_region_id` bigint DEFAULT NULL COMMENT '出发地行政区ID' AFTER `origin_code`"),
    ("biz_waybill", "destination_region_id",
        "ADD COLUMN `destination_region_id` bigint DEFAULT NULL COMMENT '目的地行政区ID' AFTER `destination_code`"),
    ("biz_waybill", "calc_status",
        "ADD COLUMN `calc_status` varchar(32) NOT NULL DEFAULT 'pending' COMMENT '计算状态' AFTER `status`"),
    ("biz_waybill", "is_locked",
        "ADD COLUMN `is_locked` smallint NOT NULL DEFAULT 0 COMMENT '是否锁定' AFTER `calc_status`"),
    ("biz_waybill", "waybill_version",
        "ADD COLUMN `waybill_version` int NOT NULL DEFAULT 1 COMMENT '运单版本号' AFTER `is_locked`"),
    ("biz_waybill", "last_calc_at",
        "ADD COLUMN `last_calc_at` datetime DEFAULT NULL COMMENT '最近一次正式计算时间' AFTER `waybill_version`"),
    ("biz_waybill", "last_result_id",
        "ADD COLUMN `last_result_id` bigint DEFAULT NULL COMMENT '最近一次计算结果主表ID' AFTER `last_calc_at`"),
    # biz_waybill_cargo
    ("biz_waybill_cargo", "brand_id",
        "ADD COLUMN `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID' AFTER `vehicle_model`"),
    ("biz_waybill_cargo", "series_id",
        "ADD COLUMN `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID' AFTER `brand_id`"),
    ("biz_waybill_cargo", "cargo_version",
        "ADD COLUMN `cargo_version` int NOT NULL DEFAULT 1 COMMENT '明细版本号' AFTER `quantity`"),
    # biz_freight_rate
    ("biz_freight_rate", "origin_region_id",
        "ADD COLUMN `origin_region_id` bigint DEFAULT NULL COMMENT '出发地行政区ID' AFTER `origin_code`"),
    ("biz_freight_rate", "destination_region_id",
        "ADD COLUMN `destination_region_id` bigint DEFAULT NULL COMMENT '目的地行政区ID' AFTER `destination_code`"),
    ("biz_freight_rate", "brand_id",
        "ADD COLUMN `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID' AFTER `vehicle_model`"),
    ("biz_freight_rate", "series_id",
        "ADD COLUMN `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID' AFTER `brand_id`"),
    ("biz_freight_rate", "match_type",
        "ADD COLUMN `match_type` varchar(16) NOT NULL DEFAULT 'series' "
        "COMMENT '车型匹配类型 series/brand/general' AFTER `series_id`"),
    ("biz_freight_rate", "min_amount",
        "ADD COLUMN `min_amount` decimal(12,2) DEFAULT NULL COMMENT '最低运费' AFTER `unit_price`"),
    ("biz_freight_rate", "is_bidirectional",
        "ADD COLUMN `is_bidirectional` smallint NOT NULL DEFAULT 0 COMMENT '是否双向' AFTER `price_type`"),
    ("biz_freight_rate", "priority",
        "ADD COLUMN `priority` int NOT NULL DEFAULT 0 COMMENT '人工优先级' AFTER `is_bidirectional`"),
    ("biz_freight_rate", "rule_version",
        "ADD COLUMN `rule_version` int NOT NULL DEFAULT 1 COMMENT '规则版本号' AFTER `status`"),
    # biz_freight_contract
    ("biz_freight_contract", "contract_version",
        "ADD COLUMN `contract_version` int NOT NULL DEFAULT 1 COMMENT '合同版本号' AFTER `status`"),
]

# 升级后需要的索引（COLUMN 创建后再加；忽略已存在）
ALTER_INDEXES: list[tuple[str, str, str]] = [
    ("biz_waybill", "idx_calc_status",
        "ADD INDEX `idx_calc_status` (`calc_status`)"),
    ("biz_waybill_cargo", "idx_cargo_brand",
        "ADD INDEX `idx_cargo_brand` (`brand_id`)"),
    ("biz_waybill_cargo", "idx_cargo_series",
        "ADD INDEX `idx_cargo_series` (`series_id`)"),
    ("biz_freight_rate", "idx_rate_match_region",
        "ADD INDEX `idx_rate_match_region` "
        "(`customer_id`, `origin_region_id`, `destination_region_id`, `status`, `is_deleted`)"),
]

# 计费引擎相关的 8 张新表
NEW_TABLES = [
    "biz_waybill_freight_result",
    "biz_waybill_freight_result_detail",
    "biz_freight_calc_task",
    "biz_freight_calc_exception",
    "biz_region_alias",
    "biz_vehicle_alias",
    "biz_freight_rate_change_log",
    "biz_waybill_import_batch",
    "biz_waybill_import_row",
]


def get_all_tenant_codes(settings) -> list:
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tenant_code FROM sys_tenant "
            "WHERE is_deleted = 0 AND db_initialized = 1"
        ))
        codes = [row[0] for row in result]
    engine.dispose()
    return codes


def _column_exists(conn, table: str, column: str) -> bool:
    sql = (
        "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
    )
    return conn.execute(text(sql), {"t": table, "c": column}).scalar() is not None


def _index_exists(conn, table: str, index: str) -> bool:
    sql = (
        "SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND INDEX_NAME = :i"
    )
    return conn.execute(text(sql), {"t": table, "i": index}).scalar() is not None


def _alter_existing_tables(conn) -> None:
    for table, column, ddl in ALTER_COLUMNS:
        if _column_exists(conn, table, column):
            continue
        try:
            conn.execute(text(f"ALTER TABLE `{table}` {ddl}"))
            print(f"  ALTER {table}.{column} OK")
        except Exception as e:
            print(f"  ALTER {table}.{column} FAILED: {e}")

    for table, index, ddl in ALTER_INDEXES:
        if _index_exists(conn, table, index):
            continue
        try:
            conn.execute(text(f"ALTER TABLE `{table}` {ddl}"))
            print(f"  INDEX {table}.{index} OK")
        except Exception as e:
            print(f"  INDEX {table}.{index} FAILED: {e}")


def _create_new_tables(engine) -> None:
    inspector = sa_inspect(engine)
    existing = set(inspector.get_table_names())
    todo = [t for t in TenantBase.metadata.sorted_tables
            if t.name in NEW_TABLES and t.name not in existing]
    if not todo:
        print("  新表均已存在，跳过 create_all")
        return
    TenantBase.metadata.create_all(engine, tables=todo)
    print(f"  已创建新表: {[t.name for t in todo]}")


def _backfill_region_ids(conn) -> None:
    # biz_waybill
    conn.execute(text(
        "UPDATE biz_waybill w "
        "JOIN biz_region r ON r.code = w.origin_code AND r.is_deleted = 0 "
        "SET w.origin_region_id = r.id "
        "WHERE w.origin_region_id IS NULL AND w.origin_code IS NOT NULL"
    ))
    conn.execute(text(
        "UPDATE biz_waybill w "
        "JOIN biz_region r ON r.code = w.destination_code AND r.is_deleted = 0 "
        "SET w.destination_region_id = r.id "
        "WHERE w.destination_region_id IS NULL AND w.destination_code IS NOT NULL"
    ))
    # biz_freight_rate
    conn.execute(text(
        "UPDATE biz_freight_rate fr "
        "JOIN biz_region r ON r.code = fr.origin_code AND r.is_deleted = 0 "
        "SET fr.origin_region_id = r.id "
        "WHERE fr.origin_region_id IS NULL AND fr.origin_code IS NOT NULL"
    ))
    conn.execute(text(
        "UPDATE biz_freight_rate fr "
        "JOIN biz_region r ON r.code = fr.destination_code AND r.is_deleted = 0 "
        "SET fr.destination_region_id = r.id "
        "WHERE fr.destination_region_id IS NULL AND fr.destination_code IS NOT NULL"
    ))
    print("  已回填 region_id 字段")


def _backfill_brand_series_ids(conn) -> None:
    # biz_waybill_cargo: brand_id
    conn.execute(text(
        "UPDATE biz_waybill_cargo c "
        "JOIN biz_vehicle_brand b ON b.brand_name_cn = c.vehicle_brand "
        "SET c.brand_id = b.brand_id "
        "WHERE c.brand_id IS NULL AND c.vehicle_brand IS NOT NULL"
    ))
    # biz_waybill_cargo: series_id（要求品牌+车系都精确）
    conn.execute(text(
        "UPDATE biz_waybill_cargo c "
        "JOIN biz_vehicle_brand b ON b.brand_name_cn = c.vehicle_brand "
        "JOIN biz_vehicle_series s ON s.brand_id = b.brand_id "
        "  AND s.series_name = c.vehicle_model "
        "SET c.series_id = s.series_id "
        "WHERE c.series_id IS NULL AND c.vehicle_model IS NOT NULL"
    ))
    # biz_freight_rate: brand_id / series_id（同上规则）
    conn.execute(text(
        "UPDATE biz_freight_rate r "
        "JOIN biz_vehicle_brand b ON b.brand_name_cn = r.vehicle_brand "
        "SET r.brand_id = b.brand_id "
        "WHERE r.brand_id IS NULL AND r.vehicle_brand IS NOT NULL"
    ))
    conn.execute(text(
        "UPDATE biz_freight_rate r "
        "JOIN biz_vehicle_brand b ON b.brand_name_cn = r.vehicle_brand "
        "JOIN biz_vehicle_series s ON s.brand_id = b.brand_id "
        "  AND s.series_name = r.vehicle_model "
        "SET r.series_id = s.series_id "
        "WHERE r.series_id IS NULL AND r.vehicle_model IS NOT NULL"
    ))
    # 回填 match_type（已存数据按当前列内容推断）
    conn.execute(text(
        "UPDATE biz_freight_rate SET match_type = CASE "
        "WHEN series_id IS NOT NULL THEN 'series' "
        "WHEN brand_id IS NOT NULL THEN 'brand' "
        "ELSE 'general' END"
    ))
    print("  已回填 brand_id / series_id / match_type")


def _backfill_calc_status(conn) -> None:
    conn.execute(text(
        "UPDATE biz_waybill SET calc_status = 'calculated' "
        "WHERE calc_status = 'pending' AND freight_amount IS NOT NULL "
        "AND is_deleted = 0"
    ))
    print("  已根据 freight_amount 回填 calc_status")


def migrate_tenant_database(tenant_code: str, settings) -> None:
    db_name = settings.tenant_database_name(tenant_code)
    print(f"\n{'=' * 60}")
    print(f"迁移租户库: {db_name} (tenant_code={tenant_code})")
    print(f"{'=' * 60}")

    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)

    with engine.begin() as conn:
        print("[1/4] 升级已有表字段与索引")
        _alter_existing_tables(conn)

    print("[2/4] 创建 8 张新表")
    _create_new_tables(engine)

    with engine.begin() as conn:
        print("[3/4] 回填 region_id / brand_id / series_id")
        _backfill_region_ids(conn)
        _backfill_brand_series_ids(conn)

    with engine.begin() as conn:
        print("[4/4] 回填 calc_status")
        _backfill_calc_status(conn)

    engine.dispose()
    print(f"租户 {tenant_code} 迁移完成")


if __name__ == "__main__":
    settings = get_settings()

    args = [a for a in sys.argv[1:] if a]

    run_all = "--all" in args
    positional = [a for a in args if not a.startswith("--")]

    if run_all or not positional:
        codes = get_all_tenant_codes(settings)
        if not codes:
            print("未找到已初始化的租户库")
            sys.exit(0)
        print(f"找到 {len(codes)} 个已初始化的租户库: {codes}")
    else:
        codes = [positional[0]]

    for code in codes:
        try:
            migrate_tenant_database(code, settings)
        except Exception as e:
            print(f"迁移租户 {code} 失败: {e}")

    print(f"\n全部完成！共处理 {len(codes)} 个租户库")
