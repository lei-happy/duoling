"""biz_vehicle_ext: 自有车辆补充道路运输证字段（证照监控）

运力宝「证照监控」需要扫描自有车辆的道路运输证到期；社会运力车辆已有
transport_license_no/expire，自有车辆此前缺失，这里补齐。

幂等：information_schema 检测后再 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260615_001"
MIGRATION_NAME = "biz_vehicle_ext: add transport_license_no/expire"
REQUIRES_TABLES = ["biz_vehicle_ext"]

_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND column_name = :column_name
    LIMIT 1
    """
)


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    return (
        conn.execute(
            _EXISTS_SQL,
            {"table_name": table_name, "column_name": column_name},
        ).fetchone()
        is not None
    )


def upgrade(conn, tenant_code: str) -> None:
    if not _column_exists(conn, "biz_vehicle_ext", "transport_license_no"):
        conn.execute(
            text(
                "ALTER TABLE biz_vehicle_ext "
                "ADD COLUMN transport_license_no VARCHAR(50) NULL "
                "COMMENT '道路运输证号' "
                "AFTER inspection_expire"
            )
        )
    if not _column_exists(conn, "biz_vehicle_ext", "transport_license_expire"):
        conn.execute(
            text(
                "ALTER TABLE biz_vehicle_ext "
                "ADD COLUMN transport_license_expire DATE NULL "
                "COMMENT '道路运输证有效期' "
                "AFTER transport_license_no"
            )
        )
