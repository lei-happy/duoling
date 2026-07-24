"""开放平台 · 能力注册表用例（纯逻辑，零 DB 依赖）

覆盖对外契约的单一事实源：
1. 注册 / 查询 / 按通道过滤 / 稳定性下线过滤；
2. dispatch 对 needs_tenant_db=False 能力的执行；
3. 字段裁剪（output_fields）+ 敏感字段脱敏（sensitive_fields）；
4. 分页结果 {list,total,...} 与裸列表两种形态的整形。

用一个临时注册的测试能力做断言，避免污染内置能力集合。
"""

from __future__ import annotations

import pytest

from app.modules.open_platform.capabilities import registry
from app.modules.open_platform.capabilities.context import OpenContext


@pytest.fixture()
def _temp_caps():
    """注册两个临时能力，用例结束后从注册表移除。"""
    added = []

    @registry.register_capability(
        code="test.echo",
        name="回显",
        category="测试",
        channels=["api", "mcp"],
        needs_tenant_db=False,
        output_fields=["id", "name", "phone"],
        sensitive_fields=["phone"],
        sort_order=1,
    )
    async def _echo(ctx: OpenContext, params: dict, db):
        return {
            "list": [
                {"id": 1, "name": "甲", "phone": "13812345678", "secret": "hide"},
                {"id": 2, "name": "乙", "phone": "139", "secret": "hide"},
            ],
            "total": 2,
            "page": 1,
            "pageSize": 20,
        }
    added.append("test.echo")

    @registry.register_capability(
        code="test.mcponly",
        name="仅MCP",
        channels=["mcp"],
        needs_tenant_db=False,
        sort_order=2,
    )
    async def _mcp_only(ctx: OpenContext, params: dict, db):
        return {"ok": True}
    added.append("test.mcponly")

    yield
    for code in added:
        registry._REGISTRY.pop(code, None)


def _ctx():
    return OpenContext(tenant_code="1001", channel="api", scope=["test.echo"])


def test_get_and_list(_temp_caps):
    assert registry.get_capability("test.echo") is not None
    codes = [s.code for s in registry.list_capabilities()]
    assert "test.echo" in codes and "test.mcponly" in codes


def test_list_channel_filter(_temp_caps):
    api_codes = [s.code for s in registry.list_capabilities(channel="api")]
    assert "test.echo" in api_codes
    assert "test.mcponly" not in api_codes  # 仅 mcp 通道，不进 api 列表


async def test_dispatch_trims_and_masks(_temp_caps):
    """裁剪到 output_fields，且 phone 脱敏；secret 不在输出字段被丢弃。"""
    result = await registry.dispatch("test.echo", {}, _ctx())
    rows = result["list"]
    assert result["total"] == 2
    assert set(rows[0].keys()) == {"id", "name", "phone"}
    assert "secret" not in rows[0]
    assert rows[0]["phone"] == "138****5678"  # 11 位掩码
    assert rows[1]["phone"] == "***"          # 短号兜底掩码


async def test_dispatch_unknown_capability_raises(_temp_caps):
    from app.common.exceptions import BizException

    with pytest.raises(BizException):
        await registry.dispatch("nope.not.exist", {}, _ctx())


def test_shape_result_bare_list(_temp_caps):
    spec = registry.get_capability("test.echo")
    shaped = registry._shape_result(
        [{"id": 9, "name": "丙", "phone": "13900000000", "x": 1}], spec
    )
    assert set(shaped[0].keys()) == {"id", "name", "phone"}
    assert shaped[0]["phone"] == "139****0000"


def test_offline_capability_hidden(_temp_caps):
    """稳定性置为 offline 的能力不出现在 list_capabilities。"""
    spec = registry.get_capability("test.echo")
    original = spec.stability
    spec.stability = "offline"
    try:
        codes = [s.code for s in registry.list_capabilities()]
        assert "test.echo" not in codes
    finally:
        spec.stability = original
