import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  CarrierContract,
  CarrierContractParam,
  CarrierRate,
  CarrierFreightPreviewRequest,
  CarrierFreightResult
} from './model';

const CONTRACT_BASE = '/billing/carrier-contract';
const RATE_BASE = '/billing/carrier-rate';

export async function pageContracts(params: CarrierContractParam) {
  const res = await request.get<ApiResult<PageResult<CarrierContract>>>(
    CONTRACT_BASE,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getContract(id: number) {
  const res = await request.get<ApiResult<CarrierContract>>(
    `${CONTRACT_BASE}/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addContract(data: CarrierContract) {
  const res = await request.post<ApiResult<unknown>>(CONTRACT_BASE, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateContract(data: CarrierContract) {
  const res = await request.put<ApiResult<unknown>>(
    `${CONTRACT_BASE}/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function activateContract(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `${CONTRACT_BASE}/${id}/activate`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function terminateContract(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `${CONTRACT_BASE}/${id}/terminate`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function resumeContract(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `${CONTRACT_BASE}/${id}/resume`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeContract(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `${CONTRACT_BASE}/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listRates(contractId: number) {
  const res = await request.get<ApiResult<CarrierRate[]>>(
    `${CONTRACT_BASE}/${contractId}/rate`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addRate(contractId: number, data: CarrierRate) {
  const res = await request.post<ApiResult<unknown>>(
    `${CONTRACT_BASE}/${contractId}/rate`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateRate(id: number, data: CarrierRate) {
  const res = await request.put<ApiResult<unknown>>(`${RATE_BASE}/${id}`, data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeRate(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${RATE_BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 承运价规则版本变更历史 */
export async function listRateVersionHistory(rateId: number) {
  const res = await request.get<ApiResult<unknown[]>>(
    `${RATE_BASE}/${rateId}/version-history`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 触发该承运价规则的受影响任务批量重算 */
export async function recalculateAffectedByRate(rateId: number) {
  const res = await request.post<
    ApiResult<{
      affectedTaskCount: number;
      enqueuedTaskCount: number;
    }>
  >(`${RATE_BASE}/${rateId}/recalculate-affected`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 承运商运费试算（不落库） */
export async function previewCarrierFreight(
  data: CarrierFreightPreviewRequest
) {
  const res = await request.post<ApiResult<CarrierFreightResult | null>>(
    '/billing/carrier-freight/preview',
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 手动重算某任务的承运商运费 */
export async function recalculateTaskCarrierFreight(taskId: number) {
  const res = await request.post<ApiResult<CarrierFreightResult>>(
    `/billing/task/${taskId}/carrier-freight/recalculate`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 查询某任务最新的承运商运费结果 */
export async function getTaskCarrierFreightResult(taskId: number) {
  const res = await request.get<ApiResult<CarrierFreightResult | null>>(
    `/billing/task/${taskId}/carrier-freight-result`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
