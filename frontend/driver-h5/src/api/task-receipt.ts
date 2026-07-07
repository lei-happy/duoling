import { del, get, post } from './request';
import type { PageResult } from './task';

export interface ReceiptItem {
  id: number;
  taskId: number;
  dispatchOrderId?: number;
  itemId?: number;
  driverId?: number;
  receiptType?: number;
  fileUrls: string[];
  remark?: string;
  uploaderName?: string;
  createdAt?: string;
}

export function uploadReceipt(payload: {
  taskId: number;
  itemId?: number;
  dispatchOrderId?: number;
  receiptType?: number;
  fileUrls: string[];
  remark?: string;
}) {
  return post<ReceiptItem>('/task-receipt/upload', payload);
}

export function listMyReceipts(params?: {
  page?: number;
  pageSize?: number;
  taskId?: number;
}) {
  return get<PageResult<ReceiptItem>>(
    '/task-receipt/my',
    params as Record<string, unknown>
  );
}

export function deleteReceipt(id: number) {
  return del<void>(`/task-receipt/${id}`);
}
