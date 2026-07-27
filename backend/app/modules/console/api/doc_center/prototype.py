"""
产品原型目录接口

约定：仓库根目录下的 ``prototype/`` 为唯一原型根（部署可用 PROTO_ROOT 覆盖）。
仅扫描该目录内的多级结构与 HTML 文件；目录内每个 .html/.htm 即一条可预览原型。
推荐结构示例：
  prototype/
    运营端/
      系统管理/
        菜单管理.html
    企业端/
      运单/
        运单列表.html
"""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse

from app.common.response import fail, success
from app.core.dependencies import get_current_user
from app.core.security import TokenData, decode_access_token

router = APIRouter()

# 原型根目录：优先 PROTO_ROOT，否则仓库根下 prototype/
_PROTO_ROOT = (
    Path(os.environ.get("PROTO_ROOT", "")).resolve()
    if os.environ.get("PROTO_ROOT")
    else Path(__file__).resolve().parents[6] / "prototype"
)

_HTML_EXTS = {".html", ".htm"}
# iframe 内相对资源需要一并放行
_ASSET_EXTS = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".mjs",
    ".map",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".bmp",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".mp4",
    ".webm",
    ".txt",
}

_PROTO_FILE_PREFIX = "/api/console/doc-center/prototypes/file"
_PROTO_COOKIE = "zt_proto_token"


def get_proto_root() -> Path:
    return _PROTO_ROOT


def _build_tree(dir_path: Path, rel_prefix: str = "") -> List[dict]:
    """递归构建目录树，仅保留 html 文件和包含 html 的目录"""
    nodes: List[dict] = []
    if not dir_path.is_dir():
        return nodes

    entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for entry in entries:
        if entry.name.startswith("."):
            continue
        rel_path = f"{rel_prefix}/{entry.name}" if rel_prefix else entry.name
        if entry.is_dir():
            children = _build_tree(entry, rel_path)
            if children:
                nodes.append(
                    {
                        "title": entry.name,
                        "key": rel_path,
                        "isLeaf": False,
                        "children": children,
                    }
                )
        elif entry.is_file() and entry.suffix.lower() in _HTML_EXTS:
            nodes.append(
                {
                    "title": entry.stem,
                    "key": rel_path.replace("\\", "/"),
                    "isLeaf": True,
                }
            )
    return nodes


def _safe_resolve(rel_path: str) -> Optional[Path]:
    if not rel_path or ".." in rel_path.replace("\\", "/").split("/"):
        return None
    try:
        target = (_PROTO_ROOT / rel_path).resolve()
    except (ValueError, OSError):
        return None
    root = _PROTO_ROOT.resolve()
    if not str(target).startswith(str(root)):
        return None
    return target


def _auth_from_request(request: Request) -> Optional[TokenData]:
    """Header / Cookie / Query 解析登录态（供 iframe 相对资源请求）"""
    user = getattr(request.state, "current_user", None)
    if user:
        return user

    token: Optional[str] = None
    cookie_token = request.cookies.get(_PROTO_COOKIE)
    if cookie_token:
        token = cookie_token
    if not token:
        qs = parse_qs(request.url.query or "")
        vals = qs.get("access_token") or qs.get("token")
        if vals:
            token = vals[0]
    if not token:
        return None
    return decode_access_token(token)


@router.get("/tree")
async def get_prototype_tree(
    _: TokenData = Depends(get_current_user),
):
    """获取 HTML 原型目录树"""
    if not _PROTO_ROOT.is_dir():
        return fail("原型目录不存在，请联系管理员在仓库中创建 prototype/ 目录")
    return success(data=_build_tree(_PROTO_ROOT.resolve()))


@router.get("/file/{file_path:path}")
async def serve_prototype_file(
    file_path: str,
    request: Request,
):
    """
    提供原型文件（HTML 及 css/js/图片等相对资源）。
    iframe 无法带 Authorization，故支持 Cookie zt_proto_token / query access_token。
    """
    user = _auth_from_request(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")

    rel = (file_path or "").replace("\\", "/").lstrip("/")
    target = _safe_resolve(rel)
    if target is None:
        raise HTTPException(status_code=400, detail="非法路径")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")

    ext = target.suffix.lower()
    if ext not in _ASSET_EXTS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    media_type, _ = mimetypes.guess_type(str(target))
    if ext in _HTML_EXTS:
        media_type = "text/html; charset=utf-8"
    elif ext == ".js" or ext == ".mjs":
        media_type = "application/javascript; charset=utf-8"
    elif ext == ".css":
        media_type = "text/css; charset=utf-8"

    return FileResponse(
        path=str(target),
        media_type=media_type or "application/octet-stream",
    )


@router.get("/resolve")
async def resolve_prototype_path(
    path: str = Query(..., description="原型 HTML 相对路径"),
    _: TokenData = Depends(get_current_user),
):
    """校验原型路径是否存在（保存前可选校验）"""
    if not path or Path(path).suffix.lower() not in _HTML_EXTS:
        return fail("请选择 HTML 原型文件")
    target = _safe_resolve(path.replace("\\", "/"))
    if target is None or not target.is_file():
        return fail("未找到该原型文件，请重新选择")
    return success(data={"path": path.replace("\\", "/"), "name": target.stem})
