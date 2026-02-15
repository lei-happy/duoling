"""
组织架构桩接口
暂时返回硬编码的默认组织节点，使用户管理页面可正常加载。
后续再完善为真实数据。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success

router = APIRouter()

# 默认组织节点
DEFAULT_ORG = {
    "organizationId": 0,
    "parentId": -1,
    "organizationName": "全部",
    "organizationType": 0,
    "sortNumber": 0,
    "children": [],
}


@router.get("")
async def list_organizations(
    _: TokenData = Depends(get_current_user),
):
    """返回默认组织列表"""
    return success(data=[DEFAULT_ORG])


@router.get("/tree")
async def organization_tree(
    _: TokenData = Depends(get_current_user),
):
    """返回默认组织树"""
    return success(data=[DEFAULT_ORG])
