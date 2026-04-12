"""
本地磁盘图片上传（uploads/{scene}/），供 client / console 路由复用。
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from app.common.exceptions import BizException

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# backend/app/common/ -> parents[2] = backend 项目根（含 app/、uploads/）
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"

ALLOWED_SCENES = {
    "avatar",
    "waybill",
    "vehicle",
    "document",
    "brand_logo",
    "car_series",
    "driver_license",
}


def save_scene_image(content: bytes, scene: str, original_name: str) -> dict:
    """
    校验并写入 uploads/{scene}/，返回 { "url": "/uploads/...", "name": 原始文件名 }
    """
    if scene not in ALLOWED_SCENES:
        raise BizException(f"不支持的上传场景: {scene}")

    ext = os.path.splitext(original_name or "unknown")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise BizException(f"不支持的文件类型: {ext}")

    if len(content) > MAX_FILE_SIZE:
        raise BizException("文件大小不能超过5MB")

    scene_dir = UPLOAD_ROOT / scene
    scene_dir.mkdir(parents=True, exist_ok=True)

    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = scene_dir / new_filename
    file_path.write_bytes(content)

    relative_url = f"/uploads/{scene}/{new_filename}"
    return {"url": relative_url, "name": original_name or "unknown"}
