"""
企业端员工管理服务（租户库）
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.client.models.biz_user import BizUser
from app.modules.client.models.biz_user_role import BizUserRole
from app.modules.client.models.biz_role import BizRole
from app.modules.client.schemas.user import (
    BizUserCreate, BizUserUpdate, BizUserOut,
)


class BizUserService:

    @staticmethod
    async def page_users(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(BizUser).where(BizUser.is_deleted == 0)

        if keyword:
            base = base.where(
                (BizUser.username.contains(keyword)) |
                (BizUser.real_name.contains(keyword)) |
                (BizUser.phone.contains(keyword))
            )
        if department:
            base = base.where(BizUser.department == department)
        if status is not None:
            base = base.where(BizUser.status == status)

        # Total count
        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        # Paginated list
        result = await db.execute(
            base.order_by(BizUser.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        users = result.scalars().all()

        items = []
        for u in users:
            roles = await BizUserService._get_user_roles(db, u.id)
            items.append(BizUserOut.from_model(u, roles=roles))

        return {
            "list": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def _get_user_roles(db: AsyncSession, user_id: int) -> list:
        result = await db.execute(
            select(BizRole)
            .join(BizUserRole, BizUserRole.role_id == BizRole.id)
            .where(
                BizUserRole.user_id == user_id,
                BizUserRole.is_deleted == 0,
                BizRole.is_deleted == 0,
            )
        )
        return [
            {"roleId": r.id, "roleCode": r.role_code, "roleName": r.role_name}
            for r in result.scalars().all()
        ]

    @staticmethod
    async def create_user(db: AsyncSession, data: BizUserCreate) -> BizUser:
        # 检查用户名唯一性
        existing = await db.execute(
            select(BizUser).where(
                BizUser.username == data.username,
                BizUser.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"用户名 {data.username} 已存在")

        user = BizUser(
            username=data.username,
            password=hash_password(data.password),
            real_name=data.realName,
            phone=data.phone,
            email=data.email,
            gender=data.gender,
            user_type=data.userType,
            department=data.department,
            remark=data.remark,
        )
        db.add(user)
        await db.flush()

        # 关联角色
        if data.roleIds:
            for rid in data.roleIds:
                db.add(BizUserRole(user_id=user.id, role_id=rid))
            await db.flush()

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, data: BizUserUpdate
    ) -> BizUser:
        result = await db.execute(
            select(BizUser).where(
                BizUser.id == user_id,
                BizUser.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")

        field_map = {
            "realName": "real_name",
            "phone": "phone",
            "email": "email",
            "avatar": "avatar",
            "gender": "gender",
            "userType": "user_type",
            "department": "department",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(user, model_field, val)

        # 更新角色关联
        if data.roleIds is not None:
            old_roles = await db.execute(
                select(BizUserRole).where(
                    BizUserRole.user_id == user_id,
                    BizUserRole.is_deleted == 0,
                )
            )
            for ur in old_roles.scalars().all():
                ur.is_deleted = 1

            for rid in data.roleIds:
                db.add(BizUserRole(user_id=user_id, role_id=rid))

        await db.flush()
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        result = await db.execute(
            select(BizUser).where(
                BizUser.id == user_id,
                BizUser.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")
        if user.user_type == 1:
            raise BizException("管理员账号无法删除")
        user.is_deleted = 1
        await db.flush()

    @staticmethod
    async def reset_password(
        db: AsyncSession, user_id: int, new_password: str = "123456"
    ) -> None:
        result = await db.execute(
            select(BizUser).where(
                BizUser.id == user_id,
                BizUser.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")
        user.password = hash_password(new_password)
        await db.flush()
