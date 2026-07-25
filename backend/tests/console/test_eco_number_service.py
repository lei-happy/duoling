"""服务平台业务编号生成测试

编号一旦重复，挂牌会插入失败或串号，因此这里重点覆盖三条容易写错的路径：

1. Redis 正常自增；
2. Redis 不可用时回库续号；
3. **Redis 丢键重启**——INCR 从 1 重新开始，必须回库核对，否则与已有编号全线撞车。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/07.数据库设计.md §3.6
对应代码：backend/app/modules/console/services/ecosystem/eco_number_service.py
"""

from __future__ import annotations

from datetime import date

import pytest

from app.modules.console.models.ecosystem.constants import PostNoPrefix, PostType
from app.modules.console.services.ecosystem import eco_number_service
from app.modules.console.services.ecosystem.eco_number_service import (
    MAX_DAILY_SEQ,
    EcoNumberService,
)

DAY = date(2026, 7, 25)
DAY_STR = "20260725"


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return list(self._rows)


class FakeDb:
    """只需要满足 ``execute(...).scalars().all()``，无需真实数据库。"""

    def __init__(self, rows=()):
        self.rows = list(rows)
        self.execute_count = 0

    async def execute(self, _stmt):
        self.execute_count += 1
        return FakeResult(self.rows)


class FakeRedis:
    """够用的 Redis 替身：支持 incr / get / set / expire。"""

    def __init__(self, store=None, broken: bool = False):
        self.store = dict(store or {})
        self.broken = broken
        self.expire_calls = []

    def incr(self, key):
        if self.broken:
            raise RuntimeError("redis down")
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def get(self, key):
        if self.broken:
            raise RuntimeError("redis down")
        value = self.store.get(key)
        return None if value is None else str(value).encode()

    def set(self, key, value, ex=None):
        if self.broken:
            raise RuntimeError("redis down")
        self.store[key] = int(value)
        return True

    def expire(self, key, ttl):
        self.expire_calls.append((key, ttl))
        return True


@pytest.fixture(autouse=True)
def _reset_redis():
    eco_number_service.reset_redis_cache()
    yield
    eco_number_service.reset_redis_cache()


def use_redis(monkeypatch, client):
    """把模块内的 Redis 客户端换成替身。"""
    monkeypatch.setattr(eco_number_service, "_get_redis", lambda: client)


class TestFormat:
    """编号格式必须严格定长，下游有按位置解析的地方。"""

    @pytest.mark.asyncio
    async def test_shape(self, monkeypatch):
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": 41}))
        no = await EcoNumberService.next_no(FakeDb(), PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250042"
        assert len(no) == 14

    @pytest.mark.asyncio
    async def test_sequence_is_zero_padded_to_four(self, monkeypatch):
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": 6}))
        no = await EcoNumberService.next_no(FakeDb(), PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250007"

    @pytest.mark.asyncio
    async def test_cargo_and_capacity_use_different_prefixes(self, monkeypatch):
        """两个大厅共用 sys_eco_post，前缀是区分货源与运力的唯一线索。"""
        use_redis(monkeypatch, FakeRedis())
        cargo = await EcoNumberService.next_post_no(FakeDb(), PostType.CARGO)
        capacity = await EcoNumberService.next_post_no(FakeDb(), PostType.CAPACITY)
        assert cargo.startswith("HY")
        assert capacity.startswith("YL")

    @pytest.mark.asyncio
    async def test_prefix_per_business_object(self, monkeypatch):
        use_redis(monkeypatch, FakeRedis())
        for prefix in (
            PostNoPrefix.INTENT,
            PostNoPrefix.DEAL,
            PostNoPrefix.REPORT,
        ):
            no = await EcoNumberService.next_no(FakeDb(), prefix, today=DAY)
            assert no == f"{prefix}{DAY_STR}0001"

    @pytest.mark.asyncio
    async def test_unknown_prefix_rejected(self):
        with pytest.raises(ValueError):
            await EcoNumberService.next_no(FakeDb(), "XX", today=DAY)


class TestRedisPath:
    @pytest.mark.asyncio
    async def test_concurrent_calls_never_repeat(self, monkeypatch):
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": 10}))
        db = FakeDb()
        numbers = [
            await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
            for _ in range(50)
        ]
        assert len(set(numbers)) == 50

    @pytest.mark.asyncio
    async def test_ttl_refreshed_on_each_take(self, monkeypatch):
        """TTL 必须续，否则长尾流量下 key 中途过期会让流水回到 1。"""
        client = FakeRedis({f"eco:seq:HY:{DAY_STR}": 10})
        use_redis(monkeypatch, client)
        await EcoNumberService.next_no(FakeDb(), PostNoPrefix.CARGO_POST, today=DAY)
        assert client.expire_calls == [(f"eco:seq:HY:{DAY_STR}", 48 * 3600)]

    @pytest.mark.asyncio
    async def test_hot_path_does_not_touch_db(self, monkeypatch):
        """Redis 命中且非当日首号时不应查库，否则高频发布会把库压出来。"""
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": 10}))
        db = FakeDb()
        await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        assert db.execute_count == 0

    @pytest.mark.asyncio
    async def test_key_is_scoped_per_prefix_and_day(self, monkeypatch):
        """不同前缀、不同日期共用一个 key 会让流水互相吃掉。"""
        client = FakeRedis()
        use_redis(monkeypatch, client)
        await EcoNumberService.next_no(FakeDb(), PostNoPrefix.CARGO_POST, today=DAY)
        await EcoNumberService.next_no(FakeDb(), PostNoPrefix.INTENT, today=DAY)
        await EcoNumberService.next_no(
            FakeDb(), PostNoPrefix.CARGO_POST, today=date(2026, 7, 26)
        )
        assert set(client.store) == {
            f"eco:seq:HY:{DAY_STR}",
            f"eco:seq:YX:{DAY_STR}",
            "eco:seq:HY:20260726",
        }


class TestDbFallback:
    @pytest.mark.asyncio
    async def test_no_redis_uses_db_max_plus_one(self, monkeypatch):
        monkeypatch.setattr(eco_number_service, "_get_redis", lambda: None)
        db = FakeDb(["HY202607250001", "HY202607250007", "HY202607250003"])
        no = await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250008"

    @pytest.mark.asyncio
    async def test_no_redis_empty_day_starts_at_one(self, monkeypatch):
        monkeypatch.setattr(eco_number_service, "_get_redis", lambda: None)
        no = await EcoNumberService.next_no(FakeDb([]), PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250001"

    @pytest.mark.asyncio
    async def test_redis_error_degrades_to_db(self, monkeypatch):
        """Redis 抛异常不能让发布整体失败——降级取号即可。"""
        use_redis(monkeypatch, FakeRedis(broken=True))
        db = FakeDb(["HY202607250004"])
        no = await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250005"

    @pytest.mark.asyncio
    async def test_db_scan_ignores_malformed_and_other_days(self, monkeypatch):
        """库里可能混入历史脏数据，解析失败的行必须跳过而不是崩掉。"""
        monkeypatch.setattr(eco_number_service, "_get_redis", lambda: None)
        db = FakeDb(
            [
                "HY202607250002",
                "HY20260725",       # 缺流水段
                "HY202607250ABC",   # 流水段非数字
                None,
                "",
            ]
        )
        no = await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250003"

    @pytest.mark.asyncio
    async def test_prefer_db_bypasses_redis(self, monkeypatch):
        """唯一索引冲突后重试时，必须以库内水位为准，否则会反复撞同一批号。"""
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": 1}))
        db = FakeDb(["HY202607250009"])
        no = await EcoNumberService.next_no(
            db, PostNoPrefix.CARGO_POST, prefer_db=True, today=DAY
        )
        assert no == "HY202607250010"


class TestRedisKeyLossRecovery:
    """Redis 重启丢键是最危险的场景：INCR 回到 1，若不核对库就会全线撞号。"""

    @pytest.mark.asyncio
    async def test_first_seq_of_day_checks_db(self, monkeypatch):
        use_redis(monkeypatch, FakeRedis())
        db = FakeDb(["HY202607250012"])
        no = await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250013"
        assert db.execute_count == 1

    @pytest.mark.asyncio
    async def test_genuine_first_of_day_keeps_one(self, monkeypatch):
        """库里当天确实没有编号时，1 就是正确答案。"""
        use_redis(monkeypatch, FakeRedis())
        no = await EcoNumberService.next_no(FakeDb([]), PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607250001"

    @pytest.mark.asyncio
    async def test_redis_watermark_is_lifted_after_recovery(self, monkeypatch):
        """校准后下一次取号应直接接着走，不再回库。"""
        client = FakeRedis()
        use_redis(monkeypatch, client)
        db = FakeDb(["HY202607250012"])
        first = await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        second = await EcoNumberService.next_no(db, PostNoPrefix.CARGO_POST, today=DAY)
        assert (first, second) == ("HY202607250013", "HY202607250014")
        assert db.execute_count == 1

    @pytest.mark.asyncio
    async def test_watermark_never_moves_backwards(self, monkeypatch):
        """校准只能抬高水位。压低水位等于人为制造重复号。"""
        client = FakeRedis({f"eco:seq:HY:{DAY_STR}": 99})
        use_redis(monkeypatch, client)
        await EcoNumberService.next_no(
            FakeDb(["HY202607250003"]), PostNoPrefix.CARGO_POST, prefer_db=True, today=DAY
        )
        assert client.store[f"eco:seq:HY:{DAY_STR}"] == 99


class TestDailyCeiling:
    @pytest.mark.asyncio
    async def test_overflow_raises_instead_of_widening(self, monkeypatch):
        """流水溢出必须报错，静默滚到 5 位会打乱定长解析。"""
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": MAX_DAILY_SEQ}))
        with pytest.raises(ValueError):
            await EcoNumberService.next_no(FakeDb(), PostNoPrefix.CARGO_POST, today=DAY)

    @pytest.mark.asyncio
    async def test_last_available_number_still_works(self, monkeypatch):
        use_redis(monkeypatch, FakeRedis({f"eco:seq:HY:{DAY_STR}": MAX_DAILY_SEQ - 1}))
        no = await EcoNumberService.next_no(FakeDb(), PostNoPrefix.CARGO_POST, today=DAY)
        assert no == "HY202607259999"
