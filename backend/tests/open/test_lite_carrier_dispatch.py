"""LITE 端 - 承运商运力上报接口测试（契约占位实现）

对应需求：项目文档/02.需求文档/03.LITE端/承运商运力上报.md
         项目文档/06.测试用例体系/04.开放接口与LITE与运力宝/04.LITE承运商运力上报.md
对应后端：backend/app/modules/open/api/lite_carrier_dispatch.py
覆盖用例：TC-OPN-LITE-001 ~ TC-OPN-LITE-006

分两层：
1. 纯逻辑：LiteCarrierDispatchRequest 入参 schema 校验（零 DB）；
2. HTTP 集成：暴露占位实现的租户上下文缺陷（BUG-OPN-001）。
"""

import pytest
from pydantic import ValidationError

from app.modules.open.api.lite_carrier_dispatch import LiteCarrierDispatchRequest


# =====================================================================
# 1) 纯逻辑：入参 schema
# =====================================================================
class TestDispatchSchema:
    """TC-OPN-LITE-001/002：运力上报必填字段与长度约束"""

    def _base(self, **override):
        data = dict(
            mainDriverName="李司机",
            mainDriverPhone="13800000000",
            plateNumber="京A12345",
        )
        data.update(override)
        return data

    def test_valid_minimal(self):
        req = LiteCarrierDispatchRequest(**self._base())
        assert req.capacityId is None
        assert req.mainDriverName == "李司机"

    def test_optional_fields(self):
        req = LiteCarrierDispatchRequest(
            **self._base(
                capacityId=9999,
                mainDriverIdCard="110101199001011234",
                trailerPlateNumber="京A98765",
            )
        )
        assert req.capacityId == 9999
        assert req.trailerPlateNumber == "京A98765"

    @pytest.mark.parametrize("missing", ["mainDriverName", "mainDriverPhone", "plateNumber"])
    def test_missing_required(self, missing):
        data = self._base()
        data.pop(missing)
        with pytest.raises(ValidationError):
            LiteCarrierDispatchRequest(**data)

    def test_phone_too_short(self):
        with pytest.raises(ValidationError):
            LiteCarrierDispatchRequest(**self._base(mainDriverPhone="12345"))

    def test_plate_too_short(self):
        with pytest.raises(ValidationError):
            LiteCarrierDispatchRequest(**self._base(plateNumber="A"))


# =====================================================================
# 2) HTTP 集成：占位实现的租户上下文缺陷
# =====================================================================
@pytest.mark.asyncio
class TestLiteDispatchHttp:
    async def test_open_path_has_no_tenant_context(self, platform_client):
        """TC-OPN-LITE-004（BUG-OPN-001）：开放路径无法解析租户上下文。

        ``/api/open/*`` 被 TenantMiddleware 跳过 token 解析，
        ``request.state.tenant_code`` 恒为 None；而本接口依赖 ``get_tenant_db``
        （其 ``get_tenant_code`` 会因缺租户抛 ``TenantException`` → HTTP 400）。
        因此占位接口在任何合法入参下都无法进入业务逻辑，token/任务状态校验形同虚设。
        """
        resp = await platform_client.post(
            "/api/open/lite/carrier/task/1/dispatch",
            headers={"X-Lite-Token": "dummy-token"},
            json={
                "mainDriverName": "李司机",
                "mainDriverPhone": "13800000000",
                "plateNumber": "京A12345",
            },
        )
        # 现状：租户依赖先抛错 → 400（记录为缺陷 BUG-OPN-001）
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == 400
        assert "租户" in body["message"]

    async def test_missing_token_also_blocked_by_tenant(self, platform_client):
        """TC-OPN-LITE-005：缺少 X-Lite-Token 时，同样先被租户依赖拦截（暴露校验顺序问题）。

        期望（需求 3.2）：应先校验 token 非空 → 返回"缺少 lite token"业务错误；
        实际：租户依赖在 handler 之前抛 400，token 校验无法生效。
        """
        resp = await platform_client.post(
            "/api/open/lite/carrier/task/1/dispatch",
            json={
                "mainDriverName": "李司机",
                "mainDriverPhone": "13800000000",
                "plateNumber": "京A12345",
            },
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == 400

    async def test_body_validation_still_422(self, platform_client):
        """TC-OPN-LITE-006：请求体缺必填字段仍应 422（参数校验早于依赖执行）"""
        resp = await platform_client.post(
            "/api/open/lite/carrier/task/1/dispatch",
            headers={"X-Lite-Token": "dummy-token"},
            json={"mainDriverName": "李司机"},
        )
        assert resp.status_code == 422
