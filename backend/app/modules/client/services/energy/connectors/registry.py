"""能源连接器注册表（仿 open_platform capabilities）"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


@dataclass
class ConnectorContext:
    supplier_id: int
    account_id: Optional[int] = None
    auth_config: Optional[dict] = None
    field_mapping: Optional[dict] = None
    cursor: Optional[str] = None
    extra: dict = field(default_factory=dict)


@dataclass
class RawRecord:
    data: dict
    external_transaction_id: Optional[str] = None


@dataclass
class ConnectorSpec:
    code: str
    name: str
    sync_modes: List[str]
    factory: Callable
    description: str = ""


_REGISTRY: Dict[str, ConnectorSpec] = {}


def register_connector(*, code: str, name: str, sync_modes: Optional[List[str]] = None, description: str = ""):
    def _decorator(cls):
        if code in _REGISTRY:
            logger.warning(f"连接器重复注册，后者覆盖前者: {code}")
        _REGISTRY[code] = ConnectorSpec(
            code=code,
            name=name,
            sync_modes=sync_modes or ["manual"],
            factory=cls,
            description=description,
        )
        return cls
    return _decorator


def get_connector(code: str) -> Optional[ConnectorSpec]:
    return _REGISTRY.get(code)


def list_connectors() -> List[ConnectorSpec]:
    return sorted(_REGISTRY.values(), key=lambda s: s.code)


def create_connector(code: str) -> Any:
    spec = get_connector(code)
    if spec is None:
        raise ValueError(f"未知连接器: {code}")
    return spec.factory()
