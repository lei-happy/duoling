import { get, post } from './request';
import type { PageResult } from './task';

export interface ReceiptItem {
  id: number;
  taskId: number;
  taskNo?: string;
  itemId?: number;
  fileUrl: string;
  uploadedAt: string;
  remark?: string;
}

export function uploadReceipt(payload: {
  taskId: number;
  itemId?: number;
  fileUrl: string;
  remark?: string;
}) {
  return post<ReceiptItem>('/task-receipt/upload', payload);
}

export function listMyReceipts(params?: { page?: number; pageSize?: number; taskId?: number }) {
  return get<PageResult<ReceiptItem>>('/task-receipt/my', params as Record<string, unknown>);
}
