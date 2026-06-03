"""biz_route: 驾车路线折线（地图预览，编辑回显）

幂等：information_schema 检测后再 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260603_001"
MIGRATION_NAME = "biz_route: add route_polyline"
REQUIRES_TABLES = ["biz_route"]

_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND column_name = :column_name
    LIMIT 1
    """
)


def upgrade(conn, tenant_code: str) -> None:
    exists = (
        conn.execute(
            _EXISTS_SQL,
            {"table_name": "biz_route", "column_name": "route_polyline"},
        ).fetchone()
        is not None
    )
    if not exists:
        conn.execute(
            text(
                "ALTER TABLE biz_route "
                "ADD COLUMN route_polyline TEXT NULL "
                "COMMENT '驾车路线折线 JSON：[[lng,lat],...]，供地图预览' "
                "AFTER waypoints"
            )
        )
