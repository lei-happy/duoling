import request from '@/utils/request';
import { download } from '@/utils/common';
import type { ApiResult, PageResult } from '@/api';
import type {
  Waybill,
  WaybillParam,
  WaybillWorkbenchStats,
  WaybillReceipt,
  WaybillReceiptConfirmPayload
} from './model';

export async function pageWaybills(params: WaybillParam) {
  const res = await request.get<ApiResult<PageResult<Waybill>>>(
    '/business/waybill',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 计划工作台 KPI：按状态聚合（可选与列表相同的筛选条件） */
export async function getWaybillWorkbenchStats(params?: WaybillParam) {
  const res = await request.get<ApiResult<WaybillWorkbenchStats>>(
    '/business/waybill/workbench-stats',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getWaybill(id: number) {
  const res = await request.get<ApiResult<Waybill>>(`/business/waybill/${id}`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 计划号是否可用（未被占用）；编辑传 excludeId 排除当前单 */
export async function checkWaybillNoAvailable(
  waybillNo: string,
  excludeId?: number
) {
  const q = waybillNo.trim();
  if (!q) return true;
  const res = await request.get<ApiResult<{ available: boolean }>>(
    '/business/waybill/check-waybill-no',
    { params: { waybillNo: q, excludeId } }
  );
  if (res.data.code === 0) {
    return res.data.data?.available ?? true;
  }
  return true;
}

export async function addWaybill(data: Waybill) {
  const res = await request.post<ApiResult<unknown>>('/business/waybill', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateWaybill(data: Waybill) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/waybill/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateWaybillStatus(id: number, status: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/waybill/${id}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 列举计划回单凭证 */
export async function listWaybillReceipts(id: number) {
  const res = await request.get<ApiResult<WaybillReceipt[]>>(
    `/business/waybill/${id}/receipts`
  );
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

/** 确认回单：计划 5 已签收 → 6 已回单 */
export async function confirmWaybillReceipt(
  id: number,
  data: WaybillReceiptConfirmPayload
) {
  const res = await request.post<ApiResult<Waybill>>(
    `/business/waybill/${id}/receipt`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 撤销回单：计划 6 已回单 → 5 已签收 */
export async function revokeWaybillReceipt(id: number) {
  const res = await request.delete<ApiResult<Waybill>>(
    `/business/waybill/${id}/receipt`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeWaybill(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/business/waybill/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 手动触发运费重算（异步任务） */
export async function recalculateWaybill(id: number) {
  const res = await request.post<ApiResult<{ taskId: number }>>(
    `/business/waybill/${id}/recalculate`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 获取计划当前活跃的计算结果 + 明细 + match_trace */
export async function getWaybillFreightResult(id: number) {
  const res = await request.get<ApiResult<unknown>>(
    `/business/waybill/${id}/freight-result`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 锁定计划（禁止重算） */
export async function lockWaybill(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/waybill/${id}/lock`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 解锁计划 */
export async function unlockWaybill(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/business/waybill/${id}/unlock`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export interface PreviewCargoLine {
  vehicleBrand?: string | null;
  vehicleModel?: string | null;
  quantity: number;
}

export interface PreviewRequest {
  customerId: number;
  originCode?: string | null;
  originRegionId?: number | null;
  origin?: string | null;
  destinationCode?: string | null;
  destinationRegionId?: number | null;
  destination?: string | null;
  cargoes: PreviewCargoLine[];
  billingDate?: string | null;
}

/** 整单试算（dry_run）：一次传所有 cargoes，返回每行结果 + match_trace */
export async function previewFreight(data: PreviewRequest) {
  const res = await request.post<ApiResult<unknown>>(
    '/billing/calculate/preview',
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export interface ImportBatchSummary {
  id: number;
  fileName?: string;
  totalCount: number;
  successCount: number;
  failCount: number;
  calcSuccessCount: number;
  calcExceptionCount: number;
  status: string;
  errorMessage?: string;
  createdBy?: number;
  createdAt?: string;
}

export interface ImportRowItem {
  id: number;
  batchId: number;
  rowNo: number;
  rawData?: Record<string, unknown>;
  validateStatus: string;
  validateMessage?: string;
  waybillId?: number;
  calcStatus?: string;
  createdAt?: string;
}

/** 下载计划批量导入 Excel 模板（表头与后端解析一致） */
export async function downloadWaybillImportTemplate(): Promise<void> {
  const res = await request.get('/business/waybill/import/template', {
    responseType: 'blob'
  });
  const blob = res.data as Blob;
  if (
    blob.type?.includes('application/json') ||
    blob.type?.includes('text/json')
  ) {
    const text = await blob.text();
    let msg = '下载失败';
    try {
      const j = JSON.parse(text) as { message?: string; msg?: string };
      msg = j.message || j.msg || msg;
    } catch {
      // ignore
    }
    throw new Error(msg);
  }
  const buf = await blob.arrayBuffer();
  download(buf, '计划批量导入模板.xlsx');
}

/** 上传 Excel 批量导入计划 */
export async function importWaybillExcel(file: File) {
  const fd = new FormData();
  fd.append('file', file);
  const res = await request.post<
    ApiResult<{
      batchId: number;
      totalCount: number;
      successCount: number;
      failCount: number;
      status: string;
    }>
  >('/business/waybill/import', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageImportBatches(page: number, limit = 20) {
  const res = await request.get<
    ApiResult<{
      list: ImportBatchSummary[];
      total: number;
      page: number;
      limit: number;
    }>
  >('/business/waybill/import/batches', { params: { page, limit } });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getImportBatch(batchId: number) {
  const res = await request.get<ApiResult<ImportBatchSummary>>(
    `/business/waybill/import/batch/${batchId}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listImportRows(
  batchId: number,
  params: { validateStatus?: string; page?: number; limit?: number } = {}
) {
  const res = await request.get<
    ApiResult<{
      list: ImportRowItem[];
      total: number;
      page: number;
      limit: number;
    }>
  >(`/business/waybill/import/batch/${batchId}/rows`, { params });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
