"""
设计对接模块接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import fail, success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.console.schemas.doc_center.design_module import (
    DesignModuleCreate,
    DesignModuleOut,
    DesignModulePriorityUpdate,
    DesignModuleSortRequest,
    DesignModuleStatusUpdate,
    DesignModuleUpdate,
)
from app.modules.console.services.doc_center.design_module_service import (
    DesignModuleService,
)

router = APIRouter()


def _to_out(row) -> dict:
    return DesignModuleOut.model_validate(row).model_dump(mode="json")


@router.get("")
async def list_design_modules(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    status: Optional[int] = Query(None, description="状态筛选"),
    priority: Optional[int] = Query(None, description="优先级筛选"),
    product_line: Optional[str] = Query(None, description="产品端筛选"),
    keyword: Optional[str] = Query(None, description="关键词"),
    view: Optional[str] = Query(None, description="list|board"),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """设计对接模块列表 / 看板"""
    if view == "board":
        board = await DesignModuleService.list_board(
            db,
            priority=priority,
            product_line=product_line,
            keyword=keyword,
        )
        return success(
            data={
                "board": {
                    k: [_to_out(i) for i in v] for k, v in board.items()
                }
            }
        )

    items, total = await DesignModuleService.list_page(
        db,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        product_line=product_line,
        keyword=keyword,
    )
    return success(
        data={
            "list": [_to_out(i) for i in items],
            "total": total,
            "page": page,
            "limit": limit,
        }
    )


@router.put("/sort")
async def sort_design_modules(
    data: DesignModuleSortRequest,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """批量更新排序（支持跨列改状态）"""
    await DesignModuleService.sort(db, data.items, current_user.user_id)
    return success(message="排序已更新")


@router.post("")
async def create_design_module(
    data: DesignModuleCreate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """创建设计对接模块"""
    row = await DesignModuleService.create(db, data, current_user.user_id)
    return success(data=_to_out(row), message="已创建模块")


@router.get("/{module_id}")
async def get_design_module(
    module_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """设计对接模块详情"""
    row = await DesignModuleService.get_by_id(db, module_id)
    if not row:
        return fail("未找到该模块，请刷新后重试")
    return success(data=_to_out(row))


@router.put("/{module_id}")
async def update_design_module(
    module_id: int,
    data: DesignModuleUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新设计对接模块"""
    row = await DesignModuleService.update(
        db, module_id, data, current_user.user_id
    )
    return success(data=_to_out(row), message="已保存")


@router.patch("/{module_id}/status")
async def update_design_module_status(
    module_id: int,
    data: DesignModuleStatusUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新状态"""
    row = await DesignModuleService.update_status(
        db, module_id, data.status, current_user.user_id
    )
    return success(data=_to_out(row), message="状态已更新")


@router.patch("/{module_id}/priority")
async def update_design_module_priority(
    module_id: int,
    data: DesignModulePriorityUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新优先级"""
    row = await DesignModuleService.update_priority(
        db, module_id, data.priority, current_user.user_id
    )
    return success(data=_to_out(row), message="优先级已更新")


@router.delete("/{module_id}")
async def delete_design_module(
    module_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """删除设计对接模块（软删）"""
    await DesignModuleService.delete(db, module_id, current_user.user_id)
    return success(message="已删除该模块")
