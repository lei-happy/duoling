"""连接器包：导入即注册"""

from app.modules.client.services.energy.connectors import excel  # noqa: F401
from app.modules.client.services.energy.connectors import http_api_template  # noqa: F401
from app.modules.client.services.energy.connectors import manual  # noqa: F401
from app.modules.client.services.energy.connectors.registry import (
    ConnectorContext,
    create_connector,
    list_connectors,
    register_connector,
)

__all__ = [
    "ConnectorContext",
    "create_connector",
    "list_connectors",
    "register_connector",
]
