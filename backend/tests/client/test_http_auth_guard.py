"""企业端 · HTTP 鉴权门槛冒烟测试（不触发 lifespan / 不落库）

验证受保护接口在**未携带 / 携带非法 Token** 时被中间件与依赖层正确拦截，
而不会返回 200 成功。这些用例在 ``get_current_user`` / ``TenantMiddleware``
层即被拒绝，不触达数据库，因此无需 DB 也能稳定执行。

对应需求：项目文档/02.需求文档/02.企业端/01.账号与组织/**
对应代码：backend/app/core/middleware.py、backend/app/core/dependencies.py
覆盖用例：TC-CLI-AUTH-010 ~ TC-CLI-AUTH-020
"""

from __future__ import annotations

import pytest

# 一批「必须登录」的 GET 接口（选取只依赖 get_current_user / 租户上下文的路径）
PROTECTED_GET_PATHS = [
    "/api/client/auth/user-info",
    "/api/client/auth/menu-version",
    "/api/client/auth/user-tenants",
    "/api/client/system/user",
    "/api/client/partner/customer",
    "/api/client/resource/customer",
]

# 鉴权失败的合理 HTTP 状态：401 未登录 / 400 缺租户 / 403 无权限
REJECT_STATUS = {400, 401, 403}


class TestAuthGuard:
    @pytest.mark.parametrize("path", PROTECTED_GET_PATHS)
    async def test_missing_token_rejected(self, http_client, path):
        resp = await http_client.get(path)
        assert resp.status_code in REJECT_STATUS, (
            f"{path} 未带 Token 应被拒绝，实得 {resp.status_code}: {resp.text}"
        )
        body = resp.json()
        assert body.get("code") != 0

    @pytest.mark.parametrize("path", PROTECTED_GET_PATHS)
    async def test_garbage_token_rejected(self, http_client, path):
        resp = await http_client.get(
            path, headers={"Authorization": "Bearer not-a-real-jwt"}
        )
        assert resp.status_code in REJECT_STATUS
        assert resp.json().get("code") != 0

    async def test_health_ok_without_auth(self, http_client):
        resp = await http_client.get("/health")
        assert resp.status_code == 200
        assert resp.json().get("status") == "ok"

    async def test_unknown_path_404(self, http_client):
        resp = await http_client.get("/api/client/__no_such_endpoint__")
        assert resp.status_code == 404
