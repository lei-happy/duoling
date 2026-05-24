"""
驾驶员端 API 路由聚合

挂载点：``/api/driver/*``

子路由：
- ``/auth/*``         手机号 / 验证码登录、企业切换、修改密码、user-info
- ``/task/*``         我的任务、装车 / 出发 / 到达 / 签收
- ``/task-receipt/*`` 回单上传与列表（一期最小）
- ``/finance/*``      我的费用单、汇总、收款账户
- ``/profile/*``      个人信息读写、头像上传（白名单字段）
"""

from fastapi import APIRouter

from app.modules.driver.api.auth import router as auth_router
from app.modules.driver.api.task import router as task_router
from app.modules.driver.api.task_receipt import router as task_receipt_router
from app.modules.driver.api.finance import router as finance_router
from app.modules.driver.api.profile import router as profile_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["司机端-认证"])
router.include_router(task_router, prefix="/task", tags=["司机端-任务"])
router.include_router(
    task_receipt_router, prefix="/task-receipt", tags=["司机端-回单"]
)
router.include_router(finance_router, prefix="/finance", tags=["司机端-财务"])
router.include_router(profile_router, prefix="/profile", tags=["司机端-个人中心"])

__all__ = ["router"]
