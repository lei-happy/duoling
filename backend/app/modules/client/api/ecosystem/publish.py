"""
服务平台-发布挂牌 API

  - GET  /options              发布弹层的默认值与可选项（含大厅能力状态）
  - POST /cargo/preview        发布前试算：能不能发、自动标题长什么样
  - POST /capacity/preview     同上（运力）
  - POST /cargo                发布货源
  - POST /capacity             发布运力

## 一次发布固定四步

1. ``load_tenant``：取发布方身份（认证、白名单、大厅能力）
2. ``Builder.build``：读源单、校验、拼草稿——**源单里的线路时间台数不接受前端传**
3. ``load_precheck``：取需要查库的预检素材（敏感词库、近 24h 发布数…）
4. ``publish``：双库写入

第 2 步的校验（任务单状态、证照有效期、地址完整度）与第 3 步的预检
（联系方式夹带、敏感词、刷屏）是两类不同的门：前者管「这单本身能不能发」，
后者管「这段内容能不能公开」。两者都不能省，也不能互相替代。

## 门控为什么按大厅分别挂

``ecosystem_cargo_publish`` 与 ``ecosystem_capacity_publish`` 是两个 feature，
版本可以只开一个（只找车的公司不需要发货源）。所以门控挂在端点上而不是
整个 router 上。
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import (
    get_current_user,
    get_platform_db,
    get_tenant_code,
    get_tenant_db,
)
from app.core.permissions import require_feature
from app.core.security import TokenData
from app.modules.client.schemas.ecosystem.post import (
    CapacityPreviewRequest,
    CapacityPublishRequest,
    CargoPreviewRequest,
    CargoPublishRequest,
)
from app.modules.client.services.company_activity_service import (
    CompanyActivityService,
)
from app.modules.client.services.ecosystem.capacity_draft_builder import (
    CapacityDraftBuilder,
)
from app.modules.client.services.ecosystem.cargo_draft_builder import CargoDraftBuilder
from app.modules.client.services.ecosystem.content_guard import PrecheckResult
from app.modules.client.services.ecosystem.post_draft import (
    PostDraft,
    run_draft_precheck,
)
from app.modules.client.services.ecosystem.publish_context import (
    EcoPublishContextService,
)
from app.modules.client.services.ecosystem.publish_service import (
    EcoPublishService,
    PublishResult,
)
from app.modules.console.models.ecosystem.constants import (
    COOPERATION_TYPE_LABELS,
    DEFAULT_VALID_DAYS,
    PRICE_TYPE_LABELS,
    SETTLE_TYPE_LABELS,
    VALID_DAYS_OPTIONS,
)

router = APIRouter()


def _options(labels: dict) -> list:
    return [{"value": k, "label": v} for k, v in labels.items()]

CARGO_FEATURE = "ecosystem_cargo_publish"
CAPACITY_FEATURE = "ecosystem_capacity_publish"


# ---------------------------------------------------------------------------
# 出参装配
# ---------------------------------------------------------------------------


def _publish_payload(result: PublishResult) -> Dict[str, Any]:
    return {
        "postId": result.post_id,
        "postNo": result.post_no,
        "status": result.status,
        "auditStatus": result.audit_status,
        # 免审直通与进审核队列，前端的后续引导完全不同（去大厅看看 / 等审核结果）
        "autoListed": result.auto_listed,
        "suspiciousFlags": result.suspicious_flags,
        # 角标同步失败不是发布失败，前端不用报错，巡检会补
        "refSynced": result.ref_synced,
    }


def _preview_payload(draft: PostDraft, precheck: PrecheckResult) -> Dict[str, Any]:
    """试算结果

    ``blocked`` 为 True 时前端应禁用发布按钮并展示 ``blockMessage``，
    但**不要把它当错误弹窗**：用户还没提交，这只是提前告知。
    """
    return {
        "title": draft.title,
        "fromProvince": draft.from_province,
        "fromCity": draft.from_city,
        "fromName": draft.from_name,
        "toProvince": draft.to_province,
        "toCity": draft.to_city,
        "toName": draft.to_name,
        "anyDirection": draft.any_direction,
        "destinations": [
            {"province": d.province, "city": d.city} for d in draft.destinations
        ],
        "windowStart": (
            draft.window_start.strftime("%Y-%m-%d %H:%M") if draft.window_start else None
        ),
        "windowEnd": (
            draft.window_end.strftime("%Y-%m-%d %H:%M") if draft.window_end else None
        ),
        "totalQuantity": draft.total_quantity,
        "quantityUnit": draft.quantity_unit,
        "sourceType": draft.source_type,
        "sourceId": draft.source_id,
        "precheck": {
            "blocked": precheck.blocked,
            "blockMessage": precheck.block_message,
            # 只回一个「需要人工看一眼」的布尔值。具体命中了哪条可疑规则
            # （近 24h 发了几条、注册多少天、报价偏离多少）是给审核员的判断依据，
            # 回给发布方等于把风控说明书发给想绕过它的人
            "needsReview": bool(precheck.suspicious_flags),
        },
    }


# ---------------------------------------------------------------------------
# 发布弹层的默认值
# ---------------------------------------------------------------------------


@router.get("/options")
async def publish_options(
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    _: TokenData = Depends(get_current_user),
):
    """发布弹层默认值

    ``hallEnabled`` 为 false 时前端应在入口处就说明原因，而不是等用户填完
    整个表单再告诉他不能发。
    """
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    return success(
        data={
            "hallEnabled": ctx.hall_enabled,
            "disabledReason": ctx.disabled_reason,
            "licenseVerified": ctx.license_verified,
            # 免审白名单的租户发布后直接展示，提示语要跟着变
            "auditWhitelist": ctx.audit_whitelist,
            "validDaysOptions": list(VALID_DAYS_OPTIONS),
            # 计价 / 合作 / 结算的中文名由后端下发，与大厅筛选同一份（constants）：
            # 让发布弹层自己写一套，很快就会出现大厅叫「按台」、发布叫「每台」
            "priceTypes": _options(PRICE_TYPE_LABELS),
            "cooperationTypes": _options(COOPERATION_TYPE_LABELS),
            "settleTypes": _options(SETTLE_TYPE_LABELS),
            "defaultValidDays": ctx.default_valid_days or DEFAULT_VALID_DAYS,
            "defaultVisibilityLevel": ctx.default_visibility_level,
            "defaultContactVisibility": ctx.default_contact_visibility,
            "defaultContactName": ctx.default_contact_name,
            "defaultContactPhone": ctx.default_contact_phone,
            "maskedName": ctx.display_masked_name,
        }
    )


# ---------------------------------------------------------------------------
# 试算
# ---------------------------------------------------------------------------


@router.post("/cargo/preview", dependencies=[Depends(require_feature(CARGO_FEATURE))])
async def preview_cargo(
    data: CargoPreviewRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    _: TokenData = Depends(get_current_user),
):
    """货源发布前试算"""
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    draft = await CargoDraftBuilder.build(
        tenant_db, task_id=data.taskId, form=data.to_form()
    )
    precheck_input = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, draft=draft
    )
    precheck = run_draft_precheck(draft, precheck_input, precheck_input.now)
    return success(data=_preview_payload(draft, precheck))


@router.post(
    "/capacity/preview", dependencies=[Depends(require_feature(CAPACITY_FEATURE))]
)
async def preview_capacity(
    data: CapacityPreviewRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    _: TokenData = Depends(get_current_user),
):
    """运力发布前试算"""
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    draft = await CapacityDraftBuilder.build(
        tenant_db, capacity_id=data.capacityId, form=data.to_form()
    )
    precheck_input = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, draft=draft
    )
    precheck = run_draft_precheck(draft, precheck_input, precheck_input.now)
    return success(data=_preview_payload(draft, precheck))


# ---------------------------------------------------------------------------
# 发布
# ---------------------------------------------------------------------------


@router.post("/cargo", dependencies=[Depends(require_feature(CARGO_FEATURE))])
@operation_log(module="服务平台", action="发布货源", description="发布货源到货源大厅")
async def publish_cargo(
    request: Request,
    data: CargoPublishRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """发布货源到货源大厅"""
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    await EcoPublishContextService.ensure_profile(platform_db, ctx)

    draft = await CargoDraftBuilder.build(
        tenant_db, task_id=data.taskId, form=data.to_form()
    )
    precheck = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, draft=draft
    )
    operator_name = await CompanyActivityService.actor_display_name(
        tenant_db, current_user.user_id
    )
    result = await EcoPublishService.publish(
        tenant_db=tenant_db,
        platform_db=platform_db,
        draft=draft,
        publisher=EcoPublishContextService.publisher(
            ctx, user_id=current_user.user_id, user_name=operator_name
        ),
        precheck=precheck,
    )
    return success(data=_publish_payload(result), message=result.message)


@router.post("/capacity", dependencies=[Depends(require_feature(CAPACITY_FEATURE))])
@operation_log(module="服务平台", action="发布运力", description="发布空闲运力到运力大厅")
async def publish_capacity(
    request: Request,
    data: CapacityPublishRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """发布空闲运力到运力大厅"""
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    await EcoPublishContextService.ensure_profile(platform_db, ctx)

    draft = await CapacityDraftBuilder.build(
        tenant_db, capacity_id=data.capacityId, form=data.to_form()
    )
    precheck = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, draft=draft
    )
    operator_name = await CompanyActivityService.actor_display_name(
        tenant_db, current_user.user_id
    )
    result = await EcoPublishService.publish(
        tenant_db=tenant_db,
        platform_db=platform_db,
        draft=draft,
        publisher=EcoPublishContextService.publisher(
            ctx, user_id=current_user.user_id, user_name=operator_name
        ),
        precheck=precheck,
    )
    return success(data=_publish_payload(result), message=result.message)
