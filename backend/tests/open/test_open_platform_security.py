"""开放平台 · 安全原语用例（纯逻辑，零 DB 依赖）

覆盖数据面鉴权最关键的三块：
1. HMAC-SHA256 请求签名：正向可验、任一要素被篡改必失败；
2. 凭证生成/哈希/可逆加密：一次性明文、库存密文/哈希、恒定时间比对；
3. 限流与防重放：进程内降级实现的固定窗口计数与 nonce 去重。

这些用例不连数据库、不起服务，收集即可跑，是回归护栏的核心。
"""

from __future__ import annotations

import pytest

from app.modules.open_platform.security import keygen, signing, ratelimit


# ============================================================
# 1. HMAC 签名
# ============================================================

def _sign_case(secret: str):
    method = "POST"
    path = "/openapi/v1/customer.query"
    query = {"page": "1", "pageSize": "20"}
    body = b'{"keyword":"\xe5\x8c\x97\xe4\xba\xac"}'
    ts = "1710000000"
    nonce = "n-abc-123"
    sts = signing.build_string_to_sign(method, path, query, body, ts, nonce)
    sign = signing.sign(secret, sts)
    return method, path, query, body, ts, nonce, sign


def test_signature_roundtrip_ok():
    secret = keygen.gen_app_secret()
    method, path, query, body, ts, nonce, sign = _sign_case(secret)
    assert signing.verify_signature(
        secret, sign, method=method, path=path, query=query,
        body=body, timestamp=ts, nonce=nonce,
    )


def test_signature_query_order_insensitive():
    """规范化查询串按键排序，参数顺序不影响签名。"""
    secret = keygen.gen_app_secret()
    body = b""
    ts, nonce = "1710000000", "n1"
    s1 = signing.sign(
        secret,
        signing.build_string_to_sign("GET", "/p", {"a": "1", "b": "2"}, body, ts, nonce),
    )
    s2 = signing.sign(
        secret,
        signing.build_string_to_sign("GET", "/p", {"b": "2", "a": "1"}, body, ts, nonce),
    )
    assert s1 == s2


@pytest.mark.parametrize("tamper", ["secret", "sign", "body", "path", "ts", "nonce", "query"])
def test_signature_tamper_rejected(tamper):
    secret = keygen.gen_app_secret()
    method, path, query, body, ts, nonce, sign = _sign_case(secret)

    kw = dict(method=method, path=path, query=dict(query),
              body=body, timestamp=ts, nonce=nonce)
    use_secret, use_sign = secret, sign

    if tamper == "secret":
        use_secret = keygen.gen_app_secret()
    elif tamper == "sign":
        use_sign = sign[:-1] + ("0" if sign[-1] != "0" else "1")
    elif tamper == "body":
        kw["body"] = body + b"x"
    elif tamper == "path":
        kw["path"] = path + "/x"
    elif tamper == "ts":
        kw["timestamp"] = "1710000001"
    elif tamper == "nonce":
        kw["nonce"] = "n-different"
    elif tamper == "query":
        kw["query"]["page"] = "2"

    assert not signing.verify_signature(use_secret, use_sign, **kw)


def test_verify_empty_sign_rejected():
    secret = keygen.gen_app_secret()
    assert not signing.verify_signature(
        secret, "", method="GET", path="/p", query={}, body=b"",
        timestamp="1", nonce="n",
    )


# ============================================================
# 2. 凭证生成 / 哈希 / 可逆加密
# ============================================================

def test_key_prefixes_and_uniqueness():
    assert keygen.gen_app_key().startswith("ak_")
    assert keygen.gen_app_secret().startswith("sk_")
    assert keygen.gen_mcp_key().startswith("mcp_")
    assert keygen.gen_mcp_token().startswith("mcpt_")
    # 高熵：两次生成不重复
    assert keygen.gen_app_secret() != keygen.gen_app_secret()
    slug = keygen.gen_server_slug()
    assert len(slug) == 12 and slug != keygen.gen_server_slug()


def test_hash_secret_verify_roundtrip():
    """MCP Token：明文直传 + 哈希比对。"""
    token = keygen.gen_mcp_token()
    h = keygen.hash_secret(token)
    assert h and h != token
    assert keygen.verify_secret(token, h)
    assert not keygen.verify_secret(token + "x", h)
    assert not keygen.verify_secret(token, "")


def test_encrypt_decrypt_roundtrip():
    """API AppSecret：可逆加密落库，签名校验时取回明文。"""
    secret = keygen.gen_app_secret()
    ct = keygen.encrypt_secret(secret)
    assert ct and ct != secret
    assert keygen.decrypt_secret(ct) == secret
    # 同一明文两次加密密文不同（Fernet 带随机 IV），但都能解回
    ct2 = keygen.encrypt_secret(secret)
    assert ct2 != ct
    assert keygen.decrypt_secret(ct2) == secret


# ============================================================
# 3. 限流 / 防重放（进程内降级路径）
# ============================================================

@pytest.fixture(autouse=True)
def _force_local_ratelimit(monkeypatch):
    """强制走进程内实现：屏蔽 Redis，并清空本地计数，保证用例确定性。"""
    monkeypatch.setattr(ratelimit, "_get_redis", lambda: None)
    ratelimit.reset_local()
    yield
    ratelimit.reset_local()


def test_nonce_replay_detected():
    key = "ak_test:nonce-1"
    assert ratelimit.seen_nonce(key, ttl_sec=60) is False  # 首次
    assert ratelimit.seen_nonce(key, ttl_sec=60) is True   # 重放


def test_rate_limit_fixed_window():
    key = "ak_test:rl"
    limit = 3
    # 前 limit 次放行，第 limit+1 次开始拒绝
    results = [ratelimit.hit_rate_limit(key, limit, window_sec=60) for _ in range(5)]
    assert results == [False, False, False, True, True]


def test_rate_limit_zero_means_unlimited():
    key = "ak_test:unlimited"
    assert all(
        ratelimit.hit_rate_limit(key, 0, window_sec=60) is False for _ in range(50)
    )
