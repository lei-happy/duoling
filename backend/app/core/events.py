"""
应用生命周期事件
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.database import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭事件"""
    # ---- 启动 ----
    logger.info("正在启动智途(ZhiTu)后端服务...")
    await db_manager.init_platform_db()

    # 启动后做一次轻量自检：菜单 feature_code 与产品功能清单是否一致
    try:
        await _warn_on_stale_feature_codes()
    except Exception as e:
        logger.warning(f"启动自检失败（不影响服务启动）：{e!r}")

    # AI 数字员工：1) 平台库 ai_* 表自动建；2) 反射 @register_tool 同步到 ai_tool
    try:
        await _bootstrap_ai_module()
    except Exception as e:
        logger.warning(f"AI 数字员工模块启动初始化失败（不影响其他服务）：{e!r}")

    # 计费引擎 worker：扫 biz_freight_calc_task 异步执行
    try:
        from app.modules.client.workers.freight_calc_worker import setup_worker_with_settings
        setup_worker_with_settings()
    except Exception as e:
        logger.warning(f"运费计算 Worker 启动失败（不影响其他服务）：{e!r}")

    logger.info("智途(ZhiTu)后端服务启动完成")

    yield

    # ---- 关闭 ----
    logger.info("正在关闭智途(ZhiTu)后端服务...")
    try:
        from app.modules.client.workers.freight_calc_worker import shutdown_worker
        shutdown_worker()
    except Exception as e:
        logger.warning(f"运费计算 Worker 关闭异常: {e!r}")
    await db_manager.close_all()
    logger.info("智途(ZhiTu)后端服务已关闭")


async def _warn_on_stale_feature_codes() -> None:
    """
    扫描 sys_menu.feature_code 是否全部在 sys_product_feature 中存在。
    若发现脏 feature_code，使用 logger.warn 打印清单，提示运维使用
    backend/scripts/fix/fix_stale_feature_codes.py 修复。
    """
    from app.modules.console.services.product.product_feature_service import (
        ProductFeatureService,
    )

    factory = db_manager._platform_session_factory  # noqa: SLF001
    if factory is None:
        return

    async with factory() as session:
        result = await ProductFeatureService.health_check(session)

    orphan = result.get("orphanFeatureCodes") or []
    unbound = result.get("unboundFeatureCodes") or []
    if orphan:
        logger.warning(
            f"[菜单一致性] sys_menu 中引用了 {len(orphan)} 个脏 feature_code（未在产品功能清单中定义），"
            f"客户端会因此过滤掉这些菜单。请运行: "
            f"python backend/scripts/fix/fix_stale_feature_codes.py。清单：{orphan}"
        )
    if unbound:
        logger.info(
            f"[菜单一致性] 共 {len(unbound)} 个功能未绑定到任何启用版本，"
            f"客户端任何租户都无法看到对应菜单：{unbound}"
        )
    if not orphan and not unbound:
        logger.info("[菜单一致性] 自检通过：feature_code 与产品功能清单完全对齐")


async def _bootstrap_ai_module() -> None:
    """AI 数字员工模块启动初始化

    1) 自动创建平台库 ai_* 元数据表（不存在则建）
    2) 加载所有 @register_tool 装饰的工具，upsert 到 ai_tool 表
    """
    from sqlalchemy import inspect as sa_inspect

    from app.core.database import PlatformBase
    from app.modules.ai.tools import import_all_tools
    from app.modules.ai.tools.registry import get_registry

    # 1) 自动建平台库 ai_* 表（依赖 console.models.__init__ 已经 import 过）
    engine = db_manager.platform_engine
    ai_tables = [
        t for t in PlatformBase.metadata.sorted_tables if t.name.startswith("ai_")
    ]
    if ai_tables:
        async with engine.connect() as conn:
            existing = await conn.run_sync(
                lambda sync_conn: sa_inspect(sync_conn).get_table_names()
            )
        missing = [t for t in ai_tables if t.name not in existing]
        if missing:
            async with engine.begin() as conn:
                await conn.run_sync(
                    lambda sync_conn: PlatformBase.metadata.create_all(
                        sync_conn, tables=missing
                    )
                )
            logger.info(
                f"[AI] 平台库 ai_* 表已自动创建: {[t.name for t in missing]}"
            )

    # 2) 反射 @register_tool 同步到 ai_tool
    import_all_tools()
    factory = db_manager._platform_session_factory  # noqa: SLF001
    if factory is None:
        return
    async with factory() as session:
        result = await get_registry().sync_to_db(session)
    logger.info(
        f"[AI] 工具注册表同步完成: 新增 {result['inserted']}, "
        f"更新 {result['updated']}, 孤立 {result['orphan']}"
    )
