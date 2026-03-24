"""
组织架构/部门管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.biz_department import BizDepartment
from app.modules.client.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
)


class DepartmentService:

    @staticmethod
    async def list_departments(db: AsyncSession) -> List[DepartmentOut]:
        """获取全部部门列表（平铺，前端组装树形）"""
        result = await db.execute(
            select(BizDepartment)
            .where(BizDepartment.is_deleted == 0)
            .order_by(BizDepartment.sort_order, BizDepartment.id)
        )
        return [DepartmentOut.from_model(d) for d in result.scalars().all()]

    @staticmethod
    async def get_department_tree(db: AsyncSession) -> List[dict]:
        """获取部门树形结构"""
        result = await db.execute(
            select(BizDepartment)
            .where(BizDepartment.is_deleted == 0)
            .order_by(BizDepartment.sort_order, BizDepartment.id)
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
            dept_name=data.deptName,
            dept_code=data.deptCode,
            leader=data.leader,
            phone=data.phone,
            sort_order=data.sortOrder,
            remark=data.remark,
        )
        db.add(dept)
        await db.flush()
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
            "deptName": "dept_name",
            "deptCode": "dept_code",
            "leader": "leader",
            "phone": "phone",
            "sortOrder": "sort_order",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(dept, model_field, val)

        await db.flush()
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

        # 检查是否有子部门
        children = await db.execute(
            select(BizDepartment).where(
                BizDepartment.parent_id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        if children.scalars().first():
            raise BizException("该部门下有子部门，无法删除")

        dept.is_deleted = 1
        await db.flush()
