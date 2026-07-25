"""服务平台（生态）平台库侧 Service

这些 Service 操作平台库 ``sys_eco_*``，被租户端与运营端共同调用：
编号生成、审核流转、意向失效等都是跨端共享的能力，放在 console 侧统一维护，
避免两端各写一份而出现规则漂移。

模块分工：

| 模块 | 职责 |
|------|------|
| ``eco_number_service`` | 业务编号生成（Redis 自增 + 库内兜底） |
| ``audit_sla`` | 工作时段口径的审核时效计算（纯逻辑） |
| ``intent_lifecycle`` | 挂牌下架时的意向收口（四条下架路径共用） |
| ``audit_query_service`` | 审核台取数：待审 / 抽检 / 全量 / 租户档案 |
| ``audit_service`` | 审核动作：通过 / 驳回 / 批量 / 强制下架 / 抽检 |
| ``whitelist_service`` | 免审白名单资格判定与授予 / 移出 |
| ``audit_serializer`` | 审核台序列化（不脱敏，与租户端那套刻意分开） |
| ``audit_facade`` | 审核台读接口装配：取数 → 批量装载 → 序列化 |
"""

from app.modules.console.services.ecosystem import audit_sla
from app.modules.console.services.ecosystem.audit_facade import EcoAuditFacade
from app.modules.console.services.ecosystem.audit_query_service import (
    AuditPostFilter,
    AuditQueueRow,
    BacklogStats,
    EcoAuditQueryService,
    OpsContext,
    TenantAuditStats,
)
from app.modules.console.services.ecosystem.audit_service import (
    REJECT_TEMPLATES,
    AuditResult,
    BatchAuditResult,
    EcoAuditService,
    FailedItem,
)
from app.modules.console.services.ecosystem.audit_serializer import (
    AUDIT_ACTION_LABELS,
    AUDIT_STATUS_LABELS,
    POST_TYPE_LABELS,
    EcoAuditSerializer,
)
from app.modules.console.services.ecosystem.eco_number_service import (
    EcoNumberService,
)
from app.modules.console.services.ecosystem.intent_lifecycle import (
    InvalidatedIntent,
    invalidate_active_intents,
    recount_active_intents,
)
from app.modules.console.services.ecosystem.whitelist_service import (
    CheckItem,
    EcoWhitelistService,
    EligibilityResult,
    WhitelistCheck,
    WhitelistResult,
)

__all__ = [
    "EcoNumberService",
    "audit_sla",
    # 取数
    "AuditPostFilter",
    "AuditQueueRow",
    "BacklogStats",
    "EcoAuditQueryService",
    "OpsContext",
    "TenantAuditStats",
    # 审核动作
    "AuditResult",
    "BatchAuditResult",
    "EcoAuditService",
    "FailedItem",
    "REJECT_TEMPLATES",
    # 审核台装配与序列化
    "EcoAuditFacade",
    "EcoAuditSerializer",
    "AUDIT_ACTION_LABELS",
    "AUDIT_STATUS_LABELS",
    "POST_TYPE_LABELS",
    # 意向收口
    "InvalidatedIntent",
    "invalidate_active_intents",
    "recount_active_intents",
    # 白名单
    "CheckItem",
    "EcoWhitelistService",
    "EligibilityResult",
    "WhitelistCheck",
    "WhitelistResult",
]
