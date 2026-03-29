"""
企业自助注册接口
"""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.modules.open.schemas.register import RegisterRequest
from app.modules.open.services.register_service import RegisterService

router = APIRouter()


@router.post("")
async def register_tenant(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_platform_db),
):
    """企业自助注册：立即返回 task_id，客户端轮询 /register/progress/{task_id}"""
    result = await RegisterService.start_register(db, data, background_tasks)
    return success(data=result.model_dump(), message="已受理注册")


@router.get("/progress/{task_id}")
async def register_progress(
    task_id: str,
    db: AsyncSession = Depends(get_platform_db),
):
    """查询企业注册任务进度与结果"""
    out = await RegisterService.get_progress(db, task_id)
    return success(data=out.model_dump())
