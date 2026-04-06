"""
管理后台文件上传（与客户端共用落盘规则与场景）
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.core.dependencies import get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.local_image_upload import save_scene_image

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    scene: str = Form(default="avatar"),
    _: TokenData = Depends(get_current_user),
):
    content = await file.read()
    original_name = file.filename or "unknown"
    data = save_scene_image(content, scene, original_name)
    return success(data=data)
