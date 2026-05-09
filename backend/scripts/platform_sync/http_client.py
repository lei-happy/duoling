"""
Console API HTTP 客户端

- 自动登录获取 JWT
- 401 时自动 refresh 一次后重试
- 网络错误指数退避重试 N 次
- 统一拆 {code, message, data} 响应外壳，code != 0 抛 ConsoleApiError
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from .config import SyncConfig


class ConsoleApiError(RuntimeError):
    """Console 业务错误（响应中 code != 0）"""

    def __init__(self, code: int, message: str, path: str = ""):
        super().__init__(f"[code={code}] {message} (path={path})")
        self.code = code
        self.message = message
        self.path = path


class ConsoleClient:
    """
    Console API 客户端

    用法：
        with ConsoleClient(cfg) as client:
            data = client.get("/system/client-menu/export")
    """

    def __init__(self, cfg: SyncConfig):
        self.cfg = cfg
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._http: Optional[httpx.Client] = None

    # ---- 资源生命周期 ----

    def __enter__(self) -> "ConsoleClient":
        self._http = httpx.Client(timeout=self.cfg.http_timeout)
        self._login()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._http is not None:
            self._http.close()
            self._http = None

    # ---- 内部：登录与刷新 ----

    def _login(self) -> None:
        assert self._http is not None
        body = {"phone": self.cfg.admin_phone, "password": self.cfg.admin_password}
        resp = self._http.post(self.cfg.login_url, json=body)
        try:
            payload = resp.json()
        except Exception as e:
            raise ConsoleApiError(
                resp.status_code,
                f"登录响应非 JSON: {resp.text[:200]}",
                self.cfg.login_url,
            ) from e

        if resp.status_code >= 400 or payload.get("code") != 0:
            raise ConsoleApiError(
                payload.get("code", resp.status_code),
                payload.get("message", "登录失败"),
                self.cfg.login_url,
            )

        data = payload.get("data") or {}
        # 多企业选择时后端会返回 {needSelectTenant: True, ...}，平台超管不会触发
        if data.get("needSelectTenant"):
            raise ConsoleApiError(
                -1,
                "登录账号属于多企业，请改用平台超管账号同步",
                self.cfg.login_url,
            )

        self._access_token = data.get("access_token")
        self._refresh_token = data.get("refresh_token")
        if not self._access_token:
            raise ConsoleApiError(-1, "登录响应缺少 access_token", self.cfg.login_url)

    def _do_refresh(self) -> bool:
        """尝试用 refresh_token 续签；成功返回 True"""
        if not self._refresh_token or self._http is None:
            return False
        body = {"refresh_token": self._refresh_token}
        try:
            resp = self._http.post(self.cfg.refresh_url, json=body)
            payload = resp.json()
        except Exception:
            return False
        if resp.status_code >= 400 or payload.get("code") != 0:
            return False
        data = payload.get("data") or {}
        token = data.get("access_token")
        if not token:
            return False
        self._access_token = token
        new_refresh = data.get("refresh_token")
        if new_refresh:
            self._refresh_token = new_refresh
        return True

    # ---- 公共：GET ----

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET /api/console{path} → 自动拆 data。失败抛 ConsoleApiError 或 httpx 异常"""
        url = self.cfg.api_url(path)
        return self._request("GET", url, params=params)

    # ---- 公共：POST（保留以备未来扩展，pull/verify 暂不写入）----

    def post(self, path: str, json_body: Optional[Dict[str, Any]] = None) -> Any:
        url = self.cfg.api_url(path)
        return self._request("POST", url, json_body=json_body)

    # ---- 内部：统一请求带重试 ----

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        assert self._http is not None
        last_err: Optional[Exception] = None
        retries = max(self.cfg.http_retries, 0)
        attempted_refresh = False

        for attempt in range(retries + 1):
            try:
                headers = {"Authorization": f"Bearer {self._access_token}"}
                resp = self._http.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=headers,
                )

                # 401: 尝试 refresh 一次再重试，不计入网络重试次数
                if resp.status_code == 401 and not attempted_refresh:
                    attempted_refresh = True
                    if self._do_refresh():
                        continue
                    # refresh 失败则尝试重新登录
                    self._login()
                    continue

                try:
                    payload = resp.json()
                except Exception as e:
                    raise ConsoleApiError(
                        resp.status_code,
                        f"响应非 JSON: {resp.text[:200]}",
                        url,
                    ) from e

                if resp.status_code >= 400 or payload.get("code") != 0:
                    raise ConsoleApiError(
                        payload.get("code", resp.status_code),
                        payload.get("message", "请求失败"),
                        url,
                    )
                return payload.get("data")

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_err = e
                if attempt >= retries:
                    break
                # 指数退避：0.5s, 1s, 2s ...
                time.sleep(0.5 * (2**attempt))
            except ConsoleApiError:
                # 业务错误不重试，直接抛
                raise

        raise RuntimeError(
            f"{method} {url} 经 {retries} 次重试仍失败: {last_err!r}"
        )
