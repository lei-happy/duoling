"""
AI 附件上传

接受 Excel/CSV 等文件，落到 uploads/ai_attach/{uuid}{ext}，
返回 file_id 供 file.parse_excel 等工具使用。
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from app.common.exceptions import BizException
from app.common.response import success
from app.core.dependencies import get_current_user
from app.core.security import TokenData

router = APIRouter()

ALLOWED_AI_ATTACH_EXTS = {".xlsx", ".xls", ".csv", ".pdf", ".png", ".jpg", ".jpeg"}
MAX_AI_ATTACH_SIZE = 20 * 1024 * 1024  # 20MB

# backend/app/modules/ai/api/client/file.py -> parents[5] = backend
AI_UPLOAD_ROOT = Path(__file__).resolve().parents[5] / "uploads" / "ai_attach"


@router.post("/upload")
async def upload_ai_attach(
    file: UploadFile = File(...),
    _: TokenData = Depends(get_current_user),
):
    content = await file.read()
    if len(content) > MAX_AI_ATTACH_SIZE:
        raise BizException("附件大小不能超过 20MB")

    original_name = file.filename or "unknown"
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_AI_ATTACH_EXTS:
        raise BizException(
            f"暂不支持的附件类型 {ext}（允许 {', '.join(sorted(ALLOWED_AI_ATTACH_EXTS))}）"
        )

    AI_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    file_id = f"{uuid.uuid4().hex}{ext}"
    (AI_UPLOAD_ROOT / file_id).write_bytes(content)

    return success(
        data={
            "fileId": file_id,
            "name": original_name,
            "size": len(content),
            "mime": file.content_type,
        }
    )
