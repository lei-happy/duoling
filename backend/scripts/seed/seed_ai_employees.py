"""
AI 数字员工初始化种子

预置：
1) 录单员小智（form_recorder）：默认绑定 file.parse_excel / file.map_columns /
   waybill.search / waybill.batch_create / customer.search
2) 数据分析员小数（data_analyst）：默认绑定 waybill.search / vehicle.search /
   customer.search

注：本脚本是幂等的，已存在的员工不会被覆盖。
Provider 配置请在 Console 端「AI 数字员工 → 模型 Provider」新增；
也可以直接在本脚本末尾用 INIT_PROVIDER 字典预置一条（建议在生产环境用 Console 创建以避免明文密钥写入仓库）。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import get_settings  # noqa: E402

# 预先 import 模型，注册到元数据
import app.modules.console.models  # noqa: E402,F401
from app.modules.ai.models.platform.ai_employee import AiEmployee  # noqa: E402
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool  # noqa: E402
from app.modules.ai.models.platform.ai_tool import AiTool  # noqa: E402


PRESET_EMPLOYEES = [
    {
        "code": "form_recorder_default",
        "name": "录单员小智",
        "employee_type": "form_recorder",
        "description": "把表格/Excel/CSV 转成结构化数据，自动录入对应业务模块。",
        "system_prompt": (
            "你是「录单员小智」，专门帮助用户把上传的表格类文件解析后录入到系统中。\n"
            "工作流程：\n"
            "1. 用户上传 Excel/CSV → 调用 file.parse_excel 解析表头与样本行；\n"
            "2. 根据表头与目标业务（默认是运单），给出列映射建议；\n"
            "3. 调用 file.map_columns 生成可入库的行；\n"
            "4. 调用 waybill.batch_create 批量入库（属高风险动作，会触发用户确认）。\n"
            "录单成功后用一句话总结结果（成功/失败条数、典型错误）。"
        ),
        "welcome_message": (
            "你好，我是录单员小智。你可以直接拖入 Excel/CSV，我会帮你完成字段映射并入库。"
        ),
        "suggested_questions": [
            "帮我录入这份运单表格",
            "把这份 Excel 解析一下让我看看表头",
            "刚才录单失败的几条原因是什么",
        ],
        "model_config": {
            "temperature": 0.2,
            "max_tool_loops": 10,
            "context_window": 30,
        },
        "feature_code": "ai_assistant",
        "tools": [
            "file.parse_excel",
            "file.map_columns",
            "waybill.search",
            "waybill.batch_create",
            "customer.search",
        ],
    },
    {
        "code": "data_analyst_default",
        "name": "数据分析员小数",
        "employee_type": "data_analyst",
        "description": "查询业务数据并给出分析摘要。",
        "system_prompt": (
            "你是「数据分析员小数」，擅长帮助用户检索业务数据并给出结构化的洞察。\n"
            "原则：\n"
            "1. 一切数据来自工具查询，不要凭空编造；\n"
            "2. 优先用关键字模糊查询；\n"
            "3. 给出结论前先列出关键数字与同环比；\n"
            "4. 表格化呈现，必要时建议用户进入对应业务页面继续操作。"
        ),
        "welcome_message": (
            "你好，我是数据分析员小数。可以问我「本月运单数量」「车辆使用率」等业务问题。"
        ),
        "suggested_questions": [
            "查一下本月新增的运单",
            "客户 XX 最近一周的运单数",
            "在用车辆有多少",
        ],
        "model_config": {
            "temperature": 0.3,
            "max_tool_loops": 8,
            "context_window": 20,
        },
        "feature_code": "ai_assistant",
        "tools": [
            "waybill.search",
            "vehicle.search",
            "customer.search",
        ],
    },
]


def seed_ai_employees() -> None:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync, echo=False)
    Session = sessionmaker(bind=engine)
    inserted, skipped = 0, 0
    with Session() as session:
        for spec in PRESET_EMPLOYEES:
            ex = session.execute(
                select(AiEmployee).where(
                    AiEmployee.code == spec["code"], AiEmployee.is_deleted == 0
                )
            ).scalar_one_or_none()
            if ex:
                print(f"[SKIP] 数字员工 {spec['code']} 已存在")
                skipped += 1
                continue
            row = AiEmployee(
                code=spec["code"],
                name=spec["name"],
                employee_type=spec["employee_type"],
                description=spec.get("description"),
                system_prompt=spec.get("system_prompt"),
                welcome_message=spec.get("welcome_message"),
                suggested_questions=spec.get("suggested_questions"),
                model_config_json=spec.get("model_config"),
                feature_code=spec.get("feature_code"),
                status=1,
            )
            session.add(row)
            session.flush()

            tool_codes = spec.get("tools") or []
            if tool_codes:
                tool_rows = session.execute(
                    select(AiTool).where(
                        AiTool.code.in_(tool_codes), AiTool.is_deleted == 0
                    )
                ).scalars().all()
                for idx, t in enumerate(tool_rows):
                    session.add(
                        AiEmployeeTool(
                            employee_id=row.id,
                            tool_id=t.id,
                            sort_order=idx,
                            enabled=1,
                        )
                    )
            session.commit()
            inserted += 1
            print(f"[OK] 数字员工 {spec['code']} 已创建（{len(spec.get('tools') or [])} 工具）")

    print(f"\n完成：新增 {inserted}，跳过 {skipped}。")
    print("提示：若工具尚未存在，请先启动一次后端，让 @register_tool 反射同步到 ai_tool 表，再执行本脚本。")


if __name__ == "__main__":
    seed_ai_employees()
