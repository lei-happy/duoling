"""
设计对接模块服务
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.doc_center.sys_design_module import SysDesignModule
from app.modules.console.models.system.user import User
from app.modules.console.schemas.doc_center.design_module import (
    DesignModuleCreate,
    DesignModuleSortItem,
    DesignModuleUpdate,
    VALID_STATUSES,
)


class DesignModuleService:
    """设计对接模块服务"""

    @staticmethod
    async def _resolve_user_name(
        db: AsyncSession, user_id: Optional[int]
    ) -> Optional[str]:
        if not user_id:
            return None
        result = await db.execute(
            select(User.real_name, User.phone).where(
                User.id == user_id, User.is_deleted == 0
            )
        )
        row = result.one_or_none()
        if not row:
            return None
        return row.real_name or row.phone

    @staticmethod
    async def create(
        db: AsyncSession,
        data: DesignModuleCreate,
        operator_id: int,
    ) -> SysDesignModule:
        payload = data.model_dump()

        # 默认 PM 为当前用户
        if payload.get("pm_user_id") is None:
            payload["pm_user_id"] = operator_id
        if not payload.get("pm_name") and payload.get("pm_user_id"):
            payload["pm_name"] = await DesignModuleService._resolve_user_name(
                db, payload["pm_user_id"]
            )
        if payload.get("designer_user_id") and not payload.get("designer_name"):
            payload["designer_name"] = await DesignModuleService._resolve_user_name(
                db, payload["designer_user_id"]
            )
        if payload.get("developer_user_id") and not payload.get("developer_name"):
            payload["developer_name"] = await DesignModuleService._resolve_user_name(
                db, payload["developer_user_id"]
            )

        # 新模块排到当前状态列最前
        max_sort = await db.scalar(
            select(func.coalesce(func.min(SysDesignModule.sort_order), 0)).where(
                SysDesignModule.is_deleted == 0,
                SysDesignModule.status == payload.get("status", 0),
            )
        )
        sort_order = (max_sort or 0) - 1

        row = SysDesignModule(
            **payload,
            sort_order=sort_order,
            created_by=operator_id,
            updated_by=operator_id,
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    def _base_query(
        *,
        status: Optional[int] = None,
        priority: Optional[int] = None,
        product_line: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        query = select(SysDesignModule).where(SysDesignModule.is_deleted == 0)
        if status is not None:
            query = query.where(SysDesignModule.status == status)
        if priority is not None:
            query = query.where(SysDesignModule.priority == priority)
        if product_line:
            query = query.where(SysDesignModule.product_line == product_line)
        if keyword:
            like = f"%{keyword.strip()}%"
            query = query.where(
                or_(
                    SysDesignModule.title.like(like),
                    SysDesignModule.description.like(like),
                    SysDesignModule.pm_name.like(like),
                    SysDesignModule.designer_name.like(like),
                    SysDesignModule.developer_name.like(like),
                )
            )
        return query

    @staticmethod
    async def list_page(
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[int] = None,
        priority: Optional[int] = None,
        product_line: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[List[SysDesignModule], int]:
        query = DesignModuleService._base_query(
            status=status,
            priority=priority,
            product_line=product_line,
            keyword=keyword,
        )
        total = (
            await db.scalar(select(func.count()).select_from(query.subquery()))
            or 0
        )
        query = query.order_by(
            SysDesignModule.priority.desc(),
            SysDesignModule.sort_order.asc(),
            SysDesignModule.updated_at.desc(),
        )
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    @staticmethod
    async def list_board(
        db: AsyncSession,
        *,
        priority: Optional[int] = None,
        product_line: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, List[SysDesignModule]]:
        query = DesignModuleService._base_query(
            priority=priority,
            product_line=product_line,
            keyword=keyword,
        ).order_by(
            SysDesignModule.sort_order.asc(),
            SysDesignModule.priority.desc(),
            SysDesignModule.updated_at.desc(),
        )
        result = await db.execute(query)
        items = list(result.scalars().all())
        board: Dict[str, List[SysDesignModule]] = {
            str(s): [] for s in sorted(VALID_STATUSES)
        }
        for item in items:
            board.setdefault(str(item.status), []).append(item)
        return board

    @staticmethod
    async def get_by_id(
        db: AsyncSession, module_id: int
    ) -> Optional[SysDesignModule]:
        result = await db.execute(
            select(SysDesignModule).where(
                SysDesignModule.id == module_id,
                SysDesignModule.is_deleted == 0,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _fill_names(
        db: AsyncSession, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        if "pm_user_id" in payload and payload.get("pm_name") is None:
            payload["pm_name"] = await DesignModuleService._resolve_user_name(
                db, payload.get("pm_user_id")
            )
        if "designer_user_id" in payload and payload.get("designer_name") is None:
            payload["designer_name"] = await DesignModuleService._resolve_user_name(
                db, payload.get("designer_user_id")
            )
        if "developer_user_id" in payload and payload.get("developer_name") is None:
            payload["developer_name"] = await DesignModuleService._resolve_user_name(
                db, payload.get("developer_user_id")
            )
        return payload

    @staticmethod
    async def update(
        db: AsyncSession,
        module_id: int,
        data: DesignModuleUpdate,
        operator_id: int,
    ) -> SysDesignModule:
        row = await DesignModuleService.get_by_id(db, module_id)
        if not row:
            raise BizException("未找到该模块，请刷新后重试")

        payload = data.model_dump(exclude_unset=True)
        payload = await DesignModuleService._fill_names(db, payload)
        for key, value in payload.items():
            setattr(row, key, value)
        row.updated_by = operator_id
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def update_status(
        db: AsyncSession,
        module_id: int,
        status: int,
        operator_id: int,
    ) -> SysDesignModule:
        row = await DesignModuleService.get_by_id(db, module_id)
        if not row:
            raise BizException("未找到该模块，请刷新后重试")
        row.status = status
        row.updated_by = operator_id
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def update_priority(
        db: AsyncSession,
        module_id: int,
        priority: int,
        operator_id: int,
    ) -> SysDesignModule:
        row = await DesignModuleService.get_by_id(db, module_id)
        if not row:
            raise BizException("未找到该模块，请刷新后重试")
        row.priority = priority
        row.updated_by = operator_id
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def sort(
        db: AsyncSession,
        items: List[DesignModuleSortItem],
        operator_id: int,
    ) -> bool:
        ids = [i.id for i in items]
        result = await db.execute(
            select(SysDesignModule).where(
                SysDesignModule.id.in_(ids),
                SysDesignModule.is_deleted == 0,
            )
        )
        rows = {r.id: r for r in result.scalars().all()}
        missing = [i for i in ids if i not in rows]
        if missing:
            raise BizException("部分模块已不存在，请刷新后重试")

        for item in items:
            row = rows[item.id]
            row.sort_order = item.sort_order
            if item.status is not None:
                row.status = item.status
            row.updated_by = operator_id
        await db.flush()
        return True

    @staticmethod
    async def delete(
        db: AsyncSession, module_id: int, operator_id: int
    ) -> bool:
        row = await DesignModuleService.get_by_id(db, module_id)
        if not row:
            raise BizException("未找到该模块，请刷新后重试")
        row.is_deleted = 1
        row.updated_by = operator_id
        await db.flush()
        return True
