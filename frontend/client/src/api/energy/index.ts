import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';

async function get<T>(url: string, params?: Record<string, unknown>) {
  const res = await request.get<ApiResult<T>>(url, { params });
  if (res.data.code === 0) return res.data.data as T;
  return Promise.reject(new Error(res.data.message));
}

async function post<T>(url: string, data?: unknown) {
  const res = await request.post<ApiResult<T>>(url, data);
  if (res.data.code === 0) return res.data.data as T;
  return Promise.reject(new Error(res.data.message));
}

async function put<T>(url: string, data?: unknown) {
  const res = await request.put<ApiResult<T>>(url, data);
  if (res.data.code === 0) return res.data.data as T;
  return Promise.reject(new Error(res.data.message));
}

async function del<T>(url: string) {
  const res = await request.delete<ApiResult<T>>(url);
  if (res.data.code === 0) return res.data.data as T;
  return Promise.reject(new Error(res.data.message));
}

export const energyMeta = () => get<any>('/energy/meta');

export const pageSuppliers = (params: any) =>
  get<PageResult<any>>('/energy/suppliers', params);
export const addSupplier = (data: any) => post('/energy/suppliers', data);
export const updateSupplier = (id: number, data: any) =>
  put(`/energy/suppliers/${id}`, data);
export const removeSupplier = (id: number) => del(`/energy/suppliers/${id}`);

export const pageStations = (params: any) =>
  get<PageResult<any>>('/energy/stations', params);
export const getStation = (id: number) => get<any>(`/energy/stations/${id}`);
export const addStation = (data: any) => post('/energy/stations', data);
export const updateStation = (id: number, data: any) =>
  put(`/energy/stations/${id}`, data);
export const removeStation = (id: number) => del(`/energy/stations/${id}`);

export const pageAccounts = (params: any) =>
  get<PageResult<any>>('/energy/accounts', params);
export const addAccount = (data: any) => post('/energy/accounts', data);
export const updateAccount = (id: number, data: any) =>
  put(`/energy/accounts/${id}`, data);
export const removeAccount = (id: number) => del(`/energy/accounts/${id}`);
export const pageAccountTxns = (id: number, params: any) =>
  get<PageResult<any>>(`/energy/accounts/${id}/txns`, params);
export const adjustAccount = (id: number, data: any) =>
  post(`/energy/accounts/${id}/adjust`, data);

export const pageCards = (params: any) =>
  get<PageResult<any>>('/energy/cards', params);
export const addCard = (data: any) => post('/energy/cards', data);
export const updateCard = (id: number, data: any) =>
  put(`/energy/cards/${id}`, data);
export const removeCard = (id: number) => del(`/energy/cards/${id}`);
export const bindCard = (id: number, data: any) =>
  post(`/energy/cards/${id}/bind`, data);
export const unbindCard = (id: number) => post(`/energy/cards/${id}/unbind`);

export const pageRecharges = (params: any) =>
  get<PageResult<any>>('/energy/recharges', params);
export const addRecharge = (data: any) => post('/energy/recharges', data);
export const payRecharge = (id: number, data: any) =>
  post(`/energy/recharges/${id}/pay`, data);
export const cancelRecharge = (id: number, data: any) =>
  post(`/energy/recharges/${id}/cancel`, data);

export const pageConsumptions = (params: any) =>
  get<PageResult<any>>('/energy/consumptions', params);
export const addConsumption = (data: any) =>
  post('/energy/consumptions', data);
export const assignConsumption = (id: number, data: any) =>
  post(`/energy/consumptions/${id}/assign`, data);

export const pageConnectors = (params: any) =>
  get<PageResult<any>>('/energy/connectors', params);
export const addConnector = (data: any) => post('/energy/connectors', data);
export const pullConnector = (id: number) =>
  post(`/energy/connectors/${id}/pull`);
export const importConnector = (id: number, file: File) => {
  const form = new FormData();
  form.append('file', file);
  return request
    .post<ApiResult<any>>(`/energy/connectors/${id}/import`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    .then((res) => {
      if (res.data.code === 0) return res.data.data;
      return Promise.reject(new Error(res.data.message));
    });
};

export const pageRecons = (params: any) =>
  get<PageResult<any>>('/energy/recons', params);
export const createBalanceRecon = (data: any) =>
  post('/energy/recons/balance', data);
export const createConsumptionRecon = (data: any) =>
  post('/energy/recons/consumption', data);
export const reconItems = (id: number) => get<any[]>(`/energy/recons/${id}/items`);
export const processReconItem = (id: number, data: any) =>
  post(`/energy/recons/items/${id}/process`, data);
export const settleRecon = (id: number) => post(`/energy/recons/${id}/settle`);

export const pageExceptions = (params: any) =>
  get<PageResult<any>>('/energy/exceptions', params);
export const exceptionStats = () => get<any>('/energy/exceptions/stats');
export const resolveException = (id: number, data: any) =>
  post(`/energy/exceptions/${id}/resolve`, data);

export const analysisOverview = () => get<any>('/energy/analysis/overview');
export const analysisVehicleCost = (params: any) =>
  get<any[]>('/energy/analysis/vehicle-cost', params);
export const analysisSupplier = (params: any) =>
  get<any[]>('/energy/analysis/supplier-compare', params);

export const listProducts = () => get<any[]>('/energy/products');
export const addProduct = (data: any) => post('/energy/products', data);
export const updateProduct = (id: number, data: any) =>
  put(`/energy/products/${id}`, data);
export const removeProduct = (id: number) => del(`/energy/products/${id}`);
export const pageProfiles = (params: any) =>
  get<PageResult<any>>('/energy/vehicle-profiles', params);
export const upsertProfile = (data: any) =>
  post('/energy/vehicle-profiles', data);
export const listRules = () => get<any[]>('/energy/rules');
export const updateRule = (id: number, data: any) =>
  put(`/energy/rules/${id}`, data);
