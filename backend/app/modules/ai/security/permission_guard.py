"""
工具调用权限守卫

双层校验：
1) 数字员工白名单：tool 必须在该 employee 的 ai_employee_tool 绑定列表内
2) 用户菜单权限：把 user.roles → tenant 库角色 → 角色绑定的菜单 → menu_code，
   必须包含 tool.required_permission（避免越权）
   - 平台管理员（user_type=1）默认放行
   - 租户管理员（user_type=2）默认放行
"""

from __future__ import annotations

from typing import Optional, Set

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import PermissionException
from app.core.security import TokenData
from app.modules.ai.models.platform.ai_employee import AiEmployee
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.tools.base import ToolContext, ToolSpec


class PermissionGuard:
    """工具调用前的权限守卫"""

    @staticmethod
    async def check(
        ctx: ToolContext,
        spec: ToolSpec,
        employee_code: str,
    ) -> None:
        """通过则正常返回；未通过抛 PermissionException"""

        # 1) 工具是否启用
        tool_row, employee_row = await PermissionGuard._load_tool_and_employee(
            ctx.platform_db, spec.code, employee_code
        )
        if not tool_row or tool_row.status != 1:
            raise PermissionException(f"工具 {spec.code} 已停用")
        if not employee_row or employee_row.status != 1:
            raise PermissionException(f"数字员工 {employee_code} 已停用")

        # 2) 数字员工白名单
        bind = await PermissionGuard._load_employee_tool_binding(
            ctx.platform_db, employee_row.id, tool_row.id
        )
        if bind is None or bind.enabled != 1:
            raise PermissionException(
                f"数字员工「{employee_row.name}」未授权调用工具「{spec.name}」"
            )

        # 3) 用户菜单权限
        if spec.required_permission:
            allowed = await PermissionGuard._user_has_permission(
                ctx.db, ctx.user, spec.required_permission
            )
            if not allowed:
                raise PermissionException(
                    f"当前用户缺少权限码 {spec.required_permission}，无法调用工具「{spec.name}」"
                )

    # -------------------- 内部 --------------------

    @staticmethod
    async def _load_tool_and_employee(
        platform_db: AsyncSession, tool_code: str, employee_code: str
    ) -> tuple[Optional[AiTool], Optional[AiEmployee]]:
        tool_row = (
            await platform_db.execute(
                select(AiTool).where(
                    AiTool.code == tool_code,
                    AiTool.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        emp_row = (
            await platform_db.execute(
                select(AiEmployee).where(
                    AiEmployee.code == employee_code,
                    AiEmployee.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        return tool_row, emp_row

    @staticmethod
    async def _load_employee_tool_binding(
        platform_db: AsyncSession, employee_id: int, tool_id: int
    ) -> Optional[AiEmployeeTool]:
        return (
            await platform_db.execute(
                select(AiEmployeeTool).where(
                    AiEmployeeTool.employee_id == employee_id,
                    AiEmployeeTool.tool_id == tool_id,
                    AiEmployeeTool.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()

    @staticmethod
    async def _user_has_permission(
        tenant_db: AsyncSession, user: TokenData, permission_code: str
    ) -> bool:
        """根据用户角色 → 角色绑定菜单 → menu_code 反查权限"""
        # 平台/租户管理员放行
        if user.user_type in (1, 2):
            return True

        try:
            menu_codes = await PermissionGuard._collect_user_menu_codes(
                tenant_db, user.user_id
            )
        except Exception as e:
            logger.warning(f"[PermissionGuard] 加载用户菜单权限失败: {e!r}")
            return False
        return permission_code in menu_codes

    @staticmethod
    async def _collect_user_menu_codes(
        tenant_db: AsyncSession, user_id: int
    ) -> Set[str]:
        """收集用户拥有的全部菜单权限码

        路径：biz_user_role → biz_role_menu(menu_id) → 平台库 sys_menu.menu_code
        为避免跨库 JOIN，分两步查：
            1) 在租户库拿 user_id 关联的 menu_id 集合
            2) 在平台库拿 menu_id → menu_code 映射
        """
        from sqlalchemy import text as sa_text

        from app.core.database import db_manager

        # 步骤 1: 租户库
        rows = (
            await tenant_db.execute(
                sa_text(
                    """
                    SELECT DISTINCT brm.menu_id
                    FROM biz_user_role bur
                    JOIN biz_role_menu brm ON brm.role_id = bur.role_id
                    WHERE bur.user_id = :uid
                      AND bur.is_deleted = 0
                      AND brm.is_deleted = 0
                    """
                ),
                {"uid": user_id},
            )
        ).fetchall()
        menu_ids = [r[0] for r in rows if r and r[0] is not None]
        if not menu_ids:
            return set()

        # 步骤 2: 平台库
        from sqlalchemy import bindparam

        factory = db_manager._platform_session_factory  # noqa: SLF001
        if factory is None:
            return set()
        stmt = sa_text(
            "SELECT DISTINCT menu_code FROM sys_menu "
            "WHERE app_type = 'client' AND is_deleted = 0 "
            "AND id IN :ids AND menu_code IS NOT NULL AND menu_code <> ''"
        ).bindparams(bindparam("ids", expanding=True))
        async with factory() as platform_session:
            result = await platform_session.execute(stmt, {"ids": menu_ids})
            codes = {row[0] for row in result.fetchall() if row and row[0]}
        return codes
