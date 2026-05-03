"""
修复已有租户库：补建 AI 数字员工模块的 biz_ai_* 4 张表

背景：ai_assistant 在 enterprise 版本默认开通，但 required_tables 是 AI 模块
落地后才补充进 sys_product_feature 的；之前已开通 enterprise 的租户其租户库里
缺这 4 张表（biz_ai_session / biz_ai_message / biz_ai_tool_call_log /
biz_ai_context），首次访问 AI 接口就会 1146 报错。

用法：
    python scripts/fix/fix_ai_tenant_tables.py [tenant_code]

不传 tenant_code 则修复全部 db_initialized=1 的租户库。
"""

from __future__ import annotations

import sys
import os
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text, inspect as sa_inspect  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import TenantBase, DatabaseManager  # noqa: E402

# 触发 AI 租户模型注册到 TenantBase.metadata
import app.modules.ai.models  # noqa: E402,F401
# 触发其他租户模型注册（避免 metadata 不全）
from app.modules.client.models import *  # noqa: E402,F401,F403


AI_TENANT_TABLES = [
    "biz_ai_session",
    "biz_ai_message",
    "biz_ai_tool_call_log",
    "biz_ai_context",
]


def get_all_tenant_codes(settings) -> List[str]:
    url = (
        f"mysql+pymysql://{settings.TENANT_DB_USER}:{settings.TENANT_DB_PASSWORD}"
        f"@{settings.TENANT_DB_HOST}:{settings.TENANT_DB_PORT}"
        f"/{settings.platform_database_name}?charset=utf8mb4"
    )
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT tenant_code FROM sys_tenant "
                    "WHERE is_deleted = 0 AND db_initialized = 1"
                )
            )
            return [row[0] for row in result]
    finally:
        engine.dispose()


def fix_one(tenant_code: str, settings) -> None:
    db_name = settings.tenant_database_name(tenant_code)
    print(f"\n{'=' * 60}\n租户库: {db_name} (tenant_code={tenant_code})\n{'=' * 60}")
    tenant_url = settings.tenant_db_url_sync(tenant_code)
    engine = create_engine(tenant_url)
    try:
        existing = set(sa_inspect(engine).get_table_names())
        target_tables = DatabaseManager.get_tables_by_names(AI_TENANT_TABLES)
        if not target_tables:
            print("[ERR] AI 租户模型尚未注册到 metadata，请检查 import")
            return
        missing = [t for t in target_tables if t.name not in existing]
        if not missing:
            print(f"[SKIP] biz_ai_* 表已齐全：{[t.name for t in target_tables]}")
            return
        TenantBase.metadata.create_all(engine, tables=missing)
        print(f"[OK] 已补建：{[t.name for t in missing]}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    settings = get_settings()
    if len(sys.argv) > 1:
        codes = [sys.argv[1]]
    else:
        codes = get_all_tenant_codes(settings)
        if not codes:
            print("未找到已初始化的租户库")
            sys.exit(0)
        print(f"找到 {len(codes)} 个已初始化租户库: {codes}")

    fail = 0
    for code in codes:
        try:
            fix_one(code, settings)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"[FAIL] {code}: {e}")

    print(f"\n完成：共处理 {len(codes)} 个租户，失败 {fail} 个")
