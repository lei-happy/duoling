"""
文档中心接口
提供项目文档目录树浏览和 Markdown 文件内容读取
"""

import os
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.dependencies import get_current_user
from app.core.security import TokenData
from app.common.response import success, fail

router = APIRouter()

# 文档根目录：优先从环境变量 DOC_ROOT 读取（Docker 部署时使用），
# 否则按本地开发目录结构自动推导
_DOC_ROOT = Path(os.environ.get("DOC_ROOT", "")).resolve() \
    if os.environ.get("DOC_ROOT") \
    else Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent / "项目文档"

_ALLOWED_EXTENSIONS = {".md"}


def _build_tree(dir_path: Path, rel_prefix: str = "") -> List[dict]:
    """递归构建目录树，仅保留 md 文件和包含 md 文件的目录"""
    nodes: List[dict] = []

    if not dir_path.is_dir():
        return nodes

    entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name))

    for entry in entries:
        rel_path = f"{rel_prefix}/{entry.name}" if rel_prefix else entry.name

        if entry.is_dir():
            children = _build_tree(entry, rel_path)
            if children:
                nodes.append({
                    "title": entry.name,
                    "key": rel_path,
                    "isLeaf": False,
                    "children": children,
                })
        elif entry.is_file() and entry.suffix.lower() in _ALLOWED_EXTENSIONS:
            nodes.append({
                "title": entry.stem,
                "key": rel_path,
                "isLeaf": True,
            })

    return nodes


def _safe_resolve(rel_path: str) -> Optional[Path]:
    """校验相对路径安全性，防止路径穿越"""
    try:
        target = (_DOC_ROOT / rel_path).resolve()
    except (ValueError, OSError):
        return None

    if not str(target).startswith(str(_DOC_ROOT.resolve())):
        return None

    return target


@router.get("/tree")
async def get_doc_tree(
    current_user: TokenData = Depends(get_current_user),
):
    """获取文档目录树"""
    if not _DOC_ROOT.is_dir():
        return fail("文档目录不存在，请联系管理员")

    tree = _build_tree(_DOC_ROOT.resolve())
    return success(data=tree)


@router.get("/content")
async def get_doc_content(
    path: str = Query(..., description="文档相对路径"),
    current_user: TokenData = Depends(get_current_user),
):
    """获取文档内容"""
    if not path or not path.lower().endswith(".md"):
        return fail("仅支持查看 Markdown 文件")

    target = _safe_resolve(path)
    if target is None:
        raise HTTPException(status_code=400, detail="非法路径")

    if not target.is_file():
        return fail("文件不存在")

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = target.read_text(encoding="gbk")

    return success(data={"path": path, "content": content})
