"""
服务平台-货源/运力大厅 API

  - GET  /              大厅分页列表
  - GET  /filters       筛选项元数据（排序方式、展示天数、货物类别等）
  - GET  /{id}          挂牌详情（记一次浏览）

## 两个大厅共用一份实现

货源与运力的列表字段、筛选维度、排序方式高度同构，差异都收在
``sys_eco_cargo_post`` / ``sys_eco_capacity_post`` 两张扩展表里，由查询与序列化
按 ``post_type`` 分流。所以这里用 ``build_hall_router(post_type)`` 生成两个
router，而不是把同一段代码抄两遍——抄两遍的下场是某次给货源大厅加了个筛选项，
运力大厅忘了加，用户看到两个界面行为不一致。

功能门控在 ``client/api/__init__.py`` 挂载时按大厅分别施加
（``ecosystem_cargo_hall`` / ``ecosystem_capacity_hall``），因为版本可以只开一个。
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db, get_tenant_code
from app.core.security import TokenData
from app.modules.client.services.ecosystem.hall_facade import EcoHallFacade
from app.modules.client.services.ecosystem.post_query_service import (
    SORT_OPTIONS,
    HallFilter,
)
from app.modules.console.models.ecosystem.constants import (
    CARGO_CATEGORY_LABELS,
    COOPERATION_TYPE_LABELS,
    PRICE_TYPE_LABELS,
    SETTLE_TYPE_LABELS,
    VALID_DAYS_OPTIONS,
    PostType,
)

# 筛选项元数据放后端下发而不是前端硬编码，是为了让两个大厅、发布弹层、以及后续
# 小程序端用的是同一份口径。枚举的中文名在 constants 里，这里只有排序方式——
# 排序是大厅独有的，发布时用不到
_SORT_LABELS = {
    "latest": "最新发布",
    "windowStart": "装车时间最近",
    "active": "最近活跃",
    "priceAsc": "报价从低到高",
    "priceDesc": "报价从高到低",
}


def _options(labels: dict) -> List[dict]:
    return [{"value": k, "label": v} for k, v in labels.items()]


def build_hall_router(post_type: int) -> APIRouter:
    """按大厅类型生成 router"""
    router = APIRouter()

    @router.get("/filters")
    async def hall_filters(
        _: TokenData = Depends(get_current_user),
    ):
        """筛选项元数据"""
        data = {
            "postType": post_type,
            "sortOptions": [
                {"value": k, "label": _SORT_LABELS[k]}
                for k in SORT_OPTIONS
                if k in _SORT_LABELS
            ],
            "priceTypes": _options(PRICE_TYPE_LABELS),
            "cooperationTypes": _options(COOPERATION_TYPE_LABELS),
            "settleTypes": _options(SETTLE_TYPE_LABELS),
            "validDaysOptions": list(VALID_DAYS_OPTIONS),
        }
        if post_type == PostType.CARGO:
            data["cargoCategories"] = _options(CARGO_CATEGORY_LABELS)
        return success(data=data)

    @router.get("")
    async def page_hall(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, alias="limit", ge=1, le=100),
        keyword: Optional[str] = Query(None),
        fromProvince: Optional[str] = Query(None),
        fromCity: Optional[str] = Query(None),
        toProvinces: Optional[List[str]] = Query(None),
        toCity: Optional[str] = Query(None),
        windowStartFrom: Optional[datetime] = Query(None),
        windowStartTo: Optional[datetime] = Query(None),
        quantityMin: Optional[int] = Query(None, ge=0),
        quantityMax: Optional[int] = Query(None, ge=0),
        truckTypes: Optional[List[str]] = Query(None),
        slotMin: Optional[int] = Query(None, ge=1, le=30),
        slotMax: Optional[int] = Query(None, ge=1, le=30),
        cargoCategory: Optional[int] = Query(None),
        priceType: Optional[int] = Query(None),
        onlyVerified: bool = Query(False),
        onlyHighCredit: bool = Query(False),
        excludeMine: bool = Query(True),
        sortBy: str = Query("latest"),
        db: AsyncSession = Depends(get_platform_db),
        tenant_code: str = Depends(get_tenant_code),
        _: TokenData = Depends(get_current_user),
    ):
        """大厅分页列表"""
        flt = HallFilter(
            page=page,
            page_size=page_size,
            keyword=keyword,
            from_province=fromProvince,
            from_city=fromCity,
            to_provinces=toProvinces or [],
            to_city=toCity,
            window_start_from=windowStartFrom,
            window_start_to=windowStartTo,
            quantity_min=quantityMin,
            quantity_max=quantityMax,
            truck_types=truckTypes or [],
            slot_min=slotMin,
            slot_max=slotMax,
            cargo_category=cargoCategory,
            price_type=priceType,
            only_verified=onlyVerified,
            only_high_credit=onlyHighCredit,
            exclude_mine=excludeMine,
            sort_by=sortBy,
        )
        data = await EcoHallFacade.page_hall(
            db, post_type=post_type, viewer_tenant_code=tenant_code, flt=flt
        )
        return success(data=data)

    @router.get("/{post_id}")
    async def hall_detail(
        post_id: int = Path(..., gt=0),
        db: AsyncSession = Depends(get_platform_db),
        tenant_code: str = Depends(get_tenant_code),
        _: TokenData = Depends(get_current_user),
    ):
        """挂牌详情

        详情与列表走同一套可见范围，拼 ID 直接访问拿不到大厅里搜不到的挂牌。
        """
        data = await EcoHallFacade.hall_detail(
            db, post_id=post_id, viewer_tenant_code=tenant_code
        )
        return success(data=data)

    return router


cargo_hall_router = build_hall_router(PostType.CARGO)
capacity_hall_router = build_hall_router(PostType.CAPACITY)
