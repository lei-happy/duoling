"""
组织架构/部门管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.schemas.organization.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
)


class DepartmentService:

    @staticmethod
    async def page_departments(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        organization_name: Optional[str] = None,
        organization_type: Optional[str] = None,
    ) -> dict:
        """分页查询部门"""
        base = select(BizDepartment).where(BizDepartment.is_deleted == 0)

        if organization_name:
            base = base.where(BizDepartment.dept_name.contains(organization_name))
        if organization_type:
            base = base.where(BizDepartment.dept_type == organization_type)

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(BizDepartment.sort_order, BizDepartment.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = [DepartmentOut.from_model(d) for d in result.scalars().all()]

        return {
            "list": [item.model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def list_departments(
        db: AsyncSession,
        organization_name: Optional[str] = None,
        organization_type: Optional[str] = None,
    ) -> List[DepartmentOut]:
        """获取全部部门列表（平铺，前端组装树形）"""
        base = select(BizDepartment).where(BizDepartment.is_deleted == 0)

        if organization_name:
            base = base.where(BizDepartment.dept_name.contains(organization_name))
        if organization_type:
            base = base.where(BizDepartment.dept_type == organization_type)

        result = await db.execute(
            base.order_by(BizDepartment.sort_order, BizDepartment.id)
        )
        return [DepartmentOut.from_model(d) for d in result.scalars().all()]

    @staticmethod
    async def get_department_tree(
        db: AsyncSession,
        organization_name: Optional[str] = None,
    ) -> List[dict]:
        """获取部门树形结构"""
        base = select(BizDepartment).where(BizDepartment.is_deleted == 0)
        if organization_name:
            base = base.where(BizDepartment.dept_name.contains(organization_name))

        result = await db.execute(
            base.order_by(BizDepartment.sort_order, BizDepartment.id)
        )
        all_depts = result.scalars().all()

        dept_map = {}
        for d in all_depts:
            dept_map[d.id] = DepartmentOut.from_model(d).model_dump()
            dept_map[d.id]["children"] = []

        tree = []
        for d in all_depts:
            node = dept_map[d.id]
            if d.parent_id == 0 or d.parent_id not in dept_map:
                tree.append(node)
            else:
                dept_map[d.parent_id]["children"].append(node)

        return tree

    @staticmethod
    async def create_department(
        db: AsyncSession, data: DepartmentCreate
    ) -> BizDepartment:
        dept = BizDepartment(
            parent_id=data.parentId,
            dept_name=data.organizationName,
            dept_code=data.organizationCode,
            dept_type=data.organizationType,
            leader=data.leader,
            phone=data.phone,
            sort_order=data.sortNumber,
            remark=data.comments,
        )
        db.add(dept)
        await db.flush()
        await db.refresh(dept)
        return dept

    @staticmethod
    async def update_department(
        db: AsyncSession, dept_id: int, data: DepartmentUpdate
    ) -> BizDepartment:
        result = await db.execute(
            select(BizDepartment).where(
                BizDepartment.id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        dept = result.scalar_one_or_none()
        if not dept:
            raise BizException("部门不存在")

        field_map = {
            "parentId": "parent_id",
            "organizationName": "dept_name",
            "organizationCode": "dept_code",
            "organizationType": "dept_type",
            "leader": "leader",
            "phone": "phone",
            "sortNumber": "sort_order",
            "status": "status",
            "comments": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(dept, model_field, val)

        await db.flush()
        await db.refresh(dept)
        return dept

    @staticmethod
    async def delete_department(db: AsyncSession, dept_id: int) -> None:
        result = await db.execute(
            select(BizDepartment).where(
                BizDepartment.id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        dept = result.scalar_one_or_none()
        if not dept:
            raise BizException("部门不存在")

        children = await db.execute(
            select(BizDepartment).where(
                BizDepartment.parent_id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        if children.scalars().first():
            raise BizException("该部门下有子部门，无法删除")

        users = await db.execute(
            select(BizUser).where(
                BizUser.department_id == dept_id,
                BizUser.is_deleted == 0,
            )
        )
        if users.scalars().first():
            raise BizException("该部门下存在员工，无法删除")

        dept.is_deleted = 1
        await db.flush()
