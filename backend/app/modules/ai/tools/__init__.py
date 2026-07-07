"""
工具中心 Tool Hub

设计：
- 工具实现：代码内 @register_tool 装饰器（混合扩展模式）
- 工具元数据：启动时反射 upsert 到 ai_tool 表
- 工具调用：进程内直调 Service 层（高性能、共享 tenant Session）

按业务域拆文件：waybill_tools / vehicle_tools / customer_tools / file_tools / ...
"""

from app.modules.ai.tools.registry import (
    ToolRegistry,
    register_tool,
    get_registry,
)
from app.modules.ai.tools.base import ToolContext, ToolResult, ToolSpec

__all__ = [
    "ToolRegistry",
    "register_tool",
    "get_registry",
    "ToolContext",
    "ToolResult",
    "ToolSpec",
]


def import_all_tools() -> None:
    """显式 import 所有工具模块，触发 @register_tool 注册"""
    from app.modules.ai.tools import waybill_tools  # noqa: F401
    from app.modules.ai.tools import vehicle_tools  # noqa: F401
    from app.modules.ai.tools import customer_tools  # noqa: F401
    from app.modules.ai.tools import file_tools  # noqa: F401
    from app.modules.ai.tools import image_tools  # noqa: F401
