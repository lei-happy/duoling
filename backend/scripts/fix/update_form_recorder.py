"""
更新已存在的录单员小智（form_recorder_default）

背景：seed_ai_employees.py 幂等，已存在的员工不会被覆盖。本脚本用于把
「图片识别 + 追问澄清」能力落地后新的 system_prompt / model_config / 工具绑定
同步到已存在的录单员记录（不新建，不影响其它员工）。

同步内容：
- system_prompt / description / welcome_message / suggested_questions
- model_config_json（含 vision_provider_code / vision_model）
- 补齐工具绑定（新增 image.extract_waybill 等；不删除已有绑定）

用法：
    python scripts/fix/update_form_recorder.py

注意：请先启动一次后端，让 @register_tool 反射把 image.extract_waybill 同步到 ai_tool 表，
再执行本脚本，否则新工具在 ai_tool 中查不到、无法绑定。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import get_settings  # noqa: E402

import app.modules.console.models  # noqa: E402,F401
from app.modules.ai.models.platform.ai_employee import AiEmployee  # noqa: E402
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool  # noqa: E402
from app.modules.ai.models.platform.ai_tool import AiTool  # noqa: E402

from scripts.seed.seed_ai_employees import (  # noqa: E402
    FORM_RECORDER_MODEL_CONFIG,
    FORM_RECORDER_SYSTEM_PROMPT,
    FORM_RECORDER_TOOLS,
)

EMPLOYEE_CODE = "form_recorder_default"


def update_form_recorder() -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync, echo=False)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        emp = session.execute(
            select(AiEmployee).where(
                AiEmployee.code == EMPLOYEE_CODE, AiEmployee.is_deleted == 0
            )
        ).scalar_one_or_none()
        if not emp:
            print(f"[SKIP] 未找到员工 {EMPLOYEE_CODE}，请先运行 seed_ai_employees.py")
            return

        emp.system_prompt = FORM_RECORDER_SYSTEM_PROMPT
        emp.description = "把 Excel/CSV 表格与运单图片解析后自动录入为运单，遇缺失信息主动追问。"
        emp.welcome_message = (
            "你好，我是录单员小智。你可以直接拖入 Excel/CSV，或上传运单截图/照片，"
            "我会帮你提取关键信息并入库；信息不全时我会主动跟你确认。"
        )
        emp.suggested_questions = [
            "帮我录入这份运单表格",
            "识别一下这张运单图片",
            "把这份 Excel 解析一下让我看看表头",
            "刚才录单失败的几条原因是什么",
        ]
        # 合并 model_config：保留已有键，覆盖/补充录单员相关键
        merged = dict(emp.model_config_json or {})
        merged.update(FORM_RECORDER_MODEL_CONFIG)
        emp.model_config_json = merged
        session.flush()

        # 补齐工具绑定
        existing = session.execute(
            select(AiEmployeeTool, AiTool)
            .join(AiTool, AiTool.id == AiEmployeeTool.tool_id)
            .where(
                AiEmployeeTool.employee_id == emp.id,
                AiEmployeeTool.is_deleted == 0,
            )
        ).all()
        bound_codes = {row[1].code for row in existing}

        added = 0
        for idx, code in enumerate(FORM_RECORDER_TOOLS):
            if code in bound_codes:
                continue
            tool = session.execute(
                select(AiTool).where(AiTool.code == code, AiTool.is_deleted == 0)
            ).scalar_one_or_none()
            if not tool:
                print(f"[WARN] 工具 {code} 在 ai_tool 中不存在，跳过（请先启动后端同步）")
                continue
            session.add(
                AiEmployeeTool(
                    employee_id=emp.id,
                    tool_id=tool.id,
                    sort_order=len(bound_codes) + idx,
                    enabled=1,
                )
            )
            added += 1
            print(f"[OK] 绑定工具 {code}")

        session.commit()
        print(f"\n完成：录单员 {EMPLOYEE_CODE} 已更新，新增工具绑定 {added} 个。")
        print("提示：请确认 model_config 中的 vision_provider_code / vision_model 指向你们已配置的视觉模型。")


if __name__ == "__main__":
    update_form_recorder()
