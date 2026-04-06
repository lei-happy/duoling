import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { VehicleSeries } from './model';

export async function pageVehicleSeries(params: {
  brandId: number;
  page?: number;
  limit?: number;
  keyword?: string;
}) {
  const res = await request.get<
    ApiResult<{ list: VehicleSeries[]; count: number }>
  >('/basic-data/vehicle-series', { params });
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getVehicleSeries(seriesId: number) {
  const res = await request.get<ApiResult<VehicleSeries>>(
    `/basic-data/vehicle-series/${seriesId}`
  );
  if (res.data.code === 0) {
    return res.data.data!;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addVehicleSeries(data: {
  brandId: number;
  seriesName: string;
  price?: string;
  seriesImage?: string;
  energyType?: string;
  lengthMm?: number;
  widthMm?: number;
  heightMm?: number;
  wheelbaseMm?: number;
  frontTrackMm?: number;
  rearTrackMm?: number;
  approachAngle?: number;
  departureAngle?: number;
  curbWeightKg?: number;
}) {
  const res = await request.post<ApiResult<VehicleSeries>>(
    '/basic-data/vehicle-series',
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateVehicleSeries(
  seriesId: number,
  data: {
    seriesName?: string;
    price?: string;
    seriesImage?: string;
    energyType?: string;
    lengthMm?: number;
    widthMm?: number;
    heightMm?: number;
    wheelbaseMm?: number;
    frontTrackMm?: number;
    rearTrackMm?: number;
    approachAngle?: number;
    departureAngle?: number;
    curbWeightKg?: number;
  }
) {
  const res = await request.put<ApiResult<VehicleSeries>>(
    `/basic-data/vehicle-series/${seriesId}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeVehicleSeries(seriesId: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/basic-data/vehicle-series/${seriesId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}
