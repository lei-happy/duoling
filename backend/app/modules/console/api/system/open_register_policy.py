"""
运营后台：官网自助注册策略（默认版本 + 试用天数）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.system.open_register_policy import (
    OpenRegisterPolicyOut,
    OpenRegisterPolicyUpdate,
)
from app.modules.console.services.system.open_register_policy_service import (
    OpenRegisterPolicyService,
)

router = APIRouter()


@router.get("")
async def get_open_register_policy(
    db: AsyncSession = Depends(get_platform_db),
    _current_user: TokenData = Depends(get_current_user),
):
    vc, td = await OpenRegisterPolicyService.get_policy_raw(db)
    out = OpenRegisterPolicyOut(version_code=vc, trial_days=td)
    return success(data=out.model_dump(by_alias=True))


@router.put("")
async def update_open_register_policy(
    data: OpenRegisterPolicyUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _current_user: TokenData = Depends(get_current_user),
):
    await OpenRegisterPolicyService.save_policy(
        db, data.version_code, data.trial_days
    )
    vc, td = await OpenRegisterPolicyService.get_policy_raw(db)
    out = OpenRegisterPolicyOut(version_code=vc, trial_days=td)
    return success(data=out.model_dump(by_alias=True), message="保存成功")
