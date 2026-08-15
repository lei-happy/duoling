"""手工录入连接器（把单条表单当作 raw 进入管线）"""

from __future__ import annotations

from typing import List

from app.modules.client.services.energy.connectors.registry import (
    ConnectorContext,
    RawRecord,
    register_connector,
)


@register_connector(code="manual", name="手工录入", sync_modes=["manual"],
                    description="单条表单录入，走与导入相同的标准化/匹配管线")
class ManualConnector:
    async def fetch(self, ctx: ConnectorContext) -> List[RawRecord]:
        row = (ctx.extra or {}).get("row") or {}
        if not row:
            return []
        return [RawRecord(data=row, external_transaction_id=row.get("externalTransactionId"))]
