"""计费引擎 · 地名标准化测试

覆盖 BUG-CLI-001：以「州/盟/旗」结尾的地级市省略「市」后缀时，
`_expand_leaf_name_variants` 仍应生成「…市」等候选以命中层级路径。

对应代码：backend/app/modules/client/services/billing/standardize_service.py
覆盖用例：TC-CLI-BILLING-101、TC-CLI-WAYBILL-050
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.services.billing.standardize_service import (
    StandardizeService,
    _expand_leaf_name_variants,
)


class TestExpandLeafNameVariants:
    def test_zhou_stem_appends_city_candidate(self):
        variants = _expand_leaf_name_variants("达州")
        assert variants[0] == "达州"
        assert "达州市" in variants

    def test_meng_stem_appends_city_candidate(self):
        variants = _expand_leaf_name_variants("锡林郭勒")
        assert "锡林郭勒" in variants
        assert "锡林郭勒市" in variants

    def test_full_city_suffix_not_duplicated(self):
        assert _expand_leaf_name_variants("达州市") == ["达州市"]

    def test_province_suffix_skips_completion(self):
        assert _expand_leaf_name_variants("河北省") == ["河北省"]

    def test_empty_returns_empty(self):
        assert _expand_leaf_name_variants("") == []
        assert _expand_leaf_name_variants("   ") == []


class TestResolveRegionHierarchicalPath:
    async def test_omit_city_suffix_matches_full_path(self, tenant_session):
        """省略「市」后缀应与写全称解析到同一 region_id。"""
        result = await tenant_session.execute(
            select(BizRegion)
            .where(
                BizRegion.is_deleted == 0,
                BizRegion.level == 2,
                BizRegion.name.like("%州市"),
            )
            .limit(1)
        )
        city = result.scalar_one_or_none()
        if city is None:
            pytest.skip("租户库无「…州市」地级市样本")

        chain = await StandardizeService._load_region_chain(tenant_session, city)
        names = [n.name for n in reversed(chain)]
        assert len(names) >= 2

        stem = city.name[:-1] if city.name.endswith("市") else city.name
        full_path = "/".join(names)
        omit_path = "/".join(names[:-1] + [stem])

        full = await StandardizeService.resolve_region(
            tenant_session, raw_name=full_path
        )
        omit = await StandardizeService.resolve_region(
            tenant_session, raw_name=omit_path
        )

        assert full.region_id == city.id
        assert full.matched_by == "path"
        assert omit.region_id == city.id
        assert omit.matched_by == "path"
