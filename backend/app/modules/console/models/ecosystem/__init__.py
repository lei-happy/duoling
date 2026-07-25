"""服务平台（生态）平台库模型

跨租户的撮合市场数据集中存放在平台库 ``zt_platform``，因为「每租户一库」的
物理隔离让大厅列表无法跨库分页排序。本目录 16 张表构成完整的撮合内核：

  挂牌 → 意向 → 成交 → 履约 → 评价

租户库侧只有一张 ``biz_eco_post_ref``（见 app/modules/client/models/ecosystem/），
用于记录源单与挂牌的关联关系，支撑任务单/运力列表的角标与联动判断。

设计文档：doc/02.需求文档/02.企业端/13.服务平台/
"""

from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest
from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost
from app.modules.console.models.ecosystem.capacity_post import SysEcoCapacityPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.post_view import SysEcoPostView
from app.modules.console.models.ecosystem.intent import (
    SysEcoIntent,
    SysEcoIntentMessage,
)
from app.modules.console.models.ecosystem.deal import (
    SysEcoDeal,
    SysEcoDealMilestone,
)
from app.modules.console.models.ecosystem.evaluation import SysEcoEvaluation
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.models.ecosystem.block_rule import SysEcoBlockRule
from app.modules.console.models.ecosystem.subscription import SysEcoSubscription
from app.modules.console.models.ecosystem.report import SysEcoReport

__all__ = [
    "SysEcoPost",
    "SysEcoPostDest",
    "SysEcoCargoPost",
    "SysEcoCapacityPost",
    "SysEcoPostAudit",
    "SysEcoPostView",
    "SysEcoIntent",
    "SysEcoIntentMessage",
    "SysEcoDeal",
    "SysEcoDealMilestone",
    "SysEcoEvaluation",
    "SysEcoTenantProfile",
    "SysEcoTenantCredit",
    "SysEcoBlockRule",
    "SysEcoSubscription",
    "SysEcoReport",
]
