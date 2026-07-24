"""开放平台 · 控制面管理服务用例（平台库集成，事务回滚不落库）

直连 service 层，覆盖租户在「接入应用 / API 凭证 / MCP 配置」上的完整生命周期：
- 应用：创建 → 列表带凭证计数 → 更新 → 越权/非法状态拦截；
- API 凭证：创建返回一次性明文且密文可解回、更新 scope、重置密钥、吊销；
- MCP 配置：创建签发 Bearer Token + 可复制 config_json、改名不动 slug、吊销软删；
- 能力目录：list_for_display 结构、scope 校验拒绝未注册能力。

使用 conftest 的 platform_session（外层事务，结束回滚），任何写入都不落库。
平台库不可连接时整体 skip。
"""

from __future__ import annotations

import pytest

from app.common.exceptions import BizException
from app.modules.open_platform.security import keygen
from app.modules.open_platform.services.app_service import AppService
from app.modules.open_platform.services.credential_service import CredentialService
from app.modules.open_platform.services.mcp_service import McpService
from app.modules.open_platform.services.capability_service import CapabilityService

TENANT = "1001"
USER_ID = 1


# ============================================================
# 接入应用
# ============================================================

async def test_app_create_list_update(platform_session):
    db = platform_session
    app = await AppService.create_app(db, TENANT, "对接测试应用", "用于CRUD测试", USER_ID)
    assert app.id and app.status == "enabled"

    apps = await AppService.list_apps(db, TENANT)
    hit = [a for a in apps if a["id"] == app.id]
    assert hit and hit[0]["credential_count"] == 0

    updated = await AppService.update_app(db, TENANT, app.id, name="改名后", status="disabled")
    assert updated.name == "改名后" and updated.status == "disabled"


async def test_app_invalid_status_rejected(platform_session):
    db = platform_session
    app = await AppService.create_app(db, TENANT, "应用X", "", USER_ID)
    with pytest.raises(BizException):
        await AppService.update_app(db, TENANT, app.id, status="whatever")


async def test_app_cross_tenant_isolation(platform_session):
    db = platform_session
    app = await AppService.create_app(db, TENANT, "隔离测试", "", USER_ID)
    with pytest.raises(BizException):
        await AppService.get_app(db, "9999", app.id)  # 他租户不可见


# ============================================================
# API 凭证
# ============================================================

async def test_credential_lifecycle(platform_session):
    db = platform_session
    app = await AppService.create_app(db, TENANT, "凭证应用", "", USER_ID)

    created = await CredentialService.create_credential(
        db, TENANT, app.id,
        scope=["ping", "customer.query"], ip_whitelist="", expires_at=None, user_id=USER_ID,
    )
    # 一次性明文返回，且库内密文可解回同一明文
    assert created["secret"].startswith("sk_")
    assert created["access_key"].startswith("ak_")
    from app.modules.open_platform.models.platform.open_credential import OpenCredential
    from sqlalchemy import select
    row = await db.scalar(select(OpenCredential).where(OpenCredential.id == created["id"]))
    assert keygen.decrypt_secret(row.secret_store) == created["secret"]

    # 列表可见，且应用凭证计数 +1
    creds = await CredentialService.list_credentials(db, TENANT, app.id)
    assert any(c["id"] == created["id"] for c in creds)
    apps = await AppService.list_apps(db, TENANT)
    assert [a for a in apps if a["id"] == app.id][0]["credential_count"] == 1

    # 更新 scope
    upd = await CredentialService.update_scope(
        db, TENANT, created["id"], scope=["ping"], ip_whitelist="1.2.3.4",
    )
    assert upd["scope"] == ["ping"] and upd["ip_whitelist"] == "1.2.3.4"

    # 重置密钥：产生新明文，且与旧的不同
    reset = await CredentialService.reset_secret(db, TENANT, created["id"])
    assert reset["secret"].startswith("sk_") and reset["secret"] != created["secret"]

    # 吊销后不再计入应用有效凭证数
    await CredentialService.revoke(db, TENANT, created["id"])
    apps2 = await AppService.list_apps(db, TENANT)
    assert [a for a in apps2 if a["id"] == app.id][0]["credential_count"] == 0


async def test_credential_invalid_scope_rejected(platform_session):
    db = platform_session
    app = await AppService.create_app(db, TENANT, "凭证应用2", "", USER_ID)
    with pytest.raises(BizException):
        await CredentialService.create_credential(
            db, TENANT, app.id,
            scope=["not.a.real.capability"], ip_whitelist="", expires_at=None, user_id=USER_ID,
        )


# ============================================================
# MCP 配置
# ============================================================

async def test_mcp_config_lifecycle(platform_session):
    db = platform_session
    app = await AppService.create_app(db, TENANT, "MCP应用", "", USER_ID)

    cfg = await McpService.create_config(
        db, TENANT, app.id,
        display_name="我的智途助手", enabled_capabilities=["ping", "waybill.query"], user_id=USER_ID,
    )
    slug = cfg["server_slug"]
    assert cfg["token"] and "." in cfg["token"]  # access_key.token 形态
    # 可复制配置 JSON 结构正确，服务名可自定义
    servers = cfg["config_json"]["mcpServers"]
    assert "我的智途助手" in servers
    assert servers["我的智途助手"]["headers"]["Authorization"].startswith("Bearer ")
    assert servers["我的智途助手"]["url"].endswith(f"/mcp/{slug}")

    # 签发的 mcp 凭证：库内存哈希，可用明文 token 校验
    token_plain = cfg["token"].split(".", 1)[1]
    from app.modules.open_platform.models.platform.open_credential import OpenCredential
    from sqlalchemy import select
    cred = await db.scalar(
        select(OpenCredential).where(
            OpenCredential.app_id == app.id, OpenCredential.cred_type == "mcp"
        )
    )
    assert keygen.verify_secret(token_plain, cred.secret_store)

    # 改名不改 slug（不影响已连接的客户端）
    renamed = await McpService.update_config(db, TENANT, cfg["id"], display_name="新名字")
    assert renamed["display_name"] == "新名字" and renamed["server_slug"] == slug

    # 列表可见 → 吊销后软删不再出现
    assert any(c["id"] == cfg["id"] for c in await McpService.list_configs(db, TENANT, app.id))
    await McpService.revoke(db, TENANT, cfg["id"])
    assert all(c["id"] != cfg["id"] for c in await McpService.list_configs(db, TENANT, app.id))


# ============================================================
# 能力目录
# ============================================================

def test_capability_list_for_display():
    items = CapabilityService.list_for_display()
    codes = {i["code"] for i in items}
    assert {"ping", "customer.query", "vehicle.query", "waybill.query"} <= codes
    ping = [i for i in items if i["code"] == "ping"][0]
    assert ping["read_only"] is True and "api" in ping["channels"]


def test_capability_list_channel_filter():
    api_items = CapabilityService.list_for_display(channel="api")
    assert all("api" in i["channels"] for i in api_items)
