"""
产品信息公开查询接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.schemas.product.product_version import ProductVersionOut

router = APIRouter()


@router.get("/versions")
async def list_product_versions(
    db: AsyncSession = Depends(get_platform_db),
):
    """获取产品版本列表（公开，无需登录）"""
    result = await db.execute(
        select(ProductVersion)
        .where(ProductVersion.is_deleted == 0, ProductVersion.status == 1)
        .order_by(ProductVersion.sort_order)
    )
    items = result.scalars().all()
    return success(data=[ProductVersionOut.model_validate(v).model_dump(by_alias=True) for v in items])
