"""任务成本按台数分摊工具（文档 13 §3.2）

一个任务通常拉多个客户的车，成本发生在任务上、收入确认在运单上，所以要分摊。基准是
**挂接行台数**（``biz_task_waybill_item.quantity``）：台数是汽车物流的天然计量单位，
挂接行上就有准确值，不需要像里程那样按段拆。

两个必须保证的性质：

1. **分摊无损**：各运单分摊额之和 = 任务成本，尾差（分位除不尽）归最后一行；
2. **摊不掉的显式留下**：没有挂接行、或台数合计为 0 的任务，成本原样进「未分摊」，
   既不丢弃也不强行摊给某个客户——空驶率高本身就是要看的管理指标。

纯函数，不碰数据库：查询在 service 里做，这里只负责算，便于与 ``insight`` 侧用同一批
用例验证行为一致（文档 13 §5.3）。
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Sequence, Tuple

_CENT = Decimal("0.01")


def allocate_task_cost_to_waybills(
    task_costs: Dict[int, Decimal],
    task_items: Dict[int, Sequence[Tuple[int, Decimal]]],
) -> Tuple[Dict[int, Decimal], Decimal]:
    """把每个任务的成本按台数摊到运单。

    参数：
        task_costs: ``{task_id: 该任务成本}``
        task_items: ``{task_id: [(waybill_id, quantity), ...]}``

    返回 ``({waybill_id: 分摊成本}, 未分摊成本合计)``。
    """
    allocated: Dict[int, Decimal] = {}
    unallocated = Decimal("0")

    for task_id, cost in task_costs.items():
        amount = _money(cost)
        if amount == 0:
            continue
        rows = [
            (int(wid), Decimal(str(qty or 0)))
            for wid, qty in (task_items.get(int(task_id)) or [])
        ]
        total_qty = sum((q for _, q in rows), Decimal("0"))
        if not rows or total_qty <= 0:
            unallocated += amount
            continue
        assigned = Decimal("0")
        for idx, (wid, qty) in enumerate(rows):
            if idx == len(rows) - 1:
                part = amount - assigned  # 尾差归最后一行，保证分摊无损
            else:
                part = _money(amount * qty / total_qty)
                assigned += part
            allocated[wid] = allocated.get(wid, Decimal("0")) + part
    return allocated, _money(unallocated)


def split_doc_amount_by_task(
    doc_amount: Decimal,
    task_weights: Sequence[Tuple[int, Decimal]],
) -> List[Tuple[int, Decimal]]:
    """把一张单据的金额按任务权重拆到任务上（权重通常是任务侧应付净额）。

    权重全为 0 时按任务数平均：这类单（如只有底薪的工资单）本身没有任务级金额，平均
    摊比整单进「未分摊」更接近事实。返回空列表表示这张单没有任务可摊。
    """
    amount = _money(doc_amount)
    rows = [(int(t), Decimal(str(w or 0))) for t, w in task_weights]
    if not rows or amount == 0:
        return []
    total = sum((w for _, w in rows), Decimal("0"))
    if total <= 0:
        share = _money(amount / len(rows))
        out = [(t, share) for t, _ in rows[:-1]]
        out.append((rows[-1][0], amount - share * (len(rows) - 1)))
        return out
    out: List[Tuple[int, Decimal]] = []
    assigned = Decimal("0")
    for idx, (task_id, weight) in enumerate(rows):
        if idx == len(rows) - 1:
            part = amount - assigned
        else:
            part = _money(amount * weight / total)
            assigned += part
        out.append((task_id, part))
    return out


def _money(v) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)
