"""驾驶员资金账户（往来账）测试

分两层：
1. 纯逻辑：`_resolve_delta` 的符号推导（零 DB）；
2. 集成：连真实租户库 ``1001``，在**外层事务中执行并最终回滚**，
   不落任何数据。若本地无法连接租户库则整体 skip。

对应设计：doc/02.需求文档/02.企业端/07.财务结算模块/07.驾驶员资金账户.md
"""

from decimal import Decimal

import pytest

from app.common.exceptions import BizException
from app.modules.client.services.capacity.self_capacity.driver.driver_fund_account_service import (
    DriverFundAccountService,
)


# =====================================================================
# 1) 纯逻辑：delta 符号推导
# =====================================================================
class TestResolveDelta:
    def test_prepay_register_is_negative(self):
        assert DriverFundAccountService._resolve_delta(1, Decimal("100"), None) == Decimal("-100")

    def test_refund_in_is_positive(self):
        assert DriverFundAccountService._resolve_delta(2, Decimal("100"), None) == Decimal("100")

    def test_manual_in_is_positive(self):
        assert DriverFundAccountService._resolve_delta(3, Decimal("100"), None) == Decimal("100")

    def test_manual_out_is_negative(self):
        assert DriverFundAccountService._resolve_delta(4, Decimal("100"), None) == Decimal("-100")

    def test_adjust_in(self):
        assert DriverFundAccountService._resolve_delta(5, Decimal("100"), 1) == Decimal("100")

    def test_adjust_out(self):
        assert DriverFundAccountService._resolve_delta(5, Decimal("100"), 2) == Decimal("-100")

    def test_adjust_requires_direction(self):
        with pytest.raises(BizException):
            DriverFundAccountService._resolve_delta(5, Decimal("100"), None)

    @pytest.mark.parametrize("bad", [0, 3])
    def test_adjust_invalid_direction(self, bad):
        with pytest.raises(BizException):
            DriverFundAccountService._resolve_delta(5, Decimal("100"), bad)


# =====================================================================
# 2) 集成测试（真实租户库，事务回滚）
# =====================================================================
_TENANT = "1001"


@pytest.fixture()
async def db_and_driver():
    """连接租户库，开启外层事务并在结束时回滚；预置一个临时 driver 行。"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.core.config import get_settings
    from app.modules.client.models.capacity.self_capacity.driver.driver import (
        Driver,
    )

    settings = get_settings()
    try:
        engine = create_async_engine(settings.tenant_db_url(_TENANT))
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 环境无 DB 时跳过
        pytest.skip(f"租户库 {_TENANT} 不可连接：{e}")

    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        driver = Driver(
            driver_code="TEST_FUND_DRV",
            name="资金测试司机",
            phone="19900000000",
            status=1,
        )
        session.add(driver)
        await session.flush()
        yield session, int(driver.id)
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()


class _Payload:
    """轻量替代 DriverFundTransactionCreate（避免每次构造 schema）"""

    def __init__(self, bizType, amount, direction=None, remark=None,
                 relatedTaskId=None, relatedFinanceDocId=None, voucherUrl=None):
        self.bizType = bizType
        self.amount = Decimal(str(amount))
        self.direction = direction
        self.remark = remark
        self.relatedTaskId = relatedTaskId
        self.relatedFinanceDocId = relatedFinanceDocId
        self.voucherUrl = voucherUrl


@pytest.mark.asyncio
class TestFundAccountIntegration:
    async def test_lazy_create_zero_balance(self, db_and_driver):
        db, driver_id = db_and_driver
        acc = await DriverFundAccountService.get_account(db, driver_id)
        assert acc.balance == Decimal("0.00")
        assert acc.status == 1

    async def test_prepay_then_settle_flow(self, db_and_driver):
        db, driver_id = db_and_driver
        # 预付登记 5000 → 余额 -5000
        t1 = await DriverFundAccountService.post_transaction(
            db, driver_id, _Payload(1, 5000), operator_id=None
        )
        assert t1.delta == Decimal("-5000.00")
        assert t1.direction == 2
        assert t1.balanceAfter == Decimal("-5000.00")

        # 人工入账 6000 → 余额 +1000
        t2 = await DriverFundAccountService.post_transaction(
            db, driver_id, _Payload(3, 6000), operator_id=None
        )
        assert t2.balanceBefore == Decimal("-5000.00")
        assert t2.balanceAfter == Decimal("1000.00")

        acc = await DriverFundAccountService.get_account(db, driver_id)
        assert acc.balance == Decimal("1000.00")
        assert acc.totalIn == Decimal("6000.00")
        assert acc.totalOut == Decimal("5000.00")

    async def test_adjust_requires_remark(self, db_and_driver):
        db, driver_id = db_and_driver
        with pytest.raises(BizException):
            await DriverFundAccountService.post_transaction(
                db, driver_id, _Payload(5, 100, direction=1, remark="短"),
                operator_id=None,
            )

    async def test_amount_must_be_positive(self, db_and_driver):
        db, driver_id = db_and_driver
        with pytest.raises(BizException):
            await DriverFundAccountService.post_transaction(
                db, driver_id, _Payload(3, 0), operator_id=None
            )

    async def test_balance_equals_sum_of_delta(self, db_and_driver):
        db, driver_id = db_and_driver
        for p in [_Payload(1, 1000), _Payload(3, 500), _Payload(4, 200),
                  _Payload(5, 300, direction=1, remark="期初调整补录")]:
            await DriverFundAccountService.post_transaction(
                db, driver_id, p, operator_id=None
            )
        items, total = await DriverFundAccountService.list_transactions(
            db, driver_id, page=1, page_size=50
        )
        assert total == 4
        sum_delta = sum(Decimal(str(it["delta"])) for it in items)
        acc = await DriverFundAccountService.get_account(db, driver_id)
        assert acc.balance == sum_delta

    async def test_frozen_blocks_posting(self, db_and_driver):
        db, driver_id = db_and_driver
        acc = await DriverFundAccountService.get_account(db, driver_id)
        await DriverFundAccountService.toggle_status(db, acc.id, 0)
        with pytest.raises(BizException):
            await DriverFundAccountService.post_transaction(
                db, driver_id, _Payload(3, 100), operator_id=None
            )

    async def test_system_register_prepay_idempotent(self, db_and_driver):
        db, driver_id = db_and_driver
        t1 = await DriverFundAccountService.system_register_prepay(
            db, owner_id=driver_id, amount=Decimal("3000"),
            enterprise_id=None, task_id=999, finance_doc_id=8888,
            operator_id=None, doc_no="FY-TEST",
        )
        assert t1 is not None
        assert t1.delta == Decimal("-3000.00")
        # 幂等：同一费用单再次登记应跳过
        t2 = await DriverFundAccountService.system_register_prepay(
            db, owner_id=driver_id, amount=Decimal("3000"),
            enterprise_id=None, task_id=999, finance_doc_id=8888,
            operator_id=None, doc_no="FY-TEST",
        )
        assert t2 is None

    async def test_system_reverse_prepay(self, db_and_driver):
        db, driver_id = db_and_driver
        await DriverFundAccountService.system_register_prepay(
            db, owner_id=driver_id, amount=Decimal("3000"),
            enterprise_id=None, task_id=999, finance_doc_id=7777,
            operator_id=None,
        )
        acc_before = await DriverFundAccountService.get_account(db, driver_id)
        assert acc_before.balance == Decimal("-3000.00")

        r1 = await DriverFundAccountService.system_reverse_prepay(
            db, finance_doc_id=7777, operator_id=None,
        )
        assert r1 is not None
        assert r1.delta == Decimal("3000.00")
        acc_after = await DriverFundAccountService.get_account(db, driver_id)
        assert acc_after.balance == Decimal("0.00")

        # 幂等：重复冲正应跳过
        r2 = await DriverFundAccountService.system_reverse_prepay(
            db, finance_doc_id=7777, operator_id=None,
        )
        assert r2 is None


# =====================================================================
# 3) 集成测试：社会运力资金账户（owner_type=3，泛化后同一套账本）
# =====================================================================
@pytest.fixture()
async def db_and_social():
    """连接租户库，开启外层事务并回滚；预置一个临时社会运力行。"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.core.config import get_settings
    from app.modules.client.models.capacity.social_capacity.social_capacity import (
        SocialCapacity,
    )

    settings = get_settings()
    try:
        engine = create_async_engine(settings.tenant_db_url(_TENANT))
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 环境无 DB 时跳过
        pytest.skip(f"租户库 {_TENANT} 不可连接：{e}")

    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        cap = SocialCapacity(
            social_code="TEST_FUND_SC",
            driver_name="资金测试社会运力",
            driver_phone="19900000001",
            plate_number="测A00000",
            approval_status=2,
            status=1,
        )
        session.add(cap)
        await session.flush()
        yield session, int(cap.id)
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()


_OWNER_SOCIAL = 3


@pytest.mark.asyncio
class TestSocialFundAccountIntegration:
    async def test_lazy_create_zero_balance(self, db_and_social):
        db, capacity_id = db_and_social
        acc = await DriverFundAccountService.get_account(
            db, capacity_id, owner_type=_OWNER_SOCIAL
        )
        assert acc.balance == Decimal("0.00")
        assert acc.ownerType == _OWNER_SOCIAL
        assert acc.ownerId == capacity_id

    async def test_prepay_then_settle_flow(self, db_and_social):
        db, capacity_id = db_and_social
        t1 = await DriverFundAccountService.post_transaction(
            db, capacity_id, _Payload(1, 5000),
            operator_id=None, owner_type=_OWNER_SOCIAL,
        )
        assert t1.delta == Decimal("-5000.00")
        assert t1.ownerType == _OWNER_SOCIAL

        t2 = await DriverFundAccountService.post_transaction(
            db, capacity_id, _Payload(3, 6000),
            operator_id=None, owner_type=_OWNER_SOCIAL,
        )
        assert t2.balanceAfter == Decimal("1000.00")

        acc = await DriverFundAccountService.get_account(
            db, capacity_id, owner_type=_OWNER_SOCIAL
        )
        assert acc.balance == Decimal("1000.00")

    async def test_balance_equals_sum_of_delta(self, db_and_social):
        db, capacity_id = db_and_social
        for p in [_Payload(1, 1000), _Payload(3, 500), _Payload(4, 200),
                  _Payload(5, 300, direction=1, remark="期初调整补录")]:
            await DriverFundAccountService.post_transaction(
                db, capacity_id, p, operator_id=None, owner_type=_OWNER_SOCIAL,
            )
        items, total = await DriverFundAccountService.list_transactions(
            db, capacity_id, owner_type=_OWNER_SOCIAL, page=1, page_size=50
        )
        assert total == 4
        sum_delta = sum(Decimal(str(it["delta"])) for it in items)
        acc = await DriverFundAccountService.get_account(
            db, capacity_id, owner_type=_OWNER_SOCIAL
        )
        assert acc.balance == sum_delta

    async def test_owner_isolation_driver_vs_social(self, db_and_social):
        """同 id 的自有司机与社会运力账户互不影响（owner_type 隔离）。"""
        db, capacity_id = db_and_social
        await DriverFundAccountService.post_transaction(
            db, capacity_id, _Payload(3, 800),
            operator_id=None, owner_type=_OWNER_SOCIAL,
        )
        social_acc = await DriverFundAccountService.get_account(
            db, capacity_id, owner_type=_OWNER_SOCIAL
        )
        assert social_acc.balance == Decimal("800.00")

    async def test_unknown_social_rejected(self, db_and_social):
        db, _capacity_id = db_and_social
        with pytest.raises(BizException):
            await DriverFundAccountService.get_account(
                db, 999_000_111, owner_type=_OWNER_SOCIAL
            )
