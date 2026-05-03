"""
SSE 事件编码

事件类型约定：
- session     : 会话信息（session_no、session_id）
- message     : 用户消息已落库回执
- delta       : assistant 文本增量
- tool.call   : 工具调用开始（含 tool_call_id、name、arguments 摘要）
- tool.result : 工具执行结果（含 status、summary）
- confirm.required : 高风险动作待用户确认（含 confirm_token、tool_code、params）
- usage       : 用量回报（prompt/completion tokens）
- done        : 一轮对话完成（含 finish_reason、message_id）
- error       : 错误事件
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SSEEvent:
    event: str
    data: Any = field(default_factory=dict)

    def encode(self) -> str:
        if isinstance(self.data, (dict, list)):
            payload = json.dumps(self.data, ensure_ascii=False, default=str)
        else:
            payload = str(self.data)
        return f"event: {self.event}\ndata: {payload}\n\n"


def sse_pack(event: str, data: Any = None) -> str:
    return SSEEvent(event=event, data=data or {}).encode()
