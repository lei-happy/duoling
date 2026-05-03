"""客户端 AI 路由汇总"""

from fastapi import APIRouter, Depends

from app.core.dependencies import ensure_biz_ai_tables
from app.modules.ai.api.client.chat import router as chat_router
from app.modules.ai.api.client.session import router as session_router
from app.modules.ai.api.client.employee import router as employee_router
from app.modules.ai.api.client.file import router as file_router

router = APIRouter()

# chat / session 直接依赖租户库 biz_ai_* 表，挂上"首次访问自愈"依赖；
# employee / file 不读租户业务表，无需挂载。
router.include_router(
    chat_router,
    prefix="/chat",
    tags=["客户端-AI对话"],
    dependencies=[Depends(ensure_biz_ai_tables)],
)
router.include_router(
    session_router,
    prefix="/session",
    tags=["客户端-AI会话"],
    dependencies=[Depends(ensure_biz_ai_tables)],
)
router.include_router(employee_router, prefix="/employee", tags=["客户端-AI数字员工"])
router.include_router(file_router, prefix="/file", tags=["客户端-AI附件上传"])
