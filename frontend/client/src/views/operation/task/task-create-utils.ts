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

/** 序列化商品车挂接 payload */
export function buildWaybillItemsPayload(waybillItems: TaskWaybillItem[]) {
  return waybillItems.map((w) => ({
    waybillId: w.waybillId,
    waybillCargoId: w.waybillCargoId,
    quantity: w.quantity,
    segmentId: w.segmentId ?? undefined,
    remark: w.remark
  }));
}
