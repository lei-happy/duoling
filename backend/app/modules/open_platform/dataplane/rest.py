"""REST 数据面（/openapi/v1）

外部系统用 AppKey/Secret 做 HMAC 签名调用。统一响应包络：
  成功 {"code":0,"data":...,"requestId":...}
  失败 {"code":<http>,"error":<code>,"message":...,"requestId":...}
"""

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.modules.open_platform.capabilities.registry import list_capabilities
from app.modules.open_platform.dataplane import errors
from app.modules.open_platform.dataplane.authn import authenticate_api
from app.modules.open_platform.dataplane.runner import run_and_audit

router = APIRouter()


def _ok(data, request_id: str) -> JSONResponse:
    return JSONResponse({"code": 0, "data": data, "requestId": request_id})


def _err(e: errors.OpenApiError, request_id: str = "") -> JSONResponse:
    return JSONResponse(
        status_code=e.http_status,
        content={
            "code": e.http_status,
            "error": e.error_code,
            "message": e.message,
            "requestId": request_id,
        },
    )


@router.get("/_meta/capabilities")
async def meta_capabilities(request: Request):
    """返回当前凭证被授权、且支持 api 通道的能力清单。"""
    try:
        cred, ctx = await authenticate_api(request, await request.body())
    except errors.OpenApiError as e:
        return _err(e)
    allowed = set(ctx.scope or [])
    data = [
        {
            "code": s.code,
            "name": s.name,
            "category": s.category,
            "description": s.description,
            "version": s.version,
            "input_schema": s.input_schema,
        }
        for s in list_capabilities("api")
        if s.code in allowed
    ]
    return _ok(data, ctx.request_id)


@router.post("/{capability_code}")
async def invoke(capability_code: str, request: Request):
    """执行一项能力。请求体 JSON 即入参。"""
    body = await request.body()
    try:
        cred, ctx = await authenticate_api(request, body)
    except errors.OpenApiError as e:
        return _err(e)

    try:
        params = json.loads(body.decode("utf-8")) if body else {}
        if not isinstance(params, dict):
            raise errors.bad_request("请求体必须为 JSON 对象")
    except errors.OpenApiError as e:
        return _err(e, ctx.request_id)
    except Exception:
        return _err(errors.bad_request("请求体不是合法 JSON"), ctx.request_id)

    try:
        result = await run_and_audit(
            ctx, capability_code, params, method="POST", path=request.url.path
        )
    except errors.OpenApiError as e:
        return _err(e, ctx.request_id)
    return _ok(result, ctx.request_id)
