"""
文件上传接口
按场景目录管理上传文件（用户头像、运单照片等）
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form
from starlette.requests import Request

from app.core.dependencies import get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.exceptions import BizException

router = APIRouter()

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

UPLOAD_ROOT = Path(__file__).resolve().parents[4] / "uploads"

ALLOWED_SCENES = {"avatar", "waybill", "vehicle", "document"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    scene: str = Form(default="avatar"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    上传文件到指定场景目录
    - scene: 场景标识，决定存储子目录（avatar/waybill/vehicle/document）
    - 返回文件的相对访问路径
    """
    if scene not in ALLOWED_SCENES:
        raise BizException(f"不支持的上传场景: {scene}")

    original_name = file.filename or "unknown"
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise BizException(f"不支持的文件类型: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise BizException("文件大小不能超过5MB")

    scene_dir = UPLOAD_ROOT / scene
    scene_dir.mkdir(parents=True, exist_ok=True)

    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = scene_dir / new_filename
    file_path.write_bytes(content)

    relative_url = f"/uploads/{scene}/{new_filename}"

    return success(data={
        "url": relative_url,
        "name": original_name,
    })
