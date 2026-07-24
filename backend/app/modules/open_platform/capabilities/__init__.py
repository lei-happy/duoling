"""能力目录：注册表 + 内置能力

导入本包即触发内置能力注册（builtin 内的 @register_capability 生效）。
"""

from app.modules.open_platform.capabilities import builtin  # noqa: F401
from app.modules.open_platform.capabilities.registry import (
    register_capability,
    get_capability,
    list_capabilities,
    dispatch,
    CapabilitySpec,
)
from app.modules.open_platform.capabilities.context import OpenContext

__all__ = [
    "register_capability",
    "get_capability",
    "list_capabilities",
    "dispatch",
    "CapabilitySpec",
    "OpenContext",
]
