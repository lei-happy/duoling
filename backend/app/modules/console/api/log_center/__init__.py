from fastapi import APIRouter
from app.modules.console.api.log_center.operation_log import router as operation_log_router

router = APIRouter()
router.include_router(
    operation_log_router,
    prefix="/operation-log",
    tags=["日志中心-操作日志"],
)

__all__ = ["router"]
