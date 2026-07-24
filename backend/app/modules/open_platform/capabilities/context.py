"""能力执行上下文"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OpenContext:
    """由数据面鉴权后注入，贯穿能力执行与审计。"""

    tenant_code: str
    channel: str = "api"  # api / mcp
    app_id: Optional[int] = None
    credential_id: Optional[int] = None
    request_id: str = ""
    scope: List[str] = field(default_factory=list)
    client_ip: str = ""
    user_agent: str = ""
