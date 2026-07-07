"""
ContextManager: 会话上下文加载与裁剪

职责：
1) 加载历史消息（按 session_id 倒序拉最近 N 条，再正序排）
2) 把 DB 消息转成 ChatMessage 给 LLM
3) 简单滑动窗口裁剪（V1 不接 token 计数，按条数限制；后续接 tiktoken）
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.llm.base import ChatMessage, ToolCall
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.tools.registry import encode_tool_name

# 附件类型推断：扩展名 -> 逻辑类型（供 LLM 选择对应工具）
_EXCEL_EXTS = {".xlsx", ".xls"}
_CSV_EXTS = {".csv"}
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
_PDF_EXTS = {".pdf"}


def _infer_attach_type(name: str, mime: str) -> str:
    """按文件名后缀与 mime 推断附件逻辑类型"""
    lower = (name or "").lower()
    for ext in _EXCEL_EXTS:
        if lower.endswith(ext):
            return "excel"
    if any(lower.endswith(e) for e in _CSV_EXTS):
        return "csv"
    if any(lower.endswith(e) for e in _IMAGE_EXTS):
        return "image"
    if any(lower.endswith(e) for e in _PDF_EXTS):
        return "pdf"
    m = (mime or "").lower()
    if m.startswith("image/"):
        return "image"
    if "spreadsheet" in m or "excel" in m:
        return "excel"
    if "csv" in m:
        return "csv"
    if "pdf" in m:
        return "pdf"
    return "file"


def _build_attachments_note(attachments: list) -> str:
    """把用户附件渲染成结构化文本，注入到用户消息末尾，
    让模型知道有哪些文件、fileId 与类型，从而选择正确的工具。
    """
    lines: list[str] = []
    for att in attachments or []:
        if not isinstance(att, dict):
            continue
        file_id = att.get("fileId") or att.get("file_id") or ""
        if not file_id:
            continue
        name = att.get("name") or file_id
        mime = att.get("mime") or att.get("content_type") or ""
        atype = _infer_attach_type(name, mime)
        lines.append(f"[附件] name={name} | fileId={file_id} | type={atype}")
    if not lines:
        return ""
    tips = {
        "excel": "excel/csv 附件请调用 file.parse_excel(file_id=...) 解析后再做字段映射；",
        "csv": "excel/csv 附件请调用 file.parse_excel(file_id=...) 解析后再做字段映射；",
        "image": "image 附件请调用 image.extract_waybill(file_id=...) 识别运单信息；",
    }
    used = {t for t in ("excel", "csv", "image") if any(f"type={t}" in ln for ln in lines)}
    hint = "".join(tips[t] for t in ("excel", "csv", "image") if t in used)
    header = "用户本次上传了以下附件（" + (hint or "请按类型选择合适工具处理") + "）：\n"
    return header + "\n".join(lines)


class ContextManager:
    @staticmethod
    async def load_history_messages(
        tenant_db: AsyncSession,
        session_id: int,
        max_messages: int = 20,
        exclude_system: bool = True,
    ) -> list[ChatMessage]:
        """加载历史消息（按时间正序）"""
        stmt = (
            select(BizAiMessage)
            .where(
                BizAiMessage.session_id == session_id,
                BizAiMessage.is_deleted == 0,
            )
            .order_by(BizAiMessage.id.desc())
            .limit(max_messages)
        )
        rows = (await tenant_db.execute(stmt)).scalars().all()
        rows = list(reversed(rows))

        messages: list[ChatMessage] = []
        for row in rows:
            if exclude_system and row.role == "system":
                continue
            messages.append(ContextManager._row_to_message(row))
        return messages

    @staticmethod
    def _row_to_message(row: BizAiMessage) -> ChatMessage:
        tool_calls: list[ToolCall] = []
        if row.tool_calls:
            for tc in row.tool_calls:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function") or {}
                raw_name = tc.get("name") or fn.get("name") or ""
                # 历史数据可能保存的是带点号的业务 code；
                # 给 LLM 时统一编码成 wire 名（encode 是幂等的，已编码不会被二次处理）
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id") or "",
                        name=encode_tool_name(raw_name),
                        arguments=tc.get("arguments") or fn.get("arguments") or "{}",
                    )
                )
        content = row.content
        # 用户消息若带附件，把附件清单注入到文本末尾，让模型拿到 fileId 与类型
        if row.role == "user" and row.attachments:
            note = _build_attachments_note(row.attachments)
            if note:
                content = f"{content}\n\n{note}" if content else note
        return ChatMessage(
            role=row.role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=row.tool_call_id,
            # tool 消息的 name 同样编码，确保和 assistant.tool_calls 的 wire 名一致
            name=encode_tool_name(row.tool_name) if row.role == "tool" and row.tool_name else None,
        )
