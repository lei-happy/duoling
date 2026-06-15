import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  CarrierCapacityDetail,
  CarrierCapacityListItem,
  CarrierCapacityParam,
  CarrierCapacitySaveParam
} from './model';

const BASE = '/capacity/carrier_capacity/list';

export async function pageCarrierCapacities(params: CarrierCapacityParam) {
  const res = await request.get<ApiResult<PageResult<CarrierCapacityListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function getCarrierCapacity(id: number) {
  const res = await request.get<ApiResult<CarrierCapacityDetail>>(
    `${BASE}/${id}`
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function addCarrierCapacity(data: CarrierCapacitySaveParam) {
  const res = await request.post<ApiResult<CarrierCapacityDetail>>(BASE, data);
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function updateCarrierCapacity(
  id: number,
  data: CarrierCapacitySaveParam
) {
  const res = await request.put<ApiResult<CarrierCapacityDetail>>(
    `${BASE}/${id}`,
    data
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}

export async function changeCarrierCapacityStatus(
  id: number,
  status: number,
  statusRemark?: string
) {
  const res = await request.put<ApiResult<unknown>>(`${BASE}/${id}/status`, {
    status,
    statusRemark
  });
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}

export async function removeCarrierCapacity(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) return res.data.message;
  return Promise.reject(new Error(res.data.message));
}
