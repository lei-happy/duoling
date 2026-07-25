"""
服务平台-我发布的 API

  - GET  /                       我发布的分页列表（含 Tab 角标计数）
  - GET  /{id}                   自己挂牌的详情（不限状态，带热度反馈）
  - PUT  /cargo/{id}             编辑货源挂牌
  - PUT  /capacity/{id}          编辑运力挂牌
  - POST /{id}/submit            提交审核（草稿 / 被驳回）
  - POST /{id}/delist            停止展示
  - POST /{id}/relist            重新上架
  - POST /{id}/extend            延长展示天数

## 为什么编辑分成两个端点

编辑要走 Builder 重建整份草稿（这样证照有效期、地区解析、标题生成这些规则在
编辑路径上一样生效），而两个大厅的表单结构不同。用一个端点接联合类型的 body，
类型校验会退化成运行时 if-else，前端也拿不到清晰的接口契约。分成两个端点后
仍在服务里校验 ``post_type`` 是否对得上，防止拿运力表单去改一条货源挂牌。

## 为什么不做删除

挂牌只有「停止展示」，没有删除。已经有人看过、甚至正在洽谈的信息凭空消失，
对方只会以为系统出错；审核与处置历史也会跟着断掉。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import BizException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import (
    get_current_user,
    get_platform_db,
    get_tenant_code,
    get_tenant_db,
)
from app.core.security import TokenData
from app.modules.client.schemas.ecosystem.post import (
    CapacityFormRequest,
    CargoFormRequest,
    PostDelistRequest,
    PostExtendRequest,
    PostSubmitRequest,
)
from app.modules.client.services.company_activity_service import (
    CompanyActivityService,
)
from app.modules.client.services.ecosystem.capacity_draft_builder import (
    CapacityDraftBuilder,
)
from app.modules.client.services.ecosystem.cargo_draft_builder import CargoDraftBuilder
from app.modules.client.services.ecosystem.hall_facade import EcoHallFacade
from app.modules.client.services.ecosystem.post_manage_service import (
    EcoPostManageService,
    ManageResult,
)
from app.modules.client.services.ecosystem.post_query_service import (
    MyPostFilter,
    resolve_status_group,
)
from app.modules.client.services.ecosystem.publish_context import (
    EcoPublishContextService,
)
from app.modules.client.services.ecosystem.region_resolver import RegionResolver
from app.modules.console.models.ecosystem.constants import PostType

router = APIRouter()


def _manage_payload(result: ManageResult) -> dict:
    return {
        "postId": result.post_id,
        "postNo": result.post_no,
        "status": result.status,
        "auditStatus": result.audit_status,
        # 前端据此决定提示语：留在大厅里，还是被撤回去重审了
        "requireReaudit": result.require_reaudit,
        "changedLabels": result.changed_labels,
        "invalidatedIntentCount": len(result.invalidated_intents),
        "validUntil": (
            result.valid_until.strftime("%Y-%m-%d %H:%M")
            if result.valid_until
            else None
        ),
        "refSynced": result.ref_synced,
    }


async def _operator_name(tenant_db: AsyncSession, user_id: Optional[int]):
    return await CompanyActivityService.actor_display_name(tenant_db, user_id)


# ---------------------------------------------------------------------------
# 列表与详情
# ---------------------------------------------------------------------------


@router.get("")
async def page_my_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    postType: Optional[int] = Query(None),
    statusGroup: Optional[str] = Query(None, description="Tab 键：draft/auditing/..."),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    _: TokenData = Depends(get_current_user),
):
    """我发布的

    按 Tab 键而不是原始状态值过滤：「进行中」在库里是已锁定 + 履约中两个状态，
    让前端自己拼状态数组，两端的分组口径迟早会不一致。
    """
    flt = MyPostFilter(
        page=page,
        page_size=page_size,
        post_type=postType,
        statuses=resolve_status_group(statusGroup),
        keyword=keyword,
    )
    data = await EcoHallFacade.page_mine(db, owner_tenant_code=tenant_code, flt=flt)
    return success(data=data)


@router.get("/{post_id}")
async def my_post_detail(
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    tenant_code: str = Depends(get_tenant_code),
    _: TokenData = Depends(get_current_user),
):
    """自己挂牌的详情"""
    data = await EcoHallFacade.mine_detail(
        db, post_id=post_id, owner_tenant_code=tenant_code
    )
    await _attach_region_ids(tenant_db, data)
    return success(data=data)


async def _attach_region_ids(tenant_db: AsyncSession, data: dict) -> None:
    """补上编辑弹层要用的 ``fromRegionId`` / ``toRegionIds``

    运力挂牌的所在地与期望流向是发布时用户选的（运力档案里没有实时位置），而编辑
    要走 Builder 重建整份草稿，就得把当初选的地区原样传回来。平台库存的是区划代码
    与省市名，所以在这里翻回租户库 ID——否则前端只有「四川省 成都市」这样的名字，
    回填不出选中项，用户每改一次报价都得重新选一遍线路。
    """
    dest_codes = [d.get("regionCode") for d in (data.get("destinations") or [])]
    from_code = data.get("fromRegionCode")
    mapping = await RegionResolver.ids_by_codes(tenant_db, [from_code, *dest_codes])
    data["fromRegionId"] = mapping.get(int(from_code)) if from_code else None
    data["toRegionIds"] = [
        mapping[int(c)] for c in dest_codes if c and int(c) in mapping
    ]


# ---------------------------------------------------------------------------
# 编辑
# ---------------------------------------------------------------------------


@router.put("/cargo/{post_id}")
@operation_log(module="服务平台", action="编辑货源挂牌", description="编辑已发布的货源挂牌")
async def edit_cargo_post(
    request: Request,
    data: CargoFormRequest,
    post_id: int = Path(..., gt=0),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """编辑货源挂牌

    源单 ID 取自挂牌本身，不接受前端传：否则用户可以把一条已上架挂牌的源单
    悄悄换成另一张任务单，运营的源单一致性核查就白做了。
    """
    post = await EcoHallFacade.load_own_post(
        platform_db, post_id=post_id, owner_tenant_code=tenant_code
    )
    _assert_post_type(post, PostType.CARGO)
    task_id = _require_source_id(post, hint="任务单")

    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    draft = await CargoDraftBuilder.build(
        tenant_db, task_id=task_id, form=data.to_form()
    )
    precheck = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, draft=draft, exclude_post_id=post_id
    )
    result = await EcoPostManageService.edit(
        tenant_db=tenant_db,
        platform_db=platform_db,
        post_id=post_id,
        owner=EcoPublishContextService.owner(
            ctx,
            user_id=current_user.user_id,
            user_name=await _operator_name(tenant_db, current_user.user_id),
        ),
        draft=draft,
        precheck=precheck,
    )
    return success(data=_manage_payload(result), message=result.message)


@router.put("/capacity/{post_id}")
@operation_log(module="服务平台", action="编辑运力挂牌", description="编辑已发布的运力挂牌")
async def edit_capacity_post(
    request: Request,
    data: CapacityFormRequest,
    post_id: int = Path(..., gt=0),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """编辑运力挂牌"""
    post = await EcoHallFacade.load_own_post(
        platform_db, post_id=post_id, owner_tenant_code=tenant_code
    )
    _assert_post_type(post, PostType.CAPACITY)
    capacity_id = _require_source_id(post, hint="运力档案")

    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    draft = await CapacityDraftBuilder.build(
        tenant_db, capacity_id=capacity_id, form=data.to_form()
    )
    precheck = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, draft=draft, exclude_post_id=post_id
    )
    result = await EcoPostManageService.edit(
        tenant_db=tenant_db,
        platform_db=platform_db,
        post_id=post_id,
        owner=EcoPublishContextService.owner(
            ctx,
            user_id=current_user.user_id,
            user_name=await _operator_name(tenant_db, current_user.user_id),
        ),
        draft=draft,
        precheck=precheck,
    )
    return success(data=_manage_payload(result), message=result.message)


# ---------------------------------------------------------------------------
# 状态流转
# ---------------------------------------------------------------------------


@router.post("/{post_id}/submit")
@operation_log(module="服务平台", action="提交审核", description="将挂牌提交审核")
async def submit_post(
    request: Request,
    data: PostSubmitRequest,
    post_id: int = Path(..., gt=0),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """提交审核"""
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    precheck = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, exclude_post_id=post_id
    )
    result = await EcoPostManageService.submit(
        tenant_db=tenant_db,
        platform_db=platform_db,
        post_id=post_id,
        owner=EcoPublishContextService.owner(
            ctx,
            user_id=current_user.user_id,
            user_name=await _operator_name(tenant_db, current_user.user_id),
        ),
        precheck=precheck,
        valid_days=data.validDays,
    )
    return success(data=_manage_payload(result), message=result.message)


@router.post("/{post_id}/delist")
@operation_log(module="服务平台", action="停止展示", description="停止挂牌在大厅的展示")
async def delist_post(
    request: Request,
    data: PostDelistRequest,
    post_id: int = Path(..., gt=0),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """停止展示

    正在洽谈的意向会一并失效，返回值里带条数，前端要在确认弹层里先告知——
    「有 3 位同行正在与你洽谈，停止展示会一并结束这些洽谈」。
    """
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    result = await EcoPostManageService.delist(
        tenant_db=tenant_db,
        platform_db=platform_db,
        post_id=post_id,
        owner=EcoPublishContextService.owner(
            ctx,
            user_id=current_user.user_id,
            user_name=await _operator_name(tenant_db, current_user.user_id),
        ),
        remark=data.remark,
    )
    return success(data=_manage_payload(result), message=result.message)


@router.post("/{post_id}/relist")
@operation_log(module="服务平台", action="重新上架", description="将已下架挂牌重新上架")
async def relist_post(
    request: Request,
    data: PostSubmitRequest,
    post_id: int = Path(..., gt=0),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """重新上架

    一律回待审核，免审白名单在这里不生效：白名单是对租户历史表现的信任，
    而被下架过的恰恰是这条内容本身。
    """
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    precheck = await EcoPublishContextService.load_precheck(
        platform_db, ctx=ctx, exclude_post_id=post_id
    )
    result = await EcoPostManageService.relist(
        tenant_db=tenant_db,
        platform_db=platform_db,
        post_id=post_id,
        owner=EcoPublishContextService.owner(
            ctx,
            user_id=current_user.user_id,
            user_name=await _operator_name(tenant_db, current_user.user_id),
        ),
        valid_days=data.validDays,
        precheck=precheck,
    )
    return success(data=_manage_payload(result), message=result.message)


@router.post("/{post_id}/extend")
@operation_log(module="服务平台", action="延长展示", description="延长挂牌展示天数")
async def extend_post(
    request: Request,
    data: PostExtendRequest,
    post_id: int = Path(..., gt=0),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    current_user: TokenData = Depends(get_current_user),
):
    """延长展示天数（只对展示中的挂牌有效，不触发重审）"""
    ctx = await EcoPublishContextService.load_tenant(platform_db, tenant_code)
    result = await EcoPostManageService.extend(
        platform_db=platform_db,
        post_id=post_id,
        owner=EcoPublishContextService.owner(
            ctx,
            user_id=current_user.user_id,
            user_name=await _operator_name(tenant_db, current_user.user_id),
        ),
        days=data.days,
    )
    return success(data=_manage_payload(result), message=result.message)


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------


def _assert_post_type(post, expected: int) -> None:
    if int(post.post_type) != int(expected):
        raise BizException("挂牌类型不对，请刷新页面后重试")


def _require_source_id(post, *, hint: str) -> int:
    """编辑必须有源单

    手工录入的挂牌一期不支持编辑：没有源单就没有 Builder，无法重建草稿，
    也就跑不了证照与地址校验。硬改成「只改传上来的字段」等于给手工挂牌开一条
    不做校验的编辑通道。
    """
    if not post.source_id:
        raise BizException(f"这条挂牌没有关联的{hint}，暂时不支持修改，请停止展示后重新发布")
    return int(post.source_id)
