"""
AI 数字员工模块 ORM 模型

平台库（PlatformBase，跨租户共用）：
- AiEmployee          : 数字员工角色定义
- AiTool              : 工具元数据（与代码 @register_tool 对齐）
- AiEmployeeTool      : 数字员工 ↔ 工具多对多绑定
- AiPromptTemplate    : 提示词模板
- AiModelProvider     : LLM Provider 配置

租户业务库（TenantBase，__table_tier__="business"）：
- BizAiSession        : 会话主表
- BizAiMessage        : 消息明细
- BizAiToolCallLog    : 工具调用细粒度审计
- BizAiContext        : 会话/用户上下文记忆 KV
"""

from app.modules.ai.models.platform.ai_employee import AiEmployee
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool
from app.modules.ai.models.platform.ai_prompt_template import AiPromptTemplate
from app.modules.ai.models.platform.ai_model_provider import AiModelProvider

from app.modules.ai.models.tenant.biz_ai_session import BizAiSession
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.models.tenant.biz_ai_tool_call_log import BizAiToolCallLog
from app.modules.ai.models.tenant.biz_ai_context import BizAiContext

__all__ = [
    "AiEmployee",
    "AiTool",
    "AiEmployeeTool",
    "AiPromptTemplate",
    "AiModelProvider",
    "BizAiSession",
    "BizAiMessage",
    "BizAiToolCallLog",
    "BizAiContext",
]
