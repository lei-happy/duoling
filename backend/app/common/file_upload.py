"""
共享文件上传路由工厂
console 和 client 的文件上传逻辑完全一致，统一在此定义
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.core.dependencies import get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.local_image_upload import save_scene_image


def create_file_upload_router() -> APIRouter:
    """创建文件上传路由"""
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

    return router
