"""
操作日志装饰器

通过 @operation_log 装饰器自动采集租户端用户操作信息，
异步双写到平台库 sys_operation_log 和租户库 biz_operation_log。
"""

import asyncio
import json
import time
from functools import wraps
from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request

from app.core.database import db_manager
from app.core.security import TokenData
from app.modules.console.models.common.operation_log import OperationLog
from app.modules.client.models.biz_operation_log import BizOperationLog


MAX_BODY_LENGTH = 2000


def _safe_json(obj: Any) -> str:
    """安全序列化，截断到最大长度"""
    try:
        text = json.dumps(obj, default=str, ensure_ascii=False)
    except Exception:
        text = str(obj)
    return text[:MAX_BODY_LENGTH] if len(text) > MAX_BODY_LENGTH else text


def _extract_request_body(kwargs: dict) -> Optional[str]:
    """从路由参数中提取请求参数并序列化

    优先提取 Pydantic body；若无 body 则提取路径参数。
    """
    for value in kwargs.values():
        if isinstance(value, BaseModel):
            return _safe_json(value.model_dump())

    skip_keys = {"request", "db", "current_user"}
    path_params = {
        k: v for k, v in kwargs.items()
        if k not in skip_keys
        and not isinstance(v, (Request, BaseModel))
        and not hasattr(v, "execute")
    }
    if path_params:
        return _safe_json(path_params)
    return None


def _get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


async def _write_operation_log(
    *,
    tenant_code: Optional[str],
    user_id: Optional[int],
    username: Optional[str],
    module: str,
    action: str,
    description: str,
    request_method: str,
    request_url: str,
    request_body: Optional[str],
    response_body: Optional[str],
    ip: Optional[str],
    elapsed_time: int,
    status: int,
) -> None:
    """异步双写操作日志到平台库和租户库"""
    log_fields = dict(
        user_id=user_id,
        username=username,
        module=module,
        action=action,
        description=description,
        request_method=request_method,
        request_url=request_url,
        request_body=request_body,
        response_body=response_body,
        ip=ip,
        elapsed_time=elapsed_time,
        status=status,
    )

    # 写入平台库
    try:
        if db_manager._platform_session_factory:
            async with db_manager._platform_session_factory() as session:
                record = OperationLog(tenant_code=tenant_code, **log_fields)
                session.add(record)
                await session.commit()
    except Exception as e:
        logger.error(f"操作日志写入平台库失败: {e}")

    # 写入租户库
    if tenant_code:
        try:
            db_manager._get_or_create_tenant_engine(tenant_code)
            factory = db_manager._tenant_session_factories.get(tenant_code)
            if factory:
                async with factory() as session:
                    record = BizOperationLog(**log_fields)
                    session.add(record)
                    await session.commit()
        except Exception as e:
            logger.error(f"操作日志写入租户库失败 | tenant={tenant_code}: {e}")


def operation_log(module: str, action: str, description: str = ""):
    """
    操作日志装饰器

    用法：
        @router.post("")
        @operation_log(module="车辆管理", action="新增", description="新增车辆")
        async def create_vehicle(request: Request, ...):
            ...

    被装饰的端点需要声明 request: Request 参数。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Optional[Request] = kwargs.get("request")
            if request is None:
                for v in kwargs.values():
                    if isinstance(v, Request):
                        request = v
                        break

            start = time.time()
            response_body: Optional[str] = None
            log_status = 1

            try:
                result = await func(*args, **kwargs)
                response_body = _safe_json(result)
                return result
            except Exception as exc:
                log_status = 0
                response_body = _safe_json({"error": str(exc)})
                raise
            finally:
                elapsed = round((time.time() - start) * 1000)

                current_user: Optional[TokenData] = None
                tenant_code: Optional[str] = None
                client_ip: Optional[str] = None
                req_method = ""
                req_url = ""

                if request is not None:
                    current_user = getattr(request.state, "current_user", None)
                    tenant_code = getattr(request.state, "tenant_code", None)
                    client_ip = _get_client_ip(request)
                    req_method = request.method
                    req_url = str(request.url.path)

                request_body = _extract_request_body(kwargs)

                asyncio.create_task(_write_operation_log(
                    tenant_code=tenant_code,
                    user_id=current_user.user_id if current_user else None,
                    username=current_user.phone if current_user else None,
                    module=module,
                    action=action,
                    description=description,
                    request_method=req_method,
                    request_url=req_url,
                    request_body=request_body,
                    response_body=response_body,
                    ip=client_ip,
                    elapsed_time=elapsed,
                    status=log_status,
                ))
        return wrapper
    return decorator
