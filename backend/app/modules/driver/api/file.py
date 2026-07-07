"""
驾驶员端文件上传（复用共享文件上传路由）

司机 H5 上传装卸车照片 / 回单图片，走 driver JWT 鉴权（``get_current_user``）。
scene 白名单见 ``app.common.local_image_upload.ALLOWED_SCENES``（如 task_loading /
task_receipt）。
"""

from app.common.file_upload import create_file_upload_router

router = create_file_upload_router()
