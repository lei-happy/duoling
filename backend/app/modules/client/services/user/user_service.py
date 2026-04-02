"""
企业端员工管理服务（租户库）
"""

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

import secrets

from app.common.exceptions import BizException
from app.common.utils import hash_password
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.user.biz_user_role import BizUserRole
from app.modules.client.models.role.biz_role import BizRole
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.schemas.user.user import (
    BizUserCreate, BizUserUpdate, BizUserOut,
)

SEX_TO_GENDER = {"男": 1, "女": 2}

# 与前端表格列 prop 对齐，仅允许白名单字段参与排序
_USER_SORT_COLUMNS = {
    "createTime": BizUser.created_at,
    "id": BizUser.id,
}


def _user_list_order_clauses(sort: Optional[str], order: Optional[str]):
    """解析列表/分页排序，非法或未传时按 id 降序（与历史默认一致）。"""
    col = _USER_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [desc(BizUser.id)]
    direction = (order or "desc").strip().lower()
    primary = asc(col) if direction == "asc" else desc(col)
    # 创建时间可能相同，用 id 保证顺序稳定、分页不重复/不漏
    if col is BizUser.created_at:
        return [primary, desc(BizUser.id)]
    return [primary]


def _parse_birthday_optional(value: Optional[str]) -> Optional[date]:
    if value is None or not str(value).strip():
        return None
    try:
        return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


class BizUserService:

    @staticmethod
    def _apply_user_filters(
        base,
        *,
        phone: Optional[str] = None,
        nickname: Optional[str] = None,
        status: Optional[int] = None,
        sex: Optional[str] = None,
        organization_id: Optional[int] = None,
        dept_ids: Optional[List[int]] = None,
    ):
        if phone:
            base = base.where(BizUser.phone.contains(phone))
        if nickname:
            base = base.where(
                (BizUser.nickname.contains(nickname)) |
                (BizUser.real_name.contains(nickname))
            )
        if status is not None:
            base = base.where(BizUser.status == status)
        if sex:
            gender = SEX_TO_GENDER.get(sex)
            if gender is not None:
                base = base.where(BizUser.gender == gender)
        if organization_id is not None and dept_ids is not None:
            base = base.where(BizUser.department_id.in_(dept_ids))
        return base

    @staticmethod
    async def page_users(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        phone: Optional[str] = None,
        nickname: Optional[str] = None,
        status: Optional[int] = None,
        sex: Optional[str] = None,
        organization_id: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        base = select(BizUser).where(BizUser.is_deleted == 0)
        dept_ids = None
        if organization_id is not None:
            dept_ids = await BizUserService._get_dept_and_children_ids(db, organization_id)
        base = BizUserService._apply_user_filters(
            base,
            phone=phone,
            nickname=nickname,
            status=status,
            sex=sex,
            organization_id=organization_id,
            dept_ids=dept_ids,
        )

        count_q = select(func.count()).select_from(base.subquery())
        count = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(*_user_list_order_clauses(sort, order))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        users = result.scalars().all()

        items = []
        for u in users:
            roles = await BizUserService._get_user_roles(db, u.id)
            dept_name = await BizUserService._get_dept_name(db, u.department_id)
            items.append(BizUserOut.from_model(u, roles=roles, dept_name=dept_name))

        return {
            "list": [item.model_dump() for item in items],
            "count": count,
        }

    @staticmethod
    async def list_users(
        db: AsyncSession,
        phone: Optional[str] = None,
        nickname: Optional[str] = None,
        status: Optional[int] = None,
        sex: Optional[str] = None,
        organization_id: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[dict]:
        """查询员工列表（不分页，用于导出等场景）"""
        base = select(BizUser).where(BizUser.is_deleted == 0)
        dept_ids = None
        if organization_id is not None:
            dept_ids = await BizUserService._get_dept_and_children_ids(db, organization_id)
        base = BizUserService._apply_user_filters(
            base,
            phone=phone,
            nickname=nickname,
            status=status,
            sex=sex,
            organization_id=organization_id,
            dept_ids=dept_ids,
        )

        result = await db.execute(base.order_by(*_user_list_order_clauses(sort, order)))
        users = result.scalars().all()

        items = []
        for u in users:
            roles = await BizUserService._get_user_roles(db, u.id)
            dept_name = await BizUserService._get_dept_name(db, u.department_id)
            items.append(BizUserOut.from_model(u, roles=roles, dept_name=dept_name).model_dump())
        return items

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> dict:
        """根据ID查询员工详情"""
        result = await db.execute(
            select(BizUser).where(
                BizUser.id == user_id,
                BizUser.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")

        roles = await BizUserService._get_user_roles(db, user.id)
        dept_name = await BizUserService._get_dept_name(db, user.department_id)
        return BizUserOut.from_model(user, roles=roles, dept_name=dept_name).model_dump()

    @staticmethod
    async def _get_dept_and_children_ids(db: AsyncSession, dept_id: int) -> List[int]:
        """递归获取部门及其所有子部门的 ID 列表"""
        result = await db.execute(
            select(BizDepartment).where(BizDepartment.is_deleted == 0)
        )
        all_depts = result.scalars().all()

        dept_map = {}
        for d in all_depts:
            dept_map.setdefault(d.parent_id, []).append(d.id)

        ids = [dept_id]
        queue = [dept_id]
        while queue:
            pid = queue.pop(0)
            children = dept_map.get(pid, [])
            ids.extend(children)
            queue.extend(children)
        return ids

    @staticmethod
    async def _get_dept_name(db: AsyncSession, dept_id: Optional[int]) -> Optional[str]:
        if not dept_id:
            return None
        result = await db.execute(
            select(BizDepartment.dept_name).where(
                BizDepartment.id == dept_id,
                BizDepartment.is_deleted == 0,
            )
        )
        return result.scalar()

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
        existing = await db.execute(
            select(BizUser).where(
                BizUser.phone == data.phone,
                BizUser.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"手机号 {data.phone} 已存在")

        gender = SEX_TO_GENDER.get(data.sex, 0) if data.sex else 0

        raw_password = data.password or secrets.token_urlsafe(16)
        user = BizUser(
            phone=data.phone,
            password=hash_password(raw_password),
            real_name=data.realName or data.nickname,
            nickname=data.nickname,
            email=data.email,
            gender=gender,
            birthday=_parse_birthday_optional(data.birthday),
            user_type=data.userType,
            department_id=data.organizationId,
            status=data.status,
            remark=data.introduction,
        )
        db.add(user)
        await db.flush()

        if data.roleIds:
            for rid in data.roleIds:
                db.add(BizUserRole(user_id=user.id, role_id=rid))
            await db.flush()

        await db.refresh(user)
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

        if data.nickname is not None:
            user.nickname = data.nickname
        if data.realName is not None:
            user.real_name = data.realName
        if data.phone is not None:
            dup = await db.execute(
                select(BizUser).where(
                    BizUser.phone == data.phone,
                    BizUser.id != user_id,
                    BizUser.is_deleted == 0,
                )
            )
            if dup.scalar_one_or_none():
                raise BizException("该手机号已存在")
            user.phone = data.phone
        if data.email is not None:
            user.email = data.email
        if data.avatar is not None:
            user.avatar = data.avatar
        if data.sex is not None:
            user.gender = SEX_TO_GENDER.get(data.sex, 0)
        if data.organizationId is not None:
            user.department_id = data.organizationId
        if data.userType is not None:
            user.user_type = data.userType
        if data.status is not None:
            user.status = data.status
        if data.introduction is not None:
            user.remark = data.introduction
        if "birthday" in data.model_fields_set:
            user.birthday = _parse_birthday_optional(data.birthday)

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
        await db.refresh(user)
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
    async def batch_delete_users(db: AsyncSession, user_ids: List[int]) -> None:
        for uid in user_ids:
            result = await db.execute(
                select(BizUser).where(
                    BizUser.id == uid,
                    BizUser.is_deleted == 0,
                )
            )
            user = result.scalar_one_or_none()
            if user:
                if user.user_type == 1:
                    raise BizException(f"管理员账号 {user.phone} 无法删除")
                user.is_deleted = 1
        await db.flush()

    @staticmethod
    async def update_status(db: AsyncSession, user_id: int, status: int) -> None:
        result = await db.execute(
            select(BizUser).where(
                BizUser.id == user_id,
                BizUser.is_deleted == 0,
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise BizException("用户不存在")
        user.status = status
        await db.flush()

    @staticmethod
    async def check_existence(
        db: AsyncSession, field: str, value: str, exclude_id: Optional[int] = None
    ) -> bool:
        """检查字段值是否已存在"""
        column = getattr(BizUser, field, None)
        if column is None:
            raise BizException(f"不支持的字段: {field}")

        query = select(BizUser).where(
            column == value,
            BizUser.is_deleted == 0,
        )
        if exclude_id:
            query = query.where(BizUser.id != exclude_id)

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
