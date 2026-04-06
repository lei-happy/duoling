import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { VehicleBrand, VehicleBrandOption } from './model';

export async function pageVehicleBrands(params: {
  page?: number;
  limit?: number;
  keyword?: string;
}) {
  const res = await request.get<
    ApiResult<{ list: VehicleBrand[]; count: number }>
  >('/basic-data/vehicle-brand', { params });
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listVehicleBrandOptions(params?: {
  keyword?: string;
  limit?: number;
}) {
  const res = await request.get<ApiResult<VehicleBrandOption[]>>(
    '/basic-data/vehicle-brand/options',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data ?? [];
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getVehicleBrand(brandId: number) {
  const res = await request.get<ApiResult<VehicleBrand>>(
    `/basic-data/vehicle-brand/${brandId}`
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addVehicleBrand(data: {
  brandNameCn: string;
  brandLogo?: string;
  brandCountry?: string;
  brandIntroduce?: string;
}) {
  const res = await request.post<ApiResult<VehicleBrand>>(
    '/basic-data/vehicle-brand',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateVehicleBrand(
  brandId: number,
  data: {
    brandNameCn?: string;
    brandLogo?: string;
    brandCountry?: string;
    brandIntroduce?: string;
  }
) {
  const res = await request.put<ApiResult<VehicleBrand>>(
    `/basic-data/vehicle-brand/${brandId}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeVehicleBrand(brandId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/basic-data/vehicle-brand/${brandId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
