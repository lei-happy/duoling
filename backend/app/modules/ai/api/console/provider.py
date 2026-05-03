"""Console 端：LLM Provider 管理"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.ai.schemas.console.provider import ProviderCreate, ProviderUpdate
from app.modules.ai.services.provider_service import ProviderService

router = APIRouter()


@router.get("")
async def page_providers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await ProviderService.page(
        db, page=page, page_size=page_size, keyword=keyword, status=status,
    )
    return success(data=data)


@router.post("")
async def create_provider(
    body: ProviderCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await ProviderService.create(db, body)
    return success(data={"id": row.id}, message="创建成功")


@router.put("/{provider_id}")
async def update_provider(
    provider_id: int,
    body: ProviderUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await ProviderService.update(db, provider_id, body)
    return success(message="更新成功")


@router.put("/{provider_id}/default")
async def set_default_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """把指定 Provider 设为默认"""
    await ProviderService.set_default(db, provider_id)
    return success(message="已设为默认 Provider")


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await ProviderService.delete(db, provider_id)
    return success(message="删除成功")
