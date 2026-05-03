"""数字员工管理服务（平台库）"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.ai.models.platform.ai_employee import AiEmployee
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.schemas.console.employee import (
    EmployeeCreate,
    EmployeeUpdate,
)


class EmployeeService:

    @staticmethod
    async def page(
        platform_db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        employee_type: Optional[str] = None,
    ) -> dict:
        base = select(AiEmployee).where(AiEmployee.is_deleted == 0)
        if keyword:
            base = base.where(
                (AiEmployee.code.contains(keyword))
                | (AiEmployee.name.contains(keyword))
            )
        if status is not None:
            base = base.where(AiEmployee.status == status)
        if employee_type:
            base = base.where(AiEmployee.employee_type == employee_type)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await platform_db.execute(count_q)).scalar() or 0

        rows = (
            await platform_db.execute(
                base.order_by(AiEmployee.sort_order.asc(), AiEmployee.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()

        # 收集所有员工的工具绑定
        emp_ids = [r.id for r in rows]
        tool_ids_by_emp: dict[int, list[int]] = {eid: [] for eid in emp_ids}
        if emp_ids:
            from sqlalchemy import bindparam, text as sa_text

            stmt = sa_text(
                "SELECT employee_id, tool_id FROM ai_employee_tool "
                "WHERE is_deleted = 0 AND enabled = 1 AND employee_id IN :ids"
            ).bindparams(bindparam("ids", expanding=True))
            for row in (
                await platform_db.execute(stmt, {"ids": emp_ids})
            ).fetchall():
                tool_ids_by_emp.setdefault(row[0], []).append(row[1])

        return {
            "list": [
                EmployeeService._to_dict(r, tool_ids_by_emp.get(r.id, []))
                for r in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get(platform_db: AsyncSession, employee_id: int) -> dict:
        row = (
            await platform_db.execute(
                select(AiEmployee).where(
                    AiEmployee.id == employee_id, AiEmployee.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("数字员工不存在")
        tool_ids = await EmployeeService._load_tool_ids(platform_db, row.id)
        return EmployeeService._to_dict(row, tool_ids)

    @staticmethod
    async def get_by_code(
        platform_db: AsyncSession, code: str
    ) -> Optional[AiEmployee]:
        row = (
            await platform_db.execute(
                select(AiEmployee).where(
                    AiEmployee.code == code, AiEmployee.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        return row

    @staticmethod
    async def create(platform_db: AsyncSession, data: EmployeeCreate) -> AiEmployee:
        existing = (
            await platform_db.execute(
                select(AiEmployee.id).where(
                    AiEmployee.code == data.code, AiEmployee.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise BizException(f"员工编码 {data.code} 已存在")

        row = AiEmployee(
            code=data.code,
            name=data.name,
            employee_type=data.employeeType,
            description=data.description,
            avatar=data.avatar,
            system_prompt=data.systemPrompt,
            welcome_message=data.welcomeMessage,
            suggested_questions=data.suggestedQuestions,
            model_config_json=data.modelConfig,
            feature_code=data.featureCode,
            sort_order=data.sortOrder,
            status=data.status,
        )
        platform_db.add(row)
        await platform_db.flush()

        if data.toolIds:
            await EmployeeService._sync_tool_bindings(
                platform_db, row.id, data.toolIds
            )

        await platform_db.commit()
        await platform_db.refresh(row)
        return row

    @staticmethod
    async def update(
        platform_db: AsyncSession, employee_id: int, data: EmployeeUpdate
    ) -> AiEmployee:
        row = (
            await platform_db.execute(
                select(AiEmployee).where(
                    AiEmployee.id == employee_id, AiEmployee.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("数字员工不存在")

        field_map = {
            "name": "name",
            "employeeType": "employee_type",
            "description": "description",
            "avatar": "avatar",
            "systemPrompt": "system_prompt",
            "welcomeMessage": "welcome_message",
            "suggestedQuestions": "suggested_questions",
            "modelConfig": "model_config_json",
            "featureCode": "feature_code",
            "sortOrder": "sort_order",
            "status": "status",
        }
        for sf, mf in field_map.items():
            v = getattr(data, sf, None)
            if v is not None:
                setattr(row, mf, v)

        if data.toolIds is not None:
            await EmployeeService._sync_tool_bindings(
                platform_db, row.id, data.toolIds
            )

        await platform_db.flush()
        await platform_db.commit()
        await platform_db.refresh(row)
        return row

    @staticmethod
    async def delete(platform_db: AsyncSession, employee_id: int) -> None:
        row = (
            await platform_db.execute(
                select(AiEmployee).where(
                    AiEmployee.id == employee_id, AiEmployee.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("数字员工不存在")
        row.is_deleted = 1
        await platform_db.flush()
        await platform_db.commit()

    @staticmethod
    async def list_visible_for_user(
        platform_db: AsyncSession,
    ) -> list[AiEmployee]:
        """客户端使用：列出全部启用的数字员工

        TODO: 远期可按 feature_code 与租户产品版本过滤；
        当前阶段所有 enterprise 租户都开通 ai_assistant，统一可见。
        """
        rows = (
            await platform_db.execute(
                select(AiEmployee)
                .where(AiEmployee.is_deleted == 0, AiEmployee.status == 1)
                .order_by(AiEmployee.sort_order.asc(), AiEmployee.id.asc())
            )
        ).scalars().all()
        return list(rows)

    @staticmethod
    async def list_enabled_tool_codes(
        platform_db: AsyncSession, employee_id: int
    ) -> list[str]:
        """加载某员工 enabled=1 的工具 code 列表（按 sort_order）"""
        rows = (
            await platform_db.execute(
                select(AiTool.code, AiEmployeeTool.sort_order)
                .join(
                    AiEmployeeTool,
                    AiEmployeeTool.tool_id == AiTool.id,
                )
                .where(
                    AiEmployeeTool.employee_id == employee_id,
                    AiEmployeeTool.enabled == 1,
                    AiEmployeeTool.is_deleted == 0,
                    AiTool.is_deleted == 0,
                    AiTool.status == 1,
                )
                .order_by(AiEmployeeTool.sort_order.asc(), AiTool.id.asc())
            )
        ).all()
        return [r[0] for r in rows]

    # -------- 内部 --------

    @staticmethod
    async def _load_tool_ids(
        platform_db: AsyncSession, employee_id: int
    ) -> list[int]:
        rows = (
            await platform_db.execute(
                select(AiEmployeeTool.tool_id).where(
                    AiEmployeeTool.employee_id == employee_id,
                    AiEmployeeTool.is_deleted == 0,
                    AiEmployeeTool.enabled == 1,
                )
            )
        ).all()
        return [r[0] for r in rows]

    @staticmethod
    async def _sync_tool_bindings(
        platform_db: AsyncSession, employee_id: int, tool_ids: list[int]
    ) -> None:
        await platform_db.execute(
            delete(AiEmployeeTool).where(AiEmployeeTool.employee_id == employee_id)
        )
        for idx, tid in enumerate(tool_ids):
            platform_db.add(
                AiEmployeeTool(
                    employee_id=employee_id,
                    tool_id=tid,
                    sort_order=idx,
                    enabled=1,
                )
            )
        await platform_db.flush()

    @staticmethod
    def _to_dict(row: AiEmployee, tool_ids: list[int]) -> dict:
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "employeeType": row.employee_type,
            "description": row.description,
            "avatar": row.avatar,
            "systemPrompt": row.system_prompt,
            "welcomeMessage": row.welcome_message,
            "suggestedQuestions": row.suggested_questions,
            "modelConfig": row.model_config_json,
            "featureCode": row.feature_code,
            "sortOrder": row.sort_order,
            "status": row.status,
            "toolIds": tool_ids,
            "createdAt": row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else None,
            "updatedAt": row.updated_at.strftime("%Y-%m-%d %H:%M:%S") if row.updated_at else None,
        }
