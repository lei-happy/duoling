"""
同步审批中心默认流程模板到所有已激活租户（幂等 upsert）

设计要点：
- 默认模板以 **草稿** 形态下发（status=0）：引擎的 match_flow 只命中"已发布"模板，
  因此在运营到「审批流程配置」补齐审批人并发布之前，社会运力等场景仍走旧单级直审，
  实现平滑灰度（见《08.审批中心/05.实施方案与部署落地》）。
- 幂等键：flow_code（租户内唯一）。已存在则跳过，避免覆盖运营已编辑/已发布的配置。
- 仅对已建出 biz_approval_flow 表（即开通 approval_manage 的租户）执行。

用法：
    python scripts/seed/seed_approval_flows.py
    python scripts/seed/seed_approval_flows.py 1001 1010   # 仅指定租户编码
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings


# ============================================================
# 默认流程模板定义（唯一真实来源）
# 每个模板：flow_code, biz_type, flow_name, is_default, nodes[]
# node: node_order, node_type, node_name, approver_type, approver_config(JSON 文本/None),
#       sign_type, empty_strategy
# ============================================================
FLOW_DEFS = [
    {
        "flow_code": "social_capacity_audit_default",
        "biz_type": "social_capacity_audit",
        "flow_name": "社会运力准入审核（默认）",
        "is_default": 1,
        "remark": "系统下发的默认单级模板，请补齐审批人后发布以启用审批中心流转",
        "nodes": [
            {
                "node_order": 1,
                "node_type": 1,        # 审批节点
                "node_name": "运力准入审核",
                "approver_type": 2,    # 指定角色（运营发布前需在配置页补齐 role_ids）
                "approver_config": None,
                "sign_type": 1,        # 或签
                "empty_strategy": 3,   # 审批人为空则报错阻断（强制运营先配置）
            },
        ],
    },
]


def _table_exists(session: Session, table_name: str) -> bool:
    row = session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :t LIMIT 1"
        ),
        {"t": table_name},
    ).first()
    return row is not None


def upsert_flows_for_tenant(tenant_code: str, engine) -> int:
    """向指定租户库 upsert 默认审批模板，返回新增模板数量。"""
    created = 0
    with Session(engine) as session:
        if not _table_exists(session, "biz_approval_flow"):
            return 0  # 该租户未开通审批中心

        for flow in FLOW_DEFS:
            existing = session.execute(
                text(
                    "SELECT id FROM biz_approval_flow "
                    "WHERE flow_code = :code AND is_deleted = 0"
                ),
                {"code": flow["flow_code"]},
            ).scalar_one_or_none()
            if existing is not None:
                continue

            session.execute(
                text(
                    "INSERT INTO biz_approval_flow "
                    "(biz_type, flow_name, flow_code, priority, is_default, "
                    " allow_withdraw, withdraw_scope, status, version, remark, is_deleted) "
                    "VALUES (:biz_type, :name, :code, 100, :is_default, "
                    " 1, 1, 0, 1, :remark, 0)"
                ),
                {
                    "biz_type": flow["biz_type"],
                    "name": flow["flow_name"],
                    "code": flow["flow_code"],
                    "is_default": flow["is_default"],
                    "remark": flow["remark"],
                },
            )
            flow_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            for n in flow["nodes"]:
                session.execute(
                    text(
                        "INSERT INTO biz_approval_flow_node "
                        "(flow_id, node_order, node_type, node_name, approver_type, "
                        " approver_config, sign_type, empty_strategy, "
                        " allow_transfer, allow_addsign, is_deleted) "
                        "VALUES (:fid, :order, :ntype, :nname, :atype, "
                        " :aconfig, :stype, :empty, 1, 1, 0)"
                    ),
                    {
                        "fid": flow_id,
                        "order": n["node_order"],
                        "ntype": n["node_type"],
                        "nname": n["node_name"],
                        "atype": n["approver_type"],
                        "aconfig": n["approver_config"],
                        "stype": n["sign_type"],
                        "empty": n["empty_strategy"],
                    },
                )
            created += 1

        session.commit()
    return created


def main():
    settings = get_settings()

    if len(sys.argv) > 1:
        tenant_codes = [c.strip() for c in sys.argv[1:] if c.strip()]
        print(f"[INFO] 使用命令行指定租户: {tenant_codes}")
    else:
        platform_engine = create_engine(settings.platform_db_url_sync)
        with Session(platform_engine) as session:
            rows = session.execute(
                text(
                    "SELECT tenant_code FROM sys_tenant "
                    "WHERE is_deleted = 0 AND status = 1 AND db_initialized = 1"
                )
            ).fetchall()
        tenant_codes = [r[0] for r in rows]
        platform_engine.dispose()

    if not tenant_codes:
        print("[INFO] 无租户可同步，跳过（可传租户编码：python scripts/seed/seed_approval_flows.py 1001）")
        return

    print(f"[INFO] 将同步 {len(tenant_codes)} 个租户库的默认审批模板")

    for code in tenant_codes:
        tenant_engine = create_engine(settings.tenant_db_url_sync(code))
        try:
            created = upsert_flows_for_tenant(code, tenant_engine)
            if created:
                print(f"  [{code}] 新增 {created} 个默认审批模板（草稿）")
            else:
                print(f"  [{code}] 默认模板已存在或未开通审批中心，跳过")
        except Exception as e:
            print(f"  [{code}] 失败: {e}")
        finally:
            tenant_engine.dispose()

    print("[OK] 审批中心默认模板同步完成（草稿态，需运营补齐审批人并发布后生效）")


if __name__ == "__main__":
    main()
