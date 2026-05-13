"""
标准化服务（计费引擎 Phase 2）

职责：
  - 把运单/导入数据中的非标准地名 / 品牌+车型字符串映射到 ID
    * 地名 → biz_region.id
    * 品牌 → biz_vehicle_brand.brand_id
    * 品牌+车系 → biz_vehicle_series.series_id
  - 优先使用 biz_region_alias / biz_vehicle_alias 中的别名映射
  - 提供 region 树上溯（用于地区层级匹配）
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.region_alias import RegionAlias
from app.modules.client.models.billing.vehicle_alias import VehicleAlias
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import BizVehicleBrand
from app.modules.client.models.vehicle_basic.biz_vehicle_series import BizVehicleSeries


# ---- region.level → 文案 ----
REGION_LEVEL_LABEL = {
    1: "province",
    2: "city",
    3: "district",
    4: "custom",
}


def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


@dataclass
class RegionResolution:
    """单个地区解析结果"""

    region_id: Optional[int]
    region_code: Optional[str]
    region_name: Optional[str]
    level: Optional[int]
    matched_by: str  # id_input / code_input / alias / name / unresolved
    chain: list["RegionNode"]  # 该 region 自下而上到省的链路


@dataclass
class RegionNode:
    region_id: int
    code: str
    name: str
    level: int
    level_label: str


@dataclass
class VehicleResolution:
    """单个货物明细的车型解析结果"""

    brand_id: Optional[int]
    series_id: Optional[int]
    brand_name: Optional[str]
    series_name: Optional[str]
    matched_by: str  # ids_input / brand_alias / series_alias / brand_name / series_name / unresolved


def vehicle_alias_key(brand: Optional[str], model: Optional[str]) -> str:
    """与 waybill_brand_model_key 保持一致的内部键（'\\x1f' 分隔）"""
    return f"{_norm(brand)}\x1f{_norm(model)}"


class StandardizeService:

    # ---- region ----

    @staticmethod
    async def _load_region_chain(
        db: AsyncSession, region: BizRegion
    ) -> list[RegionNode]:
        """从给定 region 沿 parent_code 一路上溯，返回 [自身, 父级, 祖父级, ...]"""
        chain: list[RegionNode] = []
        cursor: Optional[BizRegion] = region
        seen: set[str] = set()
        while cursor and cursor.code not in seen:
            seen.add(cursor.code)
            chain.append(RegionNode(
                region_id=cursor.id,
                code=cursor.code,
                name=cursor.name,
                level=cursor.level,
                level_label=REGION_LEVEL_LABEL.get(cursor.level, "custom"),
            ))
            if not cursor.parent_code:
                break
            r = await db.execute(
                select(BizRegion).where(
                    BizRegion.code == cursor.parent_code,
                    BizRegion.is_deleted == 0,
                ).limit(1)
            )
            cursor = r.scalar_one_or_none()
        return chain

    @staticmethod
    async def _find_region_by_id(
        db: AsyncSession, region_id: int
    ) -> Optional[BizRegion]:
        r = await db.execute(
            select(BizRegion).where(
                BizRegion.id == region_id, BizRegion.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _find_region_by_code(
        db: AsyncSession, code: str
    ) -> Optional[BizRegion]:
        r = await db.execute(
            select(BizRegion).where(
                BizRegion.code == code, BizRegion.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _find_region_by_alias(
        db: AsyncSession, name: str
    ) -> Optional[BizRegion]:
        s = _norm(name)
        if not s:
            return None
        r = await db.execute(
            select(RegionAlias).where(
                RegionAlias.alias_name == s,
                RegionAlias.status == 1,
                RegionAlias.is_deleted == 0,
            )
        )
        alias = r.scalar_one_or_none()
        if not alias:
            return None
        return await StandardizeService._find_region_by_id(db, alias.region_id)

    @staticmethod
    async def _find_region_by_name(
        db: AsyncSession, name: str
    ) -> Optional[BizRegion]:
        """精确名字匹配。多个同名时返回 level 最深（区/县优先）的一条。"""
        s = _norm(name)
        if not s:
            return None
        r = await db.execute(
            select(BizRegion).where(
                BizRegion.name == s, BizRegion.is_deleted == 0,
            ).order_by(BizRegion.level.desc(), BizRegion.id.asc())
        )
        return r.scalars().first()

    @staticmethod
    async def resolve_region(
        db: AsyncSession,
        *,
        region_id: Optional[int] = None,
        code: Optional[str] = None,
        raw_name: Optional[str] = None,
    ) -> RegionResolution:
        """按 id → code → alias → name 的优先级解析地区。

        任一信息可为空；全部解析失败时 region_id=None 且 matched_by="unresolved"。
        """
        region: Optional[BizRegion] = None
        matched_by = "unresolved"

        if region_id:
            region = await StandardizeService._find_region_by_id(db, region_id)
            if region:
                matched_by = "id_input"

        if not region and code:
            region = await StandardizeService._find_region_by_code(db, code)
            if region:
                matched_by = "code_input"

        if not region and raw_name:
            region = await StandardizeService._find_region_by_alias(db, raw_name)
            if region:
                matched_by = "alias"
            else:
                region = await StandardizeService._find_region_by_name(db, raw_name)
                if region:
                    matched_by = "name"

        if not region:
            return RegionResolution(
                region_id=None, region_code=None, region_name=None,
                level=None, matched_by=matched_by, chain=[],
            )

        chain = await StandardizeService._load_region_chain(db, region)
        return RegionResolution(
            region_id=region.id,
            region_code=region.code,
            region_name=region.name,
            level=region.level,
            matched_by=matched_by,
            chain=chain,
        )

    # ---- vehicle ----

    @staticmethod
    async def _find_brand_by_name(
        db: AsyncSession, name: str
    ) -> Optional[BizVehicleBrand]:
        s = _norm(name)
        if not s:
            return None
        r = await db.execute(
            select(BizVehicleBrand).where(BizVehicleBrand.brand_name_cn == s)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _find_series_by_brand_and_name(
        db: AsyncSession, brand_id: int, series_name: str
    ) -> Optional[BizVehicleSeries]:
        s = _norm(series_name)
        if not s:
            return None
        r = await db.execute(
            select(BizVehicleSeries).where(
                BizVehicleSeries.brand_id == brand_id,
                BizVehicleSeries.series_name == s,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _find_alias(
        db: AsyncSession, alias_name: str, kind: str
    ) -> Optional[VehicleAlias]:
        r = await db.execute(
            select(VehicleAlias).where(
                VehicleAlias.alias_name == alias_name,
                VehicleAlias.alias_kind == kind,
                VehicleAlias.status == 1,
                VehicleAlias.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def resolve_vehicle(
        db: AsyncSession,
        *,
        brand_id: Optional[int] = None,
        series_id: Optional[int] = None,
        raw_brand: Optional[str] = None,
        raw_model: Optional[str] = None,
    ) -> VehicleResolution:
        """按 ids → series 别名 → brand 别名 → 名称精确 的优先级解析。"""
        # 1) ID 直给（认为已标准化）
        if brand_id and series_id:
            r = await db.execute(
                select(BizVehicleSeries).where(
                    BizVehicleSeries.series_id == series_id
                )
            )
            s = r.scalar_one_or_none()
            r2 = await db.execute(
                select(BizVehicleBrand).where(BizVehicleBrand.brand_id == brand_id)
            )
            b = r2.scalar_one_or_none()
            return VehicleResolution(
                brand_id=brand_id,
                series_id=series_id,
                brand_name=b.brand_name_cn if b else None,
                series_name=s.series_name if s else None,
                matched_by="ids_input",
            )

        # 2) 整体（品牌+车型）别名
        if raw_brand or raw_model:
            key = vehicle_alias_key(raw_brand, raw_model)
            alias = await StandardizeService._find_alias(db, key, "series")
            if alias and alias.brand_id and alias.series_id:
                r = await db.execute(
                    select(BizVehicleSeries).where(
                        BizVehicleSeries.series_id == alias.series_id
                    )
                )
                s = r.scalar_one_or_none()
                r2 = await db.execute(
                    select(BizVehicleBrand).where(
                        BizVehicleBrand.brand_id == alias.brand_id
                    )
                )
                b = r2.scalar_one_or_none()
                return VehicleResolution(
                    brand_id=alias.brand_id,
                    series_id=alias.series_id,
                    brand_name=b.brand_name_cn if b else _norm(raw_brand) or None,
                    series_name=s.series_name if s else _norm(raw_model) or None,
                    matched_by="series_alias",
                )

        # 3) 名称精确匹配
        brand_obj: Optional[BizVehicleBrand] = None
        if raw_brand:
            brand_obj = await StandardizeService._find_brand_by_name(db, raw_brand)
        # 品牌别名兜底
        if not brand_obj and raw_brand:
            alias = await StandardizeService._find_alias(db, _norm(raw_brand), "brand")
            if alias and alias.brand_id:
                r2 = await db.execute(
                    select(BizVehicleBrand).where(
                        BizVehicleBrand.brand_id == alias.brand_id
                    )
                )
                brand_obj = r2.scalar_one_or_none()
                if brand_obj and not raw_model:
                    return VehicleResolution(
                        brand_id=brand_obj.brand_id, series_id=None,
                        brand_name=brand_obj.brand_name_cn, series_name=None,
                        matched_by="brand_alias",
                    )

        if brand_obj and raw_model:
            series_obj = await StandardizeService._find_series_by_brand_and_name(
                db, brand_obj.brand_id, raw_model
            )
            if series_obj:
                return VehicleResolution(
                    brand_id=brand_obj.brand_id,
                    series_id=series_obj.series_id,
                    brand_name=brand_obj.brand_name_cn,
                    series_name=series_obj.series_name,
                    matched_by="series_name",
                )
            # 品牌命中但车系未命中：返回 brand-only
            return VehicleResolution(
                brand_id=brand_obj.brand_id, series_id=None,
                brand_name=brand_obj.brand_name_cn, series_name=_norm(raw_model) or None,
                matched_by="brand_name",
            )

        if brand_obj:
            return VehicleResolution(
                brand_id=brand_obj.brand_id, series_id=None,
                brand_name=brand_obj.brand_name_cn, series_name=None,
                matched_by="brand_name",
            )

        return VehicleResolution(
            brand_id=None, series_id=None,
            brand_name=_norm(raw_brand) or None,
            series_name=_norm(raw_model) or None,
            matched_by="unresolved",
        )
