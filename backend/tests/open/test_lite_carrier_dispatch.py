"""LITE 端 - 承运商运力上报接口测试（契约占位实现）

对应需求：doc/02.需求文档/03.LITE端/承运商运力上报.md
         doc/06.测试用例体系/04.开放接口与LITE与运力宝/04.LITE承运商运力上报.md
对应后端：backend/app/modules/open/api/lite_carrier_dispatch.py
覆盖用例：TC-OPN-LITE-001 ~ TC-OPN-LITE-007

分两层：
1. 纯逻辑：LiteCarrierDispatchRequest 入参 schema 校验（零 DB）；
2. HTTP 集成：租户解析、token 校验、任务状态校验（BUG-OPN-001 已修复）。
"""

import pytest
from pydantic import ValidationError

from app.modules.open.api.lite_carrier_dispatch import (
    LiteCarrierDispatchRequest,
    _parse_lite_tenant_code,
)
from app.common.exceptions import BizException

LITE_PLACEHOLDER_TOKEN = "dummy-lite-token"
TEST_TENANT = "1001"


def _lite_dispatch_url(task_id: int, tenant_code: str = TEST_TENANT) -> str:
    return f"/api/open/lite/carrier/task/{task_id}/dispatch?tenant_code={tenant_code}"


def _lite_dispatch_body(**override) -> dict:
    data = dict(
        mainDriverName="李司机",
        mainDriverPhone="13800000000",
        plateNumber="京A12345",
    )
    data.update(override)
    return data


def _lite_dispatch_headers(token: str = LITE_PLACEHOLDER_TOKEN) -> dict:
    return {"X-Lite-Token": token}


# =====================================================================
# 1) 纯逻辑：入参 schema & 租户解析
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


class TestLiteTenantParse:
    """TC-OPN-LITE-004：从 token / 查询参数解析 tenant_code"""

    def test_missing_token(self):
        with pytest.raises(BizException, match="缺少 lite token"):
            _parse_lite_tenant_code(None)

    def test_placeholder_token_with_query_param(self):
        assert _parse_lite_tenant_code(
            LITE_PLACEHOLDER_TOKEN, tenant_code_param=TEST_TENANT
        ) == TEST_TENANT

    def test_placeholder_token_without_tenant(self):
        with pytest.raises(BizException, match="无法从 lite token 解析租户信息"):
            _parse_lite_tenant_code(LITE_PLACEHOLDER_TOKEN)


# =====================================================================
# 2) HTTP 集成
# =====================================================================
@pytest.mark.asyncio
class TestLiteDispatchHttp:
    async def test_resolves_tenant_via_query_param(self, lite_dispatch_client):
        """TC-OPN-LITE-004：携带 tenant_code 后可进入业务逻辑（不再 400 缺租户）。"""
        resp = await lite_dispatch_client.post_dispatch(999_999_999)
        assert resp.status_code == 200
        body = resp.json()
        # 任务不存在等业务错误，而非 TenantException 400
        assert body["code"] != 0
        assert "租户" not in body["message"]

    async def test_missing_token_returns_biz_error(self, platform_client):
        """TC-OPN-LITE-005：缺少 X-Lite-Token → 业务错误「缺少 lite token」。"""
        resp = await platform_client.post(
            _lite_dispatch_url(1),
            json=_lite_dispatch_body(),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] != 0
        assert "lite token" in body["message"]

    async def test_token_without_tenant_rejected(self, platform_client):
        """TC-OPN-LITE-004：占位 token 无 tenant_code 参数 → 业务错误。"""
        resp = await platform_client.post(
            "/api/open/lite/carrier/task/1/dispatch",
            headers=_lite_dispatch_headers(),
            json=_lite_dispatch_body(),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] != 0
        assert "租户" in body["message"]

    async def test_body_validation_still_422(self, lite_dispatch_client):
        """TC-OPN-LITE-006：请求体缺必填字段仍应 422（参数校验早于依赖执行）"""
        resp = await lite_dispatch_client.post_dispatch(
            1,
            json={"mainDriverName": "李司机"},
        )
        assert resp.status_code == 422

    async def test_dispatch_on_seeded_carrier_task(self, tenant_session):
        """TC-OPN-LITE-007：carrier_type=2 / status=0 任务可成功上报推进至 status=1。"""
        from datetime import datetime

        from app.modules.client.models.task.task import Task
        from app.modules.open.api.lite_carrier_dispatch import _dispatch_on_tenant_db

        task = Task(
            task_no=f"LITE_TEST_{datetime.now().strftime('%H%M%S%f')}",
            carrier_type=2,
            carrier_id=None,
            carrier_name="测试承运商",
            status=0,
        )
        tenant_session.add(task)
        await tenant_session.flush()

        req = LiteCarrierDispatchRequest(**_lite_dispatch_body())
        result = await _dispatch_on_tenant_db(
            tenant_session, int(task.id), req, LITE_PLACEHOLDER_TOKEN
        )
        assert result["code"] == 0
        assert result["data"]["status"] == 1
        assert result["data"]["taskNo"] == task.task_no
