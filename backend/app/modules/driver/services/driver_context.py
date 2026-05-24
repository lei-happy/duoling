"""
驾驶员上下文工具

所有 ``/api/driver`` 接口在切到租户库后，需要锁定"当前手机号所对应的本企业内
biz_driver 行"，再以 driver_id 作为业务过滤主键。该锁定动作通过
``DriverContext.fetch(...)`` 完成，幂等可重复调用。
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException, PermissionException
from app.core.security import TokenData
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver


@dataclass
class DriverContext:
    """驾驶员上下文（与 token 一一对应）"""

    user_id: int
    phone: str
    tenant_code: str
    driver: Driver

    @property
    def driver_id(self) -> int:
        return int(self.driver.id)


async def get_current_driver(
    tenant_db: AsyncSession,
    current_user: TokenData,
) -> DriverContext:
    """
    锁定当前企业内的 biz_driver 行。

    优先按 ``user_id`` 匹配（员工同步时已写入 driver.user_id）；
    回退到 ``phone`` 匹配，兼容历史数据。

    校验：
    - 必须存在 user_type=3（驾驶员）的 sys_user_tenant 关联 → 由登录入口保证；
      此处仅校验 biz_driver 是否存在且 status ∈ {1 在职}
    - 不存在 → 抛 BizException("当前企业未配置您的驾驶员档案")
    """
    if not current_user.tenant_code:
        raise BizException("当前会话缺少企业上下文")

    # user_type=3 才能调 driver API
    if int(current_user.user_type or 0) != 3:
        raise PermissionException("仅驾驶员账号可访问")

    # 1) 优先按 user_id
    drv: Optional[Driver] = None
    stmt = select(Driver).where(
        Driver.user_id == current_user.user_id,
        Driver.is_deleted == 0,
    )
    res = await tenant_db.execute(stmt)
    drv = res.scalar_one_or_none()

    # 2) fallback：按 phone
    if drv is None and current_user.phone:
        stmt = select(Driver).where(
            Driver.phone == current_user.phone,
            Driver.is_deleted == 0,
        )
        res = await tenant_db.execute(stmt)
        drv = res.scalar_one_or_none()

    if drv is None:
        raise BizException("当前企业未配置您的驾驶员档案，请联系企业管理员")

    if int(drv.status) != 1:
        raise PermissionException("您的驾驶员账号已被冻结或离职，无法访问")

    return DriverContext(
        user_id=current_user.user_id,
        phone=current_user.phone,
        tenant_code=current_user.tenant_code,
        driver=drv,
    )
