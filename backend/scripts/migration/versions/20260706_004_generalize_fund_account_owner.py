"""generalize_fund_account_owner

把驾驶员资金账户泛化为"收款方资金账户"：
  * biz_driver_fund_account / biz_driver_fund_transaction 两表新增 owner_type，
    并把 driver_id 迁移为 owner_id（收款方泛化：1-自有司机 2-承运商(预留) 3-社会运力）。
  * 账户唯一键 uk_dfa_driver_ent -> uk_dfa_owner_ent (owner_type, owner_id, enterprise_id)；
    流水索引 idx_dft_driver -> idx_dft_owner (owner_type, owner_id)。

幂等设计（需与 runner Phase 1.5 reconcile 协同）：
  runner 会先按 ORM 给已存在表补列——owner_type 会被补成 DEFAULT 1，
  owner_id 会被补成 BIGINT NOT NULL DEFAULT 0（reconcile 对 BIGINT 兜底 0）。
  故本迁移在 owner_id 已存在时执行「owner_id = driver_id」回填再删除 driver_id；
  若 owner_id 尚不存在则直接 CHANGE COLUMN 重命名。
  对全新租户（表由 Phase 1 按新 ORM 建好、无 driver_id）本迁移全部为 no-op。
"""

from sqlalchemy import text

MIGRATION_ID = "20260706_004"
MIGRATION_NAME = "generalize_fund_account_owner"

REQUIRES_TABLES = ["biz_driver_fund_account", "biz_driver_fund_transaction"]


_COL_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :tn
      AND column_name = :cn
    LIMIT 1
    """
)

_INDEX_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = :tn
      AND index_name = :ix
    LIMIT 1
    """
)


def _col_exists(conn, table_name: str, column_name: str) -> bool:
    return conn.execute(
        _COL_EXISTS_SQL, {"tn": table_name, "cn": column_name}
    ).fetchone() is not None


def _index_exists(conn, table_name: str, index_name: str) -> bool:
    return conn.execute(
        _INDEX_EXISTS_SQL, {"tn": table_name, "ix": index_name}
    ).fetchone() is not None


def _migrate_owner(
    conn,
    table: str,
    owner_type_comment: str,
    owner_id_comment: str,
) -> None:
    """两表通用：加 owner_type、driver_id -> owner_id。"""
    if not _col_exists(conn, table, "owner_type"):
        conn.execute(text(
            f"ALTER TABLE `{table}` ADD COLUMN `owner_type` SMALLINT NOT NULL "
            f"DEFAULT 1 COMMENT '{owner_type_comment}'"
        ))

    has_owner_id = _col_exists(conn, table, "owner_id")
    has_driver_id = _col_exists(conn, table, "driver_id")

    if not has_owner_id:
        if has_driver_id:
            # reconcile 未补 owner_id：直接重命名（保留原值）
            conn.execute(text(
                f"ALTER TABLE `{table}` CHANGE COLUMN `driver_id` `owner_id` "
                f"BIGINT NOT NULL COMMENT '{owner_id_comment}'"
            ))
            has_owner_id = True
            has_driver_id = False
        else:
            conn.execute(text(
                f"ALTER TABLE `{table}` ADD COLUMN `owner_id` BIGINT NOT NULL "
                f"DEFAULT 0 COMMENT '{owner_id_comment}'"
            ))
            has_owner_id = True
    elif has_driver_id:
        # reconcile 已把 owner_id 补成 DEFAULT 0：从 driver_id 回填真实值
        conn.execute(text(
            f"UPDATE `{table}` SET `owner_id` = `driver_id` "
            f"WHERE `owner_id` = 0 OR `owner_id` IS NULL"
        ))


def upgrade(conn, tenant_code: str) -> None:
    acct = "biz_driver_fund_account"
    txn = "biz_driver_fund_transaction"

    # ---- 账户表 ----
    _migrate_owner(
        conn, acct,
        owner_type_comment="收款方类型 1-自有司机 2-承运商(预留) 3-社会运力",
        owner_id_comment=(
            "收款方ID：owner_type=1时为biz_driver.id，=3时为biz_social_capacity.id"
        ),
    )
    # 删除旧唯一键（drop 列前先解绑）
    if _index_exists(conn, acct, "uk_dfa_driver_ent"):
        conn.execute(text(f"ALTER TABLE `{acct}` DROP INDEX `uk_dfa_driver_ent`"))
    # 删除 driver_id 上的自动索引（index=True 生成）
    if _index_exists(conn, acct, "ix_biz_driver_fund_account_driver_id"):
        conn.execute(text(
            f"ALTER TABLE `{acct}` DROP INDEX `ix_biz_driver_fund_account_driver_id`"
        ))
    # 删除遗留 driver_id 列
    if _col_exists(conn, acct, "driver_id") and _col_exists(conn, acct, "owner_id"):
        conn.execute(text(f"ALTER TABLE `{acct}` DROP COLUMN `driver_id`"))
    # owner_id 索引（对齐 ORM index=True）
    if not _index_exists(conn, acct, "ix_biz_driver_fund_account_owner_id"):
        conn.execute(text(
            f"ALTER TABLE `{acct}` ADD INDEX "
            f"`ix_biz_driver_fund_account_owner_id` (`owner_id`)"
        ))
    # 新唯一键
    if not _index_exists(conn, acct, "uk_dfa_owner_ent"):
        conn.execute(text(
            f"ALTER TABLE `{acct}` ADD UNIQUE KEY `uk_dfa_owner_ent` "
            f"(`owner_type`, `owner_id`, `enterprise_id`)"
        ))

    # ---- 流水表 ----
    _migrate_owner(
        conn, txn,
        owner_type_comment="收款方类型 1-自有司机 2-承运商(预留) 3-社会运力（冗余）",
        owner_id_comment="收款方ID（冗余，便于按收款方查）",
    )
    if _index_exists(conn, txn, "idx_dft_driver"):
        conn.execute(text(f"ALTER TABLE `{txn}` DROP INDEX `idx_dft_driver`"))
    if _col_exists(conn, txn, "driver_id") and _col_exists(conn, txn, "owner_id"):
        conn.execute(text(f"ALTER TABLE `{txn}` DROP COLUMN `driver_id`"))
    if not _index_exists(conn, txn, "idx_dft_owner"):
        conn.execute(text(
            f"ALTER TABLE `{txn}` ADD INDEX `idx_dft_owner` "
            f"(`owner_type`, `owner_id`)"
        ))
