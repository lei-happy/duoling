"""公开产品版本 / 版本功能矩阵 / 更新日志接口测试

对应需求：项目文档/06.测试用例体系/04.开放接口与LITE与运力宝/02.公开产品与更新日志.md
对应后端：backend/app/modules/open/api/product.py
         backend/app/modules/open/api/changelog.py
覆盖用例：TC-OPN-PRODUCT-001 ~ TC-OPN-PRODUCT-004、TC-OPN-CHANGELOG-001 ~ 003

均为无需认证的只读接口，验证响应结构与分页参数校验。平台库不可达时 skip。
"""

import pytest


@pytest.mark.asyncio
class TestProductHttp:
    async def test_list_versions(self, platform_client):
        """TC-OPN-PRODUCT-001：产品版本列表（公开）"""
        resp = await platform_client.get("/api/open/product/versions")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert isinstance(body["data"], list)

    async def test_version_features_matrix(self, platform_client):
        """TC-OPN-PRODUCT-002：版本×功能矩阵结构完整（versions/modules/features）"""
        resp = await platform_client.get("/api/open/product/version-features")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert set(["versions", "modules", "features"]).issubset(data.keys())
        assert isinstance(data["versions"], list)
        assert isinstance(data["modules"], list)
        assert isinstance(data["features"], list)
        # 若有功能项，includedIn 必须为列表
        for f in data["features"]:
            assert isinstance(f["includedIn"], list)
            assert "featureCode" in f


@pytest.mark.asyncio
class TestChangelogHttp:
    async def test_list_default_page(self, platform_client):
        """TC-OPN-CHANGELOG-001：更新日志默认分页（仅已发布）"""
        resp = await platform_client.get("/api/open/changelog")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert set(["list", "total", "page", "page_size"]).issubset(data.keys())
        assert data["page"] == 1
        assert data["page_size"] == 20

    async def test_custom_page_size(self, platform_client):
        """TC-OPN-CHANGELOG-002：自定义分页参数生效"""
        resp = await platform_client.get(
            "/api/open/changelog", params={"page": 2, "page_size": 5}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["page"] == 2
        assert body["data"]["page_size"] == 5

    @pytest.mark.parametrize("params", [{"page": 0}, {"page_size": 0}, {"page_size": 101}])
    async def test_invalid_pagination_422(self, platform_client, params):
        """TC-OPN-CHANGELOG-003：分页参数越界 → 422"""
        resp = await platform_client.get("/api/open/changelog", params=params)
        assert resp.status_code == 422
