"""
管理后台文件上传（复用共享文件上传路由）
"""

from app.common.file_upload import create_file_upload_router

router = create_file_upload_router()
