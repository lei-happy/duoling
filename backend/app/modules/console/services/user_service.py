"""
用户管理服务
"""

from typing import Optional, List, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.console.models.user import User
from app.modules.console.models.role import Role
from app.modules.console.models.user_role import UserRole
from app.modules.console.schemas.user import (
    UserOut, UserCreate, UserUpdate, UserRoleItem,
)


SEX_MAP = {0: None, 1: "男", 2: "女"}
SEX_REVERSE = {"男": 1, "女": 2}


class UserService:
    """用户管理服务"""

    @staticmethod
    async def _get_user_roles(db: AsyncSession, user_id: int) -> List[UserRoleItem]:
        """获取用户的角色列表"""
        result = await db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.is_deleted == 0)
        )
        roles = result.scalars().all()
        return [
            UserRoleItem(roleId=r.id, roleCode=r.role_code, roleName=r.role_name)
            for r in roles
        ]

    @staticmethod
    async def _to_out(db: AsyncSession, u: User) -> UserOut:
        """将 ORM 模型转换为输出"""
        roles = await UserService._get_user_roles(db, u.id)
        return UserOut(
            userId=u.id,
            phone=u.phone,
            nickname=u.real_name,
            avatar=u.avatar,
            sex=SEX_MAP.get(u.gender),
            email=u.email,
            status=u.status,
            organizationId=None,
            organizationName=None,
            roles=roles,
            createTime=u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else None,
        )

    @staticmethod
    async def page_users(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        phone: Optional[str] = None,
        nickname: Optional[str] = None,
        status: Optional[int] = None,
        sex: Optional[str] = None,
    ) -> dict:
        """分页查询用户（仅平台管理员 user_type=0）"""
        query = select(User).where(User.is_deleted == 0, User.user_type == 0)
        if phone:
            query = query.where(User.phone.contains(phone))
        if nickname:
            query = query.where(User.real_name.contains(nickname))
        if status is not None:
            query = query.where(User.status == status)
        if sex:
            gender = SEX_REVERSE.get(sex)
            if gender is not None:
                query = query.where(User.gender == gender)

        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        query = query.order_by(User.id.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        out_list = []
        for u in items:
            out_list.append(await UserService._to_out(db, u))

        return {
            "list": [item.model_dump() for item in out_list],
            "count": count,
        }

    @staticmethod
    async def list_users(
        db: AsyncSession,
        phone: Optional[str] = None,
    ) -> List[UserOut]:
        """查询用户列表（不分页，仅平台管理员 user_type=0）"""
        query = select(User).where(User.is_deleted == 0, User.user_type == 0)
        if phone:
            query = query.where(User.phone.contains(phone))
        query = query.order_by(User.id.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        out_list = []
        for u in items:
            out_list.append(await UserService._to_out(db, u))
        return out_list

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> UserOut:
        """根据 ID 查询用户"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")
        return await UserService._to_out(db, user)

    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate) -> None:
        """新增用户"""
        existing = await db.execute(
            select(User).where(User.phone == data.phone, User.is_deleted == 0)
        )
        if existing.scalar_one_or_none():
            raise BizException("该手机号已存在")

        gender = SEX_REVERSE.get(data.sex, 0) if data.sex else 0
        user = User(
            phone=data.phone,
            password=hash_password(data.password or "123456"),
            real_name=data.nickname,
            avatar=data.avatar,
            gender=gender,
            email=data.email,
            user_type=0,
            status=data.status if data.status is not None else 1,
        )
        db.add(user)
        await db.flush()

        if data.roles:
            for role_id in data.roles:
                db.add(UserRole(user_id=user.id, role_id=role_id))
            await db.flush()

    @staticmethod
    async def update_user(db: AsyncSession, data: UserUpdate) -> None:
        """修改用户"""
        result = await db.execute(
            select(User).where(User.id == data.userId, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")

        if data.phone is not None:
            dup = await db.execute(
                select(User).where(
                    User.phone == data.phone,
                    User.id != data.userId,
                    User.is_deleted == 0,
                )
            )
            if dup.scalar_one_or_none():
                raise BizException("该手机号已存在")
            user.phone = data.phone
        if data.nickname is not None:
            user.real_name = data.nickname
        if data.avatar is not None:
            user.avatar = data.avatar
        if data.sex is not None:
            user.gender = SEX_REVERSE.get(data.sex, 0)
        if data.email is not None:
            user.email = data.email
        if data.status is not None:
            user.status = data.status

        if data.roles is not None:
            await db.execute(
                delete(UserRole).where(UserRole.user_id == data.userId)
            )
            for role_id in data.roles:
                db.add(UserRole(user_id=data.userId, role_id=role_id))

        await db.flush()

    @staticmethod
    async def batch_delete(db: AsyncSession, user_ids: List[int]) -> None:
        """批量删除用户（软删除）"""
        result = await db.execute(
            select(User).where(User.id.in_(user_ids), User.is_deleted == 0)
        )
        users = result.scalars().all()
        for u in users:
            u.is_deleted = 1
        await db.flush()

    @staticmethod
    async def update_status(db: AsyncSession, user_id: int, status: int) -> None:
        """修改用户状态"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == 0)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")
        user.status = status
        await db.flush()

    @staticmethod
    async def check_existence(
        db: AsyncSession, field: str, value: str, user_id: Optional[int] = None
    ) -> bool:
        """检查字段是否已存在"""
        if field == "phone":
            query = select(User).where(User.phone == value, User.is_deleted == 0)
        else:
            return False
        if user_id:
            query = query.where(User.id != user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
