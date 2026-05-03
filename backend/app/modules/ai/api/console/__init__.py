"""Console 端 AI 路由汇总"""

from fastapi import APIRouter

from app.modules.ai.api.console.employee import router as employee_router
from app.modules.ai.api.console.tool import router as tool_router
from app.modules.ai.api.console.prompt import router as prompt_router
from app.modules.ai.api.console.provider import router as provider_router
from app.modules.ai.api.console.observe import router as observe_router

router = APIRouter()
router.include_router(employee_router, prefix="/employee", tags=["管理后台-AI数字员工"])
router.include_router(tool_router, prefix="/tool", tags=["管理后台-AI工具"])
router.include_router(prompt_router, prefix="/prompt", tags=["管理后台-AI提示词模板"])
router.include_router(provider_router, prefix="/provider", tags=["管理后台-AI模型Provider"])
router.include_router(observe_router, prefix="/observe", tags=["管理后台-AI调用观测"])
