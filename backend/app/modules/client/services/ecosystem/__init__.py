"""服务平台（生态）租户端 Service

安全核心的三块都是**纯逻辑、零 DB**，可被穷举单测：

- ``visibility`` / ``serializer``：字段可见性唯一实现点（分层脱敏）
- ``post_query_service``：大厅可见范围唯一收口点（屏蔽名单、状态与有效期）
- ``content_guard``：发布预检（联系方式硬拦截、敏感词、可疑标红）

发布链路同样把「算什么」与「写哪儿」分开，纯逻辑部分照样零 DB：

- ``region_resolver``：租户 ``region_id`` → 省/市/区 + 行政区划代码
- ``title_builder``：标题自动生成（纯函数）
- ``post_draft``：类型无关的落库中间表示，让内核不出现 ``if post_type``
- ``cargo_draft_builder`` / ``capacity_draft_builder``：源单 → 草稿，
  货源与运力的差异全部收敛在这里
- ``publish_service``：平台库 + 租户库双写、查重、快照镜像

发布之后的生命周期同样把规则与落库分开：

- ``post_state_machine``：合法流转的唯一判定点（纯逻辑）
- ``post_edit_policy``：改了什么决定要不要重审（纯逻辑）
- ``post_manage_service``：编辑 / 提交 / 停止展示 / 重新上架 / 延长展示
- ``post_ref_sync``：挂牌状态回写租户库镜像（失败不阻断，交巡检补偿）

下架时的意向收口在 ``console.services.ecosystem.intent_lifecycle``：
主动下架、强制下架、到期下架、源单失效下架四条路径共用一份，
各写一份的结果一定是某条路径漏掉意向失效。

面向 API 层的两个装配件，让路由函数不必自己编排多步流程：

- ``publish_context``：发布人身份 + 预检素材里需要查库的那一半
- ``hall_facade``：查询 → 批量装载 → 查看方上下文 → 序列化，四步固定顺序

其余模块负责查询编排与状态流转。
"""

from app.modules.client.services.ecosystem.capacity_draft_builder import (
    CapacityDraftBuilder,
    CapacityPublishForm,
)
from app.modules.client.services.ecosystem.cargo_draft_builder import (
    CargoDraftBuilder,
    CargoPublishForm,
)
from app.modules.client.services.ecosystem.content_guard import (
    PrecheckInput,
    PrecheckResult,
    SensitiveWordRule,
    run_precheck,
)
from app.modules.client.services.ecosystem.hall_facade import EcoHallFacade
from app.modules.client.services.ecosystem.post_draft import (
    DestDraft,
    PostDraft,
    run_draft_precheck,
)
from app.modules.client.services.ecosystem.post_edit_policy import (
    EditDiff,
    ReauditTier,
    build_diff,
)
from app.modules.client.services.ecosystem.post_manage_service import (
    EcoPostManageService,
    InvalidatedIntent,
    ManageResult,
    OwnerContext,
)
from app.modules.client.services.ecosystem.post_query_service import (
    EcoPostQueryService,
    HallFilter,
    MyPostFilter,
    resolve_status_group,
)
from app.modules.client.services.ecosystem.post_ref_sync import mirror_post_status
from app.modules.client.services.ecosystem.post_state_machine import (
    ALLOWED_TRANSITIONS,
    assert_transit,
    can_transit,
    is_editable,
)
from app.modules.client.services.ecosystem.publish_context import (
    EcoPublishContextService,
    TenantHallContext,
)
from app.modules.client.services.ecosystem.publish_service import (
    EcoPublishService,
    PublisherContext,
    PublishResult,
)
from app.modules.client.services.ecosystem.region_resolver import (
    RegionResolver,
    ResolvedRegion,
)
from app.modules.client.services.ecosystem.serializer import EcoPostSerializer
from app.modules.client.services.ecosystem.title_builder import (
    build_capacity_title,
    build_cargo_title,
)
from app.modules.client.services.ecosystem.viewer_context import (
    EcoViewerContextBuilder,
)
from app.modules.client.services.ecosystem.visibility import (
    EcoViewerContext,
    ViewerLevel,
    mask_company_name,
    resolve_level,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "CapacityDraftBuilder",
    "CapacityPublishForm",
    "CargoDraftBuilder",
    "CargoPublishForm",
    "DestDraft",
    "EcoHallFacade",
    "EcoPostManageService",
    "EcoPostQueryService",
    "EcoPostSerializer",
    "EcoPublishContextService",
    "EcoPublishService",
    "EcoViewerContext",
    "EcoViewerContextBuilder",
    "EditDiff",
    "HallFilter",
    "InvalidatedIntent",
    "ManageResult",
    "MyPostFilter",
    "OwnerContext",
    "PostDraft",
    "PrecheckInput",
    "PrecheckResult",
    "PublishResult",
    "PublisherContext",
    "ReauditTier",
    "RegionResolver",
    "ResolvedRegion",
    "SensitiveWordRule",
    "TenantHallContext",
    "ViewerLevel",
    "assert_transit",
    "build_capacity_title",
    "build_cargo_title",
    "build_diff",
    "can_transit",
    "is_editable",
    "mask_company_name",
    "mirror_post_status",
    "resolve_level",
    "resolve_status_group",
    "run_draft_precheck",
    "run_precheck",
]
