"""客户端：列出可用数字员工 / 员工已绑定工具"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.ai.models.platform.ai_employee import AiEmployee
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.schemas.client.chat import EmployeeOut, EmployeeToolOut
from app.modules.ai.services.employee_service import EmployeeService

router = APIRouter()


@router.get("")
async def list_employees(
    platform_db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    rows = await EmployeeService.list_visible_for_user(platform_db)
    return success(
        data={"list": [EmployeeOut.from_model(r).model_dump() for r in rows]}
    )


@router.get("/{employee_code}/tools")
async def list_employee_tools(
    employee_code: str,
    platform_db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    emp = (
        await platform_db.execute(
            select(AiEmployee).where(
                AiEmployee.code == employee_code, AiEmployee.is_deleted == 0
            )
        )
    ).scalar_one_or_none()
    if not emp:
        raise BizException("数字员工不存在")

    rows = (
        await platform_db.execute(
            select(AiTool, AiEmployeeTool.sort_order)
            .join(AiEmployeeTool, AiEmployeeTool.tool_id == AiTool.id)
            .where(
                AiEmployeeTool.employee_id == emp.id,
                AiEmployeeTool.enabled == 1,
                AiEmployeeTool.is_deleted == 0,
                AiTool.is_deleted == 0,
                AiTool.status == 1,
            )
            .order_by(AiEmployeeTool.sort_order.asc(), AiTool.id.asc())
        )
    ).all()
    return success(
        data={
            "list": [
                EmployeeToolOut(
                    code=t.code,
                    name=t.name,
                    category=t.category,
                    description=t.description,
                    riskLevel=t.risk_level,
                    confirmRequired=bool(t.confirm_required),
                ).model_dump()
                for t, _ord in rows
            ]
        }
    )
