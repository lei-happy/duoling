"""
应用配置管理
通过 pydantic-settings 从环境变量 / .env 文件加载配置
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """全局配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---- 应用 ----
    APP_NAME: str = "ZhiTu"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_SECRET_KEY: str = "change-me"

    # ---- JWT ----
    JWT_SECRET_KEY: str = "change-me"
    JWT_REFRESH_SECRET_KEY: str = "change-me-refresh"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2小时
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # ---- 数据库环境后缀 ----
    # 开发环境设为 "_ci"，生产环境为空字符串
    DB_SUFFIX: str = ""

    # ---- 平台数据库 ----
    PLATFORM_DB_HOST: str = "127.0.0.1"
    PLATFORM_DB_PORT: int = 3306
    PLATFORM_DB_USER: str = "root"
    PLATFORM_DB_PASSWORD: str = ""
    PLATFORM_DB_NAME: str = "zt_platform"

    # ---- 租户数据库 ----
    TENANT_DB_HOST: str = "127.0.0.1"
    TENANT_DB_PORT: int = 3306
    TENANT_DB_USER: str = "root"
    TENANT_DB_PASSWORD: str = ""
    TENANT_DB_PREFIX: str = "zt_biz_"

    # ---- Redis ----
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # ---- 阿里云短信认证（DYPNS） ----
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = "速通互联验证码"
    ALIYUN_SMS_ENABLED: bool = True

    # ---- 跨域 ----
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # ---- 日志 ----
    LOG_LEVEL: str = "DEBUG"
    LOG_DIR: str = "logs"

    # ---- 数据库调试 ----
    DB_ECHO: bool = False

    @property
    def platform_database_name(self) -> str:
        """平台库实际数据库名（含环境后缀）"""
        return f"{self.PLATFORM_DB_NAME}{self.DB_SUFFIX}"

    def tenant_database_name(self, tenant_code: str) -> str:
        """租户库实际数据库名（含环境后缀）"""
        return f"{self.TENANT_DB_PREFIX}{tenant_code}{self.DB_SUFFIX}"

    @property
    def platform_db_url(self) -> str:
        """平台主库连接字符串（异步）"""
        return (
            f"mysql+aiomysql://{self.PLATFORM_DB_USER}:{self.PLATFORM_DB_PASSWORD}"
            f"@{self.PLATFORM_DB_HOST}:{self.PLATFORM_DB_PORT}/{self.platform_database_name}"
            f"?charset=utf8mb4"
        )

    @property
    def platform_db_url_sync(self) -> str:
        """平台主库连接字符串（同步，用于 Alembic 迁移等）"""
        return (
            f"mysql+pymysql://{self.PLATFORM_DB_USER}:{self.PLATFORM_DB_PASSWORD}"
            f"@{self.PLATFORM_DB_HOST}:{self.PLATFORM_DB_PORT}/{self.platform_database_name}"
            f"?charset=utf8mb4"
        )

    def tenant_db_url(self, tenant_code: str) -> str:
        """根据租户编码生成租户库连接字符串（异步）"""
        db_name = self.tenant_database_name(tenant_code)
        return (
            f"mysql+aiomysql://{self.TENANT_DB_USER}:{self.TENANT_DB_PASSWORD}"
            f"@{self.TENANT_DB_HOST}:{self.TENANT_DB_PORT}/{db_name}"
            f"?charset=utf8mb4"
        )

    def tenant_db_url_sync(self, tenant_code: str) -> str:
        """根据租户编码生成租户库连接字符串（同步）"""
        db_name = self.tenant_database_name(tenant_code)
        return (
            f"mysql+pymysql://{self.TENANT_DB_USER}:{self.TENANT_DB_PASSWORD}"
            f"@{self.TENANT_DB_HOST}:{self.TENANT_DB_PORT}/{db_name}"
            f"?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        """Redis 连接字符串"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
