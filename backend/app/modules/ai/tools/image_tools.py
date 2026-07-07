"""
图片运单识别工具

录单员核心能力（图片流）：把用户上传的运单截图/照片交给视觉大模型，
判断是否包含运单信息并抽取为结构化行，供 waybill.batch_create 入库。

设计要点：
- 视觉能力隔离在本工具内部单次调用，主对话模型只需是能做 tool calling 的文本模型；
- 视觉 Provider 配置来自数字员工 model_config_json 的 vision_provider_code / vision_model，
  经 Orchestrator 透传到 ToolContext.extras["model_config"]。
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel, Field

from app.modules.ai.llm.base import ChatMessage
from app.modules.ai.llm.factory import LLMProviderFactory
from app.modules.ai.tools.base import ToolContext, ToolResult
from app.modules.ai.tools.file_tools import _resolve_safe_path
from app.modules.ai.tools.registry import register_tool

_IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
}

_VISION_SYSTEM_PROMPT = (
    "你是运单信息抽取助手。用户会给你一张图片，请判断图片中是否包含物流运单信息"
    "（如运单号、客户/委托方、起讫地、车辆品牌车型、VIN、数量、经销商、运费等）。\n"
    "严格只输出一个 JSON 对象，不要输出多余文字，不要用 markdown 代码块包裹。JSON 结构：\n"
    "{\n"
    '  "has_waybill": true/false,   // 图片是否包含运单信息\n'
    '  "confidence": 0.0~1.0,        // 判断置信度\n'
    '  "rows": [                     // 抽取到的运单行；无则为空数组\n'
    "    {\n"
    '      "waybillNo": "运单号(可空)",\n'
    '      "customerName": "客户/委托方名称(可空)",\n'
    '      "origin": "出发地(可空)",\n'
    '      "destination": "目的地(可空)",\n'
    '      "vehicleBrand": "车辆品牌(可空)",\n'
    '      "vehicleModel": "车型(可空)",\n'
    '      "vin": "车架号VIN(可空)",\n'
    '      "quantity": 数量(可空),\n'
    '      "dealerName": "经销商(可空)",\n'
    '      "dealerContact": "联系人(可空)",\n'
    '      "dealerPhone": "电话(可空)",\n'
    '      "dealerAddress": "地址(可空)",\n'
    '      "freightAmount": 运费金额(可空),\n'
    '      "remark": "备注(可空)"\n'
    "    }\n"
    "  ],\n"
    '  "notes": "无法确定或需要人工确认的说明(可空)"\n'
    "}\n"
    "抽取原则：只填你在图片中真实看到的内容，看不清或没有的字段留空(null)，禁止臆造；"
    "客户信息若图片中没有，请把 customerName 留空并在 notes 中提示需要用户确认客户。"
)


class ExtractWaybillParams(BaseModel):
    file_id: str = Field(..., description="AI 附件文件ID（图片，来自 /ai/file/upload 返回）")
    hint: Optional[str] = Field(
        None, description="可选提示，如用户已说明客户/单据类型等，辅助识别"
    )


def _image_to_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = _IMAGE_MIME.get(suffix)
    if not mime:
        raise ValueError(f"暂不支持的图片类型 {suffix}（支持 {', '.join(sorted(_IMAGE_MIME))}）")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _extract_json(text: str) -> Optional[dict]:
    """从模型输出中鲁棒地解析 JSON 对象（容错 markdown 代码块/前后缀文字）"""
    if not text:
        return None
    s = text.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s[:4].lower() == "json":
            s = s[4:]
    try:
        return json.loads(s.strip())
    except Exception:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(s[start : end + 1])
        except Exception:
            return None
    return None


async def _vision_complete(provider, data_url: str, hint: Optional[str]) -> str:
    """单次调用视觉模型（无 tools），收集流式文本返回"""
    user_parts: list[dict[str, Any]] = []
    text = "请识别这张图片中的运单信息并按要求输出 JSON。"
    if hint:
        text += f"\n补充提示：{hint}"
    user_parts.append({"type": "text", "text": text})
    user_parts.append({"type": "image_url", "image_url": {"url": data_url}})

    messages = [
        ChatMessage(role="system", content=_VISION_SYSTEM_PROMPT),
        ChatMessage(role="user", content=user_parts),
    ]
    buf: list[str] = []
    async for chunk in provider.chat_stream(
        messages=messages,
        tools=None,
        temperature=0.0,
    ):
        if chunk.type == "delta" and chunk.text:
            buf.append(chunk.text)
    return "".join(buf)


@register_tool(
    code="image.extract_waybill",
    name="识别图片运单信息",
    category="file",
    description=(
        "把用户上传的运单截图/照片交给视觉大模型，判断是否包含运单信息并抽取为结构化行。"
        "返回 has_waybill 与 rows；若识别到运单但缺少客户等关键信息，应结合 customer.search 追问用户后再入库。"
    ),
    params_schema=ExtractWaybillParams,
    risk_level="low",
)
async def extract_waybill_from_image(ctx: ToolContext, **kwargs) -> ToolResult:
    params = ExtractWaybillParams(**kwargs)
    try:
        path = _resolve_safe_path(params.file_id)
    except (ValueError, FileNotFoundError) as e:
        return ToolResult(success=False, error=str(e))

    try:
        data_url = _image_to_data_url(path)
    except ValueError as e:
        return ToolResult(success=False, error=str(e))

    model_config = (ctx.extras or {}).get("model_config") or {}
    vision_provider_code = model_config.get("vision_provider_code")
    vision_model = model_config.get("vision_model")
    if not vision_provider_code and not vision_model:
        return ToolResult(
            success=False,
            error=(
                "未配置视觉模型。请在 Console「AI 数字员工」中为录单员的 model_config "
                "补充 vision_provider_code / vision_model（需为支持图片输入的多模态模型）。"
            ),
        )

    try:
        provider = await LLMProviderFactory.get(
            ctx.platform_db,
            provider_code=vision_provider_code,
            model_override=vision_model,
        )
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, error=f"视觉 Provider 初始化失败: {e}")

    try:
        raw = await _vision_complete(provider, data_url, params.hint)
    except Exception as e:  # noqa: BLE001
        logger.exception(f"[image.extract_waybill] 视觉模型调用失败: {e!r}")
        return ToolResult(success=False, error=f"视觉模型调用失败: {type(e).__name__}: {e}")

    parsed = _extract_json(raw)
    if parsed is None:
        return ToolResult(
            success=False,
            error="视觉模型未返回可解析的 JSON",
            data={"raw": raw[:1000]},
        )

    has_waybill = bool(parsed.get("has_waybill"))
    rows = parsed.get("rows") or []
    if not isinstance(rows, list):
        rows = []
    notes = parsed.get("notes")

    if not has_waybill:
        return ToolResult(
            success=True,
            data={"has_waybill": False, "rows": [], "notes": notes},
            message="图片中未识别到运单信息",
        )

    return ToolResult(
        success=True,
        data={
            "has_waybill": True,
            "confidence": parsed.get("confidence"),
            "rows": rows,
            "row_count": len(rows),
            "notes": notes,
        },
        message=f"识别到疑似运单，抽取 {len(rows)} 行；请核对关键信息后入库",
    )
