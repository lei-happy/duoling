"""审批中心 API 路由聚合"""

from fastapi import APIRouter

from app.modules.client.api.approval.center import router as center_router
from app.modules.client.api.approval.flow import router as flow_router

router = APIRouter()

# 流程模板配置（更具体的前缀先注册）
router.include_router(flow_router, prefix="/flow")
# 待办 / 申请 / 记录 / 审批动作
router.include_router(center_router)

__all__ = ["router"]
