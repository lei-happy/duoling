"""
用户管理服务
"""

from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.utils import hash_password, verify_password
from app.modules.console.models.user import User
from app.modules.console.models.user_role import UserRole
from app.modules.console.models.role import Role
from app.modules.console.schemas.user import UserCreate, UserUpdate


class UserService:
    """用户管理服务"""

    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名唯一性
        existing = await db.execute(
            select(User).where(User.username == data.username, User.is_deleted == 0)
        )
        if existing.scalar_one_or_none():
            raise BizException("用户名已存在")

        user = User(
            username=data.username,
            password=hash_password(data.password),
            real_name=data.real_name,
            phone=data.phone,
            email=data.email,
            gender=data.gender,
            user_type=data.user_type,
            tenant_code=data.tenant_code,
            status=1,
            remark=data.remark,
        )
        db.add(user)
        await db.flush()

        # 关联角色
        if data.role_ids:
            for role_id in data.role_ids:
                db.add(UserRole(user_id=user.id, role_id=role_id))
            await db.flush()

        return user

    @staticmethod
    async def get_user_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        user_type: Optional[int] = None,
        tenant_code: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[User], int]:
        """获取用户列表（分页）"""
        query = select(User).where(User.is_deleted == 0)

        if keyword:
            query = query.where(
                User.username.contains(keyword)
                | User.real_name.contains(keyword)
                | User.phone.contains(keyword)
            )
        if user_type is not None:
            query = query.where(User.user_type == user_type)
        if tenant_code:
            query = query.where(User.tenant_code == tenant_code)
        if status is not None:
            query = query.where(User.status == status)

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(User.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, data: UserUpdate
    ) -> Optional[User]:
        """更新用户"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise BizException("用户不存在")

        update_data = data.model_dump(exclude_unset=True)
        role_ids = update_data.pop("role_ids", None)

        for key, value in update_data.items():
            setattr(user, key, value)

        # 更新角色关联
        if role_ids is not None:
            # 删除旧关联
            old_roles = await db.execute(
                select(UserRole).where(UserRole.user_id == user_id)
            )
            for ur in old_roles.scalars().all():
                await db.delete(ur)
            # 添加新关联
            for role_id in role_ids:
                db.add(UserRole(user_id=user_id, role_id=role_id))

        await db.flush()
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """删除用户（软删除）"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise BizException("用户不存在")
        user.is_deleted = 1
        await db.flush()
        return True

    @staticmethod
    async def reset_password(
        db: AsyncSession, user_id: int, new_password: str
    ) -> bool:
        """重置密码"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise BizException("用户不存在")
        user.password = hash_password(new_password)
        await db.flush()
        return True

    @staticmethod
    async def update_password(
        db: AsyncSession, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """修改密码"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise BizException("用户不存在")
        if not verify_password(old_password, user.password):
            raise BizException("原密码错误")
        user.password = hash_password(new_password)
        await db.flush()
        return True
