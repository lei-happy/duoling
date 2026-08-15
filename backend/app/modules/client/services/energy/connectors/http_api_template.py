"""HTTP API 连接器样板

拿到某家供应商（中石油 / 万金油 / G7 等）的接口文档后：
1. 复制本文件，改 ``code`` / ``name``
2. 在 ``_build_request`` 填鉴权、分页、游标
3. 在 ``_parse_page`` 把响应拆成 dict 列表
4. 字段差异用连接器实例上的 ``field_mapping_json`` 配置，不要写死在代码里

本类默认不发起真实请求（避免误连外部系统）；子类覆盖 ``_do_get`` 即可。
"""

from __future__ import annotations

from typing import Any, List, Optional

from loguru import logger

from app.modules.client.services.energy.connectors.registry import (
    ConnectorContext,
    RawRecord,
    register_connector,
)


@register_connector(
    code="http_api",
    name="HTTP API 样板",
    sync_modes=["interval", "cron", "manual"],
    description="三方 HTTP 拉取骨架：分页、游标断点、重试。复制后按供应商文档实现。",
)
class HttpApiConnectorTemplate:
    max_pages = 50
    max_retries = 3

    async def fetch(self, ctx: ConnectorContext) -> List[RawRecord]:
        records: List[RawRecord] = []
        cursor = ctx.cursor
        for page in range(self.max_pages):
            payload = self._build_request(ctx, cursor, page)
            data = await self._do_get(payload)
            if data is None:
                break
            rows, next_cursor, exhausted = self._parse_page(data)
            for row in rows:
                records.append(RawRecord(
                    data=row,
                    external_transaction_id=row.get("externalTransactionId") or row.get("id"),
                ))
            cursor = next_cursor
            if exhausted or not rows:
                break
        ctx.cursor = cursor
        return records

    def _build_request(self, ctx: ConnectorContext, cursor: Optional[str], page: int) -> dict:
        """子类覆盖：拼 URL / headers / query。"""
        auth = ctx.auth_config or {}
        return {
            "url": auth.get("baseUrl") or "",
            "headers": {"Authorization": auth.get("token") or ""},
            "params": {"cursor": cursor, "page": page + 1},
        }

    async def _do_get(self, payload: dict) -> Optional[Any]:
        """样板默认不发请求。子类用 httpx 实现，并自行重试。"""
        logger.info(
            "[HttpApiConnectorTemplate] 样板未发起真实请求，"
            f"url={payload.get('url')!r}。复制本类并覆盖 _do_get。"
        )
        return None

    def _parse_page(self, data: Any) -> tuple[list[dict], Optional[str], bool]:
        """返回 (rows, next_cursor, exhausted)。"""
        if isinstance(data, dict):
            rows = data.get("list") or data.get("data") or []
            cursor = data.get("nextCursor") or data.get("cursor")
            exhausted = not bool(data.get("hasMore", not rows))
            return list(rows), cursor, exhausted
        if isinstance(data, list):
            return data, None, True
        return [], None, True
