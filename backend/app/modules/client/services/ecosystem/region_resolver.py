"""地区解析：把租户侧的 region_id 翻译成省/市/区 + 行政区划代码

为什么需要这一层（详见 07.数据库设计.md §3.4）：

租户库的源单（任务单、运力档案）只存 ``origin_region_id`` 这类**租户库内的自增 ID**，
而平台库的挂牌需要 ``from_province`` / ``from_city``（大厅筛选靠它，且省份非空）
和 ``from_region_code``（全局稳定的行政区划代码）。两者之间必须显式翻译：
``biz_region.id`` 在每个租户库里都不一样，直接搬到平台库就是脏数据。

``biz_region`` 是 ``code`` + ``parent_code`` 的链式结构（level 1 省 / 2 市 / 3 区县 /
4 企业自定义子级），所以解析要沿着 ``parent_code`` 往上走。这里按**层级批量加载**：
无论传入多少个 region，最多 4 次查询（层级深度上限），不会退化成 N+1。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.region.biz_region import BizRegion

# biz_region.level
LEVEL_PROVINCE = 1
LEVEL_CITY = 2
LEVEL_DISTRICT = 3
LEVEL_CUSTOM = 4

# biz_region.source
SOURCE_SYSTEM = 0

# 省 → 市 → 区 → 自定义，正常最多 4 层。多留一层容错，
# 同时作为脏数据成环时的熔断上限（parent_code 指回自己会死循环）。
MAX_DEPTH = 5


@dataclass(frozen=True)
class ResolvedRegion:
    """一个地区解析后的结果"""

    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    # 链路上最深一级**系统**地区的行政区划代码。
    # 注意精度可能低于已填的最深名称层级：租户自建了一个「市」时，city 有值但它的
    # code 指不到 sys_regions，此时退到省级代码。宁可粗一级，也不写悬空引用。
    region_code: Optional[int] = None

    @property
    def is_usable(self) -> bool:
        """能否用于挂牌

        省份是硬要求：``sys_eco_post.from_province`` 非空，且大厅筛选完全依赖它。
        解析不出省份的挂牌进了大厅也搜不到，等于白发。
        """
        return bool(self.province)

    @property
    def display(self) -> str:
        """省市区拼接串，用于缺少展示串时兜底"""
        return "".join(p for p in (self.province, self.city, self.district) if p)


EMPTY = ResolvedRegion()


class RegionResolver:
    """租户库地区解析"""

    @staticmethod
    async def resolve(db: AsyncSession, region_id: Optional[int]) -> ResolvedRegion:
        """解析单个地区"""
        if not region_id:
            return EMPTY
        return (await RegionResolver.resolve_many(db, [region_id])).get(
            int(region_id), EMPTY
        )

    @staticmethod
    async def resolve_many(
        db: AsyncSession, region_ids: Iterable[Optional[int]]
    ) -> Dict[int, ResolvedRegion]:
        """批量解析，返回 ``{region_id: ResolvedRegion}``

        解析失败（ID 不存在、链路断裂）的 ID 不会出现在返回值里，
        调用方用 ``dict.get(id, EMPTY)`` 处理即可——静默给个空对象比抛异常更合适，
        因为发布场景下要把「地址不全」作为业务提示回给用户，而不是 500。
        """
        wanted = {int(r) for r in region_ids if r}
        if not wanted:
            return {}

        rows = (
            await db.execute(
                select(BizRegion).where(
                    BizRegion.id.in_(wanted),
                    BizRegion.is_deleted == 0,
                )
            )
        ).scalars().all()
        if not rows:
            return {}

        by_code = {r.code: r for r in rows}
        pending = {r.parent_code for r in rows if r.parent_code}

        # 逐层向上补齐祖先：每层一次查询，与传入数量无关
        for _ in range(MAX_DEPTH):
            missing = {c for c in pending if c and c not in by_code}
            if not missing:
                break
            ancestors = (
                await db.execute(
                    select(BizRegion).where(
                        BizRegion.code.in_(missing),
                        BizRegion.is_deleted == 0,
                    )
                )
            ).scalars().all()
            if not ancestors:
                break
            pending = set()
            for a in ancestors:
                by_code[a.code] = a
                if a.parent_code:
                    pending.add(a.parent_code)

        return {
            int(r.id): RegionResolver._build(r, by_code)
            for r in rows
        }

    @staticmethod
    async def ids_by_codes(
        db: AsyncSession, codes: Iterable[Optional[int]]
    ) -> Dict[int, int]:
        """行政区划代码 → 租户库 ``biz_region.id``，解析的反方向

        编辑运力挂牌时用得到：平台库存的是区划代码与省市名，而重建草稿要的是
        租户库 ID。挂牌上的代码是发布时从系统地区取的，所以这里也只认系统地区
        （``source=0``）——租户自建地区的 code 是自己编的，反查会撞上同名代码。

        查不到的代码不出现在返回值里（地区被删过），调用方按缺失处理即可。
        """
        wanted = {int(c) for c in codes if c}
        if not wanted:
            return {}
        rows = (
            await db.execute(
                select(BizRegion.id, BizRegion.code).where(
                    BizRegion.code.in_([str(c) for c in wanted]),
                    BizRegion.source == SOURCE_SYSTEM,
                    BizRegion.is_deleted == 0,
                )
            )
        ).all()
        result: Dict[int, int] = {}
        for region_id, code in rows:
            code = (code or "").strip()
            if code.isdigit():
                # 同一个代码有多行时保留第一条：正常数据下不会出现
                result.setdefault(int(code), int(region_id))
        return result

    # ------------------------------------------------------------------

    @staticmethod
    def _build(row: BizRegion, by_code: Dict[str, BizRegion]) -> ResolvedRegion:
        """沿 parent_code 向上收集整条链，再按层级归位"""
        chain: List[BizRegion] = []
        seen = set()
        current: Optional[BizRegion] = row
        while current is not None and len(chain) < MAX_DEPTH:
            if current.code in seen:
                break  # 脏数据成环，停在这里而不是死循环
            seen.add(current.code)
            chain.append(current)
            current = by_code.get(current.parent_code) if current.parent_code else None

        names: Dict[int, str] = {}
        region_code: Optional[int] = None
        for node in chain:
            level = int(node.level or 0)
            if level in (LEVEL_PROVINCE, LEVEL_CITY, LEVEL_DISTRICT):
                # chain 由深到浅，同层级只取第一个（最深的那个）
                names.setdefault(level, node.name)
                if region_code is None:
                    # 拿不到就继续往上找，退到粗一级的代码也比留空好
                    region_code = RegionResolver._standard_code(node)

        return ResolvedRegion(
            province=names.get(LEVEL_PROVINCE),
            city=names.get(LEVEL_CITY),
            district=names.get(LEVEL_DISTRICT),
            region_code=region_code,
        )

    @staticmethod
    def _standard_code(node: BizRegion) -> Optional[int]:
        """取行政区划代码

        只认系统地区（``source=0``）的代码：企业自定义地区的 code 是租户自己编的，
        写进平台库会变成指向 ``sys_regions`` 的悬空引用。代码为空不影响大厅筛选
        （筛选走省市名称），所以宁缺勿错。
        """
        if int(node.source or 0) != SOURCE_SYSTEM:
            return None
        code = (node.code or "").strip()
        return int(code) if code.isdigit() else None


async def resolve_pair(
    db: AsyncSession,
    from_region_id: Optional[int],
    to_region_id: Optional[int],
) -> tuple[ResolvedRegion, ResolvedRegion]:
    """一次查询解析起点与终点，避免发布时查两轮"""
    resolved = await RegionResolver.resolve_many(
        db, [from_region_id, to_region_id]
    )
    return (
        resolved.get(int(from_region_id), EMPTY) if from_region_id else EMPTY,
        resolved.get(int(to_region_id), EMPTY) if to_region_id else EMPTY,
    )
