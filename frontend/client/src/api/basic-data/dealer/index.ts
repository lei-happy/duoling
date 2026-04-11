import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { Dealer, DealerParam } from './model';

export async function pageDealers(params: DealerParam) {
  const res = await request.get<ApiResult<{ list: Dealer[]; count: number }>>(
    '/basic-data/dealer',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getDealer(dealerId: number) {
  const res = await request.get<ApiResult<Dealer>>(
    `/basic-data/dealer/${dealerId}`
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addDealer(data: {
  dealerName: string;
  dealerType: string;
  mainBrand: string;
  province: string;
  city: string;
  addressDetail: string;
  longitude?: number;
  latitude?: number;
}) {
  const res = await request.post<ApiResult<Dealer>>('/basic-data/dealer', data);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateDealer(
  dealerId: number,
  data: {
    dealerName?: string;
    dealerType?: string;
    mainBrand?: string;
    province?: string;
    city?: string;
    addressDetail?: string;
    longitude?: number;
    latitude?: number;
  }
) {
  const res = await request.put<ApiResult<Dealer>>(
    `/basic-data/dealer/${dealerId}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeDealer(dealerId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/basic-data/dealer/${dealerId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
