"""
初始化平台主库
创建数据库并初始化所有表结构
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings
from app.core.database import PlatformBase

# 确保所有模型被导入以注册到 metadata
from app.modules.console.models import *  # noqa: F401, F403


def init_platform_database():
    """初始化平台数据库"""
    settings = get_settings()

    # 1. 创建数据库（连接到 MySQL 时不指定数据库名）
    root_url = (
        f"mysql+pymysql://{settings.PLATFORM_DB_USER}:{settings.PLATFORM_DB_PASSWORD}"
        f"@{settings.PLATFORM_DB_HOST}:{settings.PLATFORM_DB_PORT}"
        f"?charset=utf8mb4"
    )
    engine = create_engine(root_url)
    with engine.connect() as conn:
        db_name = settings.platform_database_name
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()
    engine.dispose()
    print(f"[OK] 数据库 {settings.platform_database_name} 已创建")

    # 2. 在目标库中创建表
    platform_engine = create_engine(settings.platform_db_url_sync)
    PlatformBase.metadata.create_all(platform_engine)
    platform_engine.dispose()
    print(f"[OK] 平台库表结构已初始化")


if __name__ == "__main__":
    init_platform_database()
    print("\n平台主库初始化完成！")
