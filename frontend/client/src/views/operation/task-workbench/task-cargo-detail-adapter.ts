import type { Waybill, WaybillCargoLine } from '@/api/waybill/model';
import type { Task, TaskWaybillItem } from '@/api/operation/task/model';

/**
 * 将任务单 + 挂接明细组装为「商品车明细」弹窗所需的 Waybill 形态（与运单列表复用 waybill-cargoes-detail）。
 */
export function buildWaybillShapeForTaskCargoDetail(
  task: Task,
  items: TaskWaybillItem[]
): Waybill {
  const lines: WaybillCargoLine[] = items.map((it, idx) => ({
    vehicleBrand: it.vehicleBrand?.trim() || undefined,
    vehicleModel: it.vehicleModel?.trim() || undefined,
    quantity: it.quantity ?? 0,
    sortOrder: idx,
    seriesImage: it.seriesImage ?? null,
    vin: null
  }));

  const names = [
    ...new Set(
      items
        .map((i) => i.customerName?.trim())
        .filter((n): n is string => !!n && n.length > 0)
    )
  ];
  const nos = [
    ...new Set(
      items
        .map((i) => i.waybillNo?.trim())
        .filter((n): n is string => !!n && n.length > 0)
    )
  ];

  const customerName =
    names.length === 1
      ? names[0]
      : names.length > 1
        ? `多客户（${names.length} 家）`
        : '—';

  const waybillNo =
    nos.length === 1
      ? nos[0]!
      : nos.length > 1
        ? `${nos.length} 张运单`
        : task.taskNo?.trim() || '';

  return {
    waybillNo,
    customerName,
    origin: task.origin?.trim() || undefined,
    destination: task.destination?.trim() || undefined,
    cargoes: lines,
    quantity: items.reduce((s, i) => s + (i.quantity || 0), 0)
  };
}
