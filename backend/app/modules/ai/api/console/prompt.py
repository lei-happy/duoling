"""Console 端：AI 提示词模板管理"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.ai.schemas.console.prompt import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
)
from app.modules.ai.services.prompt_service import PromptService

router = APIRouter()


@router.get("")
async def page_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    scene: Optional[str] = None,
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await PromptService.page(
        db, page=page, page_size=page_size,
        keyword=keyword, scene=scene, status=status,
    )
    return success(data=data)


@router.post("")
async def create_prompt(
    body: PromptTemplateCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await PromptService.create(db, body)
    return success(data={"id": row.id}, message="创建成功")


@router.put("/{template_id}")
async def update_prompt(
    template_id: int,
    body: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await PromptService.update(db, template_id, body)
    return success(message="更新成功")


@router.delete("/{template_id}")
async def delete_prompt(
    template_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await PromptService.delete(db, template_id)
    return success(message="删除成功")
