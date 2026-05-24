import type { Waybill, WaybillCargoLine } from '@/api/waybill/model';
import type { Task, TaskWaybillItem } from '@/api/operation/task/model';

/** 按台数汇总主品牌/车型，用于分配承运弹窗突出展示 */
export function summarizeTaskBrandModels(items: TaskWaybillItem[]): string {
  if (!items?.length) return '--';
  const map = new Map<string, number>();
  for (const it of items) {
    const brand = (it.vehicleBrand || '').trim();
    const model = (it.vehicleModel || '').trim();
    const key = [brand, model].filter(Boolean).join(' / ') || '—';
    map.set(key, (map.get(key) || 0) + (it.quantity || 0));
  }
  const sorted = [...map.entries()].sort((a, b) => b[1] - a[1]);
  if (sorted.length === 1) {
    const [key, qty] = sorted[0]!;
    return qty > 1 ? `${key} × ${qty}` : key;
  }
  const [top, qty] = sorted[0]!;
  return `${top} × ${qty} 等 ${sorted.length} 种`;
}

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
