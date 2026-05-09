"""
platform_sync 配置加载

读取 envs/.env.{env} 文件，返回 SyncConfig 数据类。该模块刻意不复用
backend.app.core.config.Settings，因为这里只关心 Console API 凭证而非
数据库与短信等服务端配置。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# python-dotenv 已在 backend/requirements.txt 中
from dotenv import dotenv_values


# 仓库布局：
#   d:\zhitu\backend\scripts\platform_sync\config.py  -> parents[3] = d:\zhitu
TOOL_DIR: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = TOOL_DIR.parents[2]
DEFAULT_SNAPSHOT_DIR: Path = TOOL_DIR / "snapshots"

SUPPORTED_ENVS = ("dev", "prod")


@dataclass(frozen=True)
class SyncConfig:
    """单环境同步配置"""

    env: str
    api_base: str
    admin_phone: str
    admin_password: str
    http_timeout: float
    http_retries: int
    snapshot_dir: Path

    @property
    def login_url(self) -> str:
        return f"{self.api_base.rstrip('/')}/api/console/auth/login"

    @property
    def refresh_url(self) -> str:
        return f"{self.api_base.rstrip('/')}/api/console/auth/refresh"

    def api_url(self, path: str) -> str:
        """拼接 /api/console 下的子路径"""
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.api_base.rstrip('/')}/api/console{path}"


class ConfigError(RuntimeError):
    """环境配置缺失/非法时抛出"""


def _resolve_env_file(env: str) -> Path:
    return TOOL_DIR / "envs" / f".env.{env}"


def _resolve_snapshot_dir(raw: Optional[str]) -> Path:
    if not raw:
        return DEFAULT_SNAPSHOT_DIR
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (REPO_ROOT / p).resolve()
    return p


def load_config(env: str) -> SyncConfig:
    """加载指定环境的配置；缺凭证或文件即抛 ConfigError"""
    if env not in SUPPORTED_ENVS:
        raise ConfigError(
            f"不支持的环境 --env={env}，可选: {', '.join(SUPPORTED_ENVS)}"
        )

    env_file = _resolve_env_file(env)
    if not env_file.is_file():
        raise ConfigError(
            f"未找到环境配置文件: {env_file}\n"
            f"请先复制 envs/.env.example 为 envs/.env.{env} 并填写"
        )

    # dotenv_values 不污染进程环境，便于在同一进程内切换多环境
    raw = {k: v for k, v in dotenv_values(env_file).items() if v is not None}
    # 显式环境变量优先级最高（便于 CI 通过 secret 注入）
    for key in (
        "CONSOLE_API_BASE",
        "CONSOLE_ADMIN_PHONE",
        "CONSOLE_ADMIN_PASSWORD",
        "CONSOLE_HTTP_TIMEOUT",
        "CONSOLE_HTTP_RETRIES",
        "SNAPSHOT_DIR",
    ):
        if os.environ.get(key):
            raw[key] = os.environ[key]

    api_base = (raw.get("CONSOLE_API_BASE") or "").strip()
    phone = (raw.get("CONSOLE_ADMIN_PHONE") or "").strip()
    password = raw.get("CONSOLE_ADMIN_PASSWORD") or ""
    if not api_base or not phone or not password:
        raise ConfigError(
            f"{env_file} 缺少必填项 CONSOLE_API_BASE / CONSOLE_ADMIN_PHONE / CONSOLE_ADMIN_PASSWORD"
        )

    timeout = float(raw.get("CONSOLE_HTTP_TIMEOUT") or 30)
    retries = int(raw.get("CONSOLE_HTTP_RETRIES") or 3)
    snapshot_dir = _resolve_snapshot_dir(raw.get("SNAPSHOT_DIR"))

    return SyncConfig(
        env=env,
        api_base=api_base,
        admin_phone=phone,
        admin_password=password,
        http_timeout=timeout,
        http_retries=retries,
        snapshot_dir=snapshot_dir,
    )
