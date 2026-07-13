"""驾驶员上下文 ``get_current_driver`` 鉴权与档案锁定测试

分两层：
1. 纯逻辑：会话缺少企业上下文 / 非驾驶员账号（user_type != 3）在触库前即被拒；
2. 集成：连租户库 ``1001``，验证 user_id 命中、离职/冻结拒绝、无档案拒绝。

对应需求：doc/02.需求文档/03.移动端/02.驾驶员H5端/01.账号体系与多企业切换.md §六
覆盖用例：TC-DRV-AUTH-008/009/010、TC-DRV-PROFILE-004
"""

import pytest

from app.common.exceptions import BizException, PermissionException
from app.modules.driver.services.driver_context import get_current_driver
from tests.driver.conftest import make_token


# =====================================================================
# 1) 纯逻辑守卫（触库前拒绝，tenant_db 传 None 亦不会被访问）
# =====================================================================
class TestGuards:
    async def test_missing_tenant_code_rejected(self):
        token = make_token(tenant_code=None)
        with pytest.raises(BizException):
            await get_current_driver(None, token)

    async def test_non_driver_user_type_rejected(self):
        # user_type=2（普通用户）不允许访问 driver API
        token = make_token(user_type=2)
        with pytest.raises(PermissionException):
            await get_current_driver(None, token)


# =====================================================================
# 2) 集成（真实租户库，事务回滚）
# =====================================================================
class TestResolveDriver:
    async def test_resolve_by_user_id(self, driver_ctx):
        session, ctx = driver_ctx
        token = make_token(user_id=ctx.user_id, phone=ctx.phone)
        resolved = await get_current_driver(session, token)
        assert resolved.driver_id == ctx.driver_id
        assert resolved.driver.driver_code == "TEST_DRV_H5"

    async def test_frozen_driver_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        ctx.driver.status = 0  # 冻结
        await session.flush()
        token = make_token(user_id=ctx.user_id, phone=ctx.phone)
        with pytest.raises(PermissionException):
            await get_current_driver(session, token)

    async def test_resigned_driver_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        ctx.driver.status = 2  # 离职
        await session.flush()
        token = make_token(user_id=ctx.user_id, phone=ctx.phone)
        with pytest.raises(PermissionException):
            await get_current_driver(session, token)

    async def test_no_profile_rejected(self, tenant_session):
        # 未在本企业开通司机档案的 user_id / phone
        token = make_token(user_id=888777, phone="19900009999")
        with pytest.raises(BizException):
            await get_current_driver(tenant_session, token)
