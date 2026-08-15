import { EleMessage } from 'ele-admin-plus';
import type { TaskWaybillItem } from '@/api/operation/task/model';

/** 校验商品车挂接（新建配载 / 编辑商品车 Tab 共用） */
export function validateCargoTab(waybillItems: TaskWaybillItem[]): boolean {
  if (waybillItems.length < 1) {
    EleMessage.warning({ message: '请至少选择一条商品车挂接', plain: true });
    return false;
  }
  for (const it of waybillItems) {
    if (!it.quantity || it.quantity <= 0) {
      EleMessage.warning({
        message: '所有挂接商品车台数必须大于 0',
        plain: true
      });
      return false;
    }
  }
  return true;
}

/** 序列化商品车挂接 payload（同 cargo 行合并台数） */
export function buildWaybillItemsPayload(waybillItems: TaskWaybillItem[]) {
  const merged = new Map<
    number,
    {
      waybillId: number;
      waybillCargoId: number;
      quantity: number;
      segmentId: number | undefined;
      remark: string | undefined;
    }
  >();
  for (const item of waybillItems) {
    const cargoId = Number(item.waybillCargoId);
    if (!Number.isFinite(cargoId) || cargoId <= 0) continue;
    const quantity = Number(item.quantity) || 0;
    if (quantity <= 0) continue;
    const prev = merged.get(cargoId);
    if (prev) {
      prev.quantity += quantity;
      continue;
    }
    merged.set(cargoId, {
      waybillId: item.waybillId,
      waybillCargoId: cargoId,
      quantity,
      segmentId: item.segmentId ?? undefined,
      remark: item.remark
    });
  }
  return [...merged.values()];
}
