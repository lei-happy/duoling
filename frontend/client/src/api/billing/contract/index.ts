import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  FreightContract,
  FreightContractParam,
  FreightRate,
  FreightCalcRequest,
  FreightCalcResult
} from './model';

export async function pageContracts(params: FreightContractParam) {
  const res = await request.get<ApiResult<PageResult<FreightContract>>>(
    '/billing/contract',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getContract(id: number) {
  const res = await request.get<ApiResult<FreightContract>>(
    `/billing/contract/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addContract(data: FreightContract) {
  const res = await request.post<ApiResult<unknown>>(
    '/billing/contract',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateContract(data: FreightContract) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/contract/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function activateContract(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/contract/${id}/activate`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function terminateContract(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/contract/${id}/terminate`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function resumeContract(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/contract/${id}/resume`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeContract(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/billing/contract/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listRates(contractId: number) {
  const res = await request.get<ApiResult<FreightRate[]>>(
    `/billing/contract/${contractId}/rate`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addRate(contractId: number, data: FreightRate) {
  const res = await request.post<ApiResult<unknown>>(
    `/billing/contract/${contractId}/rate`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateRate(id: number, data: FreightRate) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/rate/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeRate(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/billing/rate/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function calculateFreight(data: FreightCalcRequest) {
  const res = await request.post<ApiResult<FreightCalcResult | null>>(
    '/billing/calculate',
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
