"""
把存量「线性节点链」审批流程转换为「画布流程树（process_config JSON）」

背景：审批流程配置升级为钉钉式条件分支画布后，流程定义改为存于
`biz_approval_flow.process_config`（树/条件分支 JSON）。本脚本把历史上以
`biz_approval_flow_node`（线性 node_order）维护的流程，幂等地转换为等价的
**单链树**写入 process_config，使运营可在新画布中直接打开/编辑历史流程。

行为一致性保证：
- 引擎运行时若 process_config 为空仍回退走旧 flow_node（见 engine.start），
  因此本脚本只对 process_config IS NULL 且存在 flow_node 的流程做填充，不改运行语义。
- 节点级 condition（命中才执行）会被包装为「条件路由 + 默认空分支」以保留跳过语义。
- 在途实例已冻结自己的快照，完全不受影响。

用法：
    python scripts/seed/migrate_approval_flows_to_tree.py
    python scripts/seed/migrate_approval_flows_to_tree.py 1001 1010   # 仅指定租户
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings


def _table_exists(session: Session, table_name: str) -> bool:
    row = session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :t LIMIT 1"
        ),
        {"t": table_name},
    ).first()
    return row is not None


def _as_json(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def _build_tree(nodes: list[dict]) -> dict:
    """nodes 已按 node_order 升序。返回 {version, root} 单链树。"""
    root = {
        "nodeKey": "start",
        "type": "start",
        "nodeName": "发起人",
        "childNode": None,
    }
    head = root
    for n in nodes:
        order = n["node_order"]
        node_obj = {
            "nodeKey": f"n{order}",
            "type": "approval" if n["node_type"] == 1 else "cc",
            "nodeName": n["node_name"] or f"节点{order}",
            "approverType": n["approver_type"],
            "approverConfig": _as_json(n["approver_config"]),
            "signType": n["sign_type"],
            "emptyStrategy": n["empty_strategy"],
            "allowTransfer": n["allow_transfer"],
            "allowAddsign": n["allow_addsign"],
            "childNode": None,
        }
        cond = _as_json(n["condition"])
        if cond and (cond.get("rules") if isinstance(cond, dict) else None):
            # 节点级条件 → 条件路由（命中走该节点，否则跳过）
            router = {
                "nodeKey": f"c{order}",
                "type": "condition",
                "nodeName": "条件分支",
                "conditionNodes": [
                    {
                        "nodeKey": f"cb{order}a",
                        "nodeName": "条件1",
                        "priority": 1,
                        "condition": cond,
                        "childNode": node_obj,
                    },
                    {
                        "nodeKey": f"cb{order}b",
                        "nodeName": "其它情况",
                        "priority": 2,
                        "condition": None,
                        "childNode": None,
                    },
                ],
                "childNode": None,
            }
            head["childNode"] = router
            head = router  # 后续节点接到条件路由的汇合点
        else:
            head["childNode"] = node_obj
            head = node_obj
    return {"version": 1, "root": root}


def convert_for_tenant(tenant_code: str, engine) -> int:
    converted = 0
    with Session(engine) as session:
        if not _table_exists(session, "biz_approval_flow"):
            return 0

        flows = session.execute(
            text(
                "SELECT id FROM biz_approval_flow "
                "WHERE is_deleted = 0 AND process_config IS NULL"
            )
        ).fetchall()

        for (flow_id,) in flows:
            rows = session.execute(
                text(
                    "SELECT node_order, node_type, node_name, approver_type, "
                    "approver_config, sign_type, `condition`, empty_strategy, "
                    "allow_transfer, allow_addsign "
                    "FROM biz_approval_flow_node "
                    "WHERE flow_id = :fid AND is_deleted = 0 "
                    "ORDER BY node_order ASC"
                ),
                {"fid": flow_id},
            ).mappings().all()
            if not rows:
                continue
            tree = _build_tree([dict(r) for r in rows])
            session.execute(
                text(
                    "UPDATE biz_approval_flow SET process_config = :cfg "
                    "WHERE id = :fid"
                ),
                {"cfg": json.dumps(tree, ensure_ascii=False), "fid": flow_id},
            )
            converted += 1

        session.commit()
    return converted


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
        print("[INFO] 无租户可转换，跳过")
        return

    print(f"[INFO] 将转换 {len(tenant_codes)} 个租户库的存量审批流程")
    for code in tenant_codes:
        tenant_engine = create_engine(settings.tenant_db_url_sync(code))
        try:
            n = convert_for_tenant(code, tenant_engine)
            print(f"  [{code}] 转换 {n} 个流程为画布树" if n else f"  [{code}] 无需转换")
        except Exception as e:  # noqa: BLE001
            print(f"  [{code}] 失败: {e}")
        finally:
            tenant_engine.dispose()

    print("[OK] 存量审批流程画布树转换完成")


if __name__ == "__main__":
    main()
