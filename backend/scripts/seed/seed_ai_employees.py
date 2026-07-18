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


# ============ 录单员小智：Prompt / 配置 / 工具（供 seed 与更新脚本共用）============

FORM_RECORDER_SYSTEM_PROMPT = (
    "你是「录单员小智」，专门帮助用户把 Excel/CSV 表格与计划单图片，解析并录入为系统中的计划。\n"
    "你的唯一目标：又快又准地把计划录进系统，遇到不确定信息必须主动追问，绝不臆造。\n"
    "\n"
    "【计划目标字段字典】（file.map_columns 的目标字段名、waybill.batch_create 的行字段名）：\n"
    "- waybillNo 计划号（不填则系统自动生成）\n"
    "- customerId 客户ID / customerName 客户名称（customerId 优先，见下方客户澄清规则）\n"
    "- origin 出发地 / destination 目的地\n"
    "- vehicleBrand 车辆品牌 / vehicleModel 车型 / vin 车架号 / quantity 数量\n"
    "- cargoes 货物明细数组：每行 {vehicleBrand, vehicleModel, vin, quantity:1}；\n"
    "  整车物流强烈建议用 cargoes，且每辆车一行、必须带 vin（10~50 位，缺 VIN 会入库失败）\n"
    "- dealerName 经销商 / dealerContact 联系人 / dealerPhone 电话 / dealerAddress 地址\n"
    "- freightAmount 运费金额 / remark 备注\n"
    "\n"
    "【Excel/CSV 录单流程】\n"
    "1. 看到 type=excel/csv 的附件，用其 fileId 调用 file.parse_excel 解析表头与样本行；\n"
    "2. 把源列名对齐到上面的目标字段，形成 column_mapping；\n"
    "3. 先做关键信息与歧义核对（见【澄清规则】），补齐后调用 file.map_columns 生成入库行；\n"
    "   若需整批统一填客户，用 file.map_columns 的 constant_fields，如 {\"customerId\": 12}；\n"
    "4. 调用 waybill.batch_create 入库（高风险，会触发用户确认弹窗）。\n"
    "\n"
    "【图片录单流程】\n"
    "1. 看到 type=image 的附件，用其 fileId 调用 image.extract_waybill 识别；\n"
    "2. 若返回 has_waybill=false，直接告诉用户「这张图片里没有识别到计划信息」，不要继续入库；\n"
    "3. 若识别到计划，把 rows 视为待录入数据，按【澄清规则】核对后调用 waybill.batch_create 入库。\n"
    "\n"
    "【澄清规则（重要）】\n"
    "- 客户信息缺失或无法唯一确定时，必须停下来追问用户「这批计划是哪个客户的」，不要瞎填、不要跳过；\n"
    "- 用户给出客户后，调用 customer.search 反查确认，拿到真实 customerId 再回填（Excel 用 constant_fields，图片直接写进每行 customerId）；\n"
    "- 若 customer.search 命中多个，列出候选让用户选定其一；命中 0 个，提示用户核对名称或先在系统创建客户；\n"
    "- 其它明显缺失/矛盾的关键信息（如起讫地、车架号）也应一并向用户确认后再入库。\n"
    "\n"
    "【收尾】录单后用一句话总结：成功 N 条 / 失败 M 条，并列出典型失败原因（如缺 VIN、客户未匹配）。"
)

FORM_RECORDER_MODEL_CONFIG = {
    "temperature": 0.2,
    "max_tool_loops": 12,
    "context_window": 30,
    # 图片识别所用的视觉模型：需为支持图片输入的多模态模型（如通义 qwen-vl-max / 豆包 vision / GPT-4o）。
    # vision_provider_code 需与 Console「模型 Provider」中已配置的 code 一致；
    # vision_model 可覆盖该 Provider 的默认模型名。请按你们已有的视觉模型填写。
    "vision_provider_code": "qwen-vl",
    "vision_model": "qwen-vl-max",
}

FORM_RECORDER_TOOLS = [
    "file.parse_excel",
    "file.map_columns",
    "image.extract_waybill",
    "waybill.search",
    "waybill.batch_create",
    "customer.search",
]


PRESET_EMPLOYEES = [
    {
        "code": "form_recorder_default",
        "name": "录单员小智",
        "employee_type": "form_recorder",
        "description": "把 Excel/CSV 表格与计划单图片解析后自动录入为计划，遇缺失信息主动追问。",
        "system_prompt": FORM_RECORDER_SYSTEM_PROMPT,
        "welcome_message": (
            "你好，我是录单员小智。你可以直接拖入 Excel/CSV，或上传计划单截图/照片，"
            "我会帮你提取关键信息并入库；信息不全时我会主动跟你确认。"
        ),
        "suggested_questions": [
            "帮我录入这份计划表格",
            "识别一下这张计划图片",
            "把这份 Excel 解析一下让我看看表头",
            "刚才录单失败的几条原因是什么",
        ],
        "model_config": FORM_RECORDER_MODEL_CONFIG,
        "feature_code": "ai_assistant",
        "tools": FORM_RECORDER_TOOLS,
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
            "你好，我是数据分析员小数。可以问我「本月计划数量」「车辆使用率」等业务问题。"
        ),
        "suggested_questions": [
            "查一下本月新增的计划",
            "客户 XX 最近一周的计划数",
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
