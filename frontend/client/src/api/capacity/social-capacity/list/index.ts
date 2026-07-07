import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  SocialCapacityAccount,
  SocialCapacityAccountForm,
  SocialCapacityActionBody,
  SocialCapacityAudit,
  SocialCapacityDetail,
  SocialCapacityForm,
  SocialCapacityListItem,
  SocialCapacityParam,
  SocialCapacitySelectItem,
  SocialCapacityStatusBody,
  SocialCapacityListStats
} from './model';
import type {
  DriverFundAccount,
  DriverFundTransaction,
  DriverFundTransactionParam
} from '@/api/capacity/self-capacity/driver/model';

const BASE = '/capacity/social_capacity/list';

export async function socialCapacityListStats(params?: SocialCapacityParam) {
  const res = await request.get<ApiResult<SocialCapacityListStats>>(
    `${BASE}/stats`,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function pageSocialCapacities(params: SocialCapacityParam) {
  const res = await request.get<ApiResult<PageResult<SocialCapacityListItem>>>(
    BASE,
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listForDispatch(keyword?: string, limit = 50) {
  const res = await request.get<ApiResult<SocialCapacitySelectItem[]>>(
    `${BASE}/select`,
    { params: { keyword, limit } }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function getSocialCapacity(id: number) {
  const res = await request.get<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listAuditHistory(id: number) {
  const res = await request.get<ApiResult<SocialCapacityAudit[]>>(
    `${BASE}/${id}/audit-history`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addSocialCapacity(data: SocialCapacityForm) {
  const res = await request.post<ApiResult<SocialCapacityDetail>>(BASE, data);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateSocialCapacity(
  id: number,
  data: SocialCapacityForm
) {
  const res = await request.put<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeSocialCapacity(id: number) {
  const res = await request.delete<ApiResult<unknown>>(`${BASE}/${id}`);
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function submitSocialCapacity(
  id: number,
  data?: SocialCapacityActionBody
) {
  const res = await request.post<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}/submit`,
    data ?? {}
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function withdrawSocialCapacity(
  id: number,
  data?: SocialCapacityActionBody
) {
  const res = await request.post<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}/withdraw`,
    data ?? {}
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateSocialCapacityStatus(
  id: number,
  data: SocialCapacityStatusBody
) {
  const res = await request.put<ApiResult<SocialCapacityDetail>>(
    `${BASE}/${id}/status`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

// =====================================================
// 结算账户
// =====================================================
export async function listAccounts(socialCapacityId: number) {
  const res = await request.get<ApiResult<SocialCapacityAccount[]>>(
    `${BASE}/${socialCapacityId}/accounts`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addAccount(
  socialCapacityId: number,
  data: SocialCapacityAccountForm
) {
  const res = await request.post<ApiResult<SocialCapacityAccount>>(
    `${BASE}/${socialCapacityId}/accounts`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateAccount(
  socialCapacityId: number,
  accountId: number,
  data: SocialCapacityAccountForm
) {
  const res = await request.put<ApiResult<SocialCapacityAccount>>(
    `${BASE}/${socialCapacityId}/accounts/${accountId}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeAccount(
  socialCapacityId: number,
  accountId: number
) {
  const res = await request.delete<ApiResult<unknown>>(
    `${BASE}/${socialCapacityId}/accounts/${accountId}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function setDefaultAccount(
  socialCapacityId: number,
  accountId: number
) {
  const res = await request.post<ApiResult<SocialCapacityAccount>>(
    `${BASE}/${socialCapacityId}/accounts/${accountId}/set-default`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

// =====================================================
// 资金账户（往来账，owner_type=3 社会运力）—— 复用统一资金账户模型
// =====================================================
export async function getSocialFundAccount(socialCapacityId: number) {
  const res = await request.get<ApiResult<DriverFundAccount>>(
    `${BASE}/${socialCapacityId}/fund-account`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function listSocialFundTransactions(
  socialCapacityId: number,
  params: {
    page?: number;
    limit?: number;
    bizType?: number;
    source?: number;
    start?: string;
    end?: string;
  }
) {
  const res = await request.get<
    ApiResult<{ list: DriverFundTransaction[]; total: number }>
  >(`${BASE}/${socialCapacityId}/fund-account/transactions`, { params });
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function postSocialFundTransaction(
  socialCapacityId: number,
  data: DriverFundTransactionParam
) {
  const res = await request.post<ApiResult<DriverFundTransaction>>(
    `${BASE}/${socialCapacityId}/fund-account/transactions`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function toggleSocialFundAccountStatus(
  accountId: number,
  status: number
) {
  const res = await request.patch<ApiResult<DriverFundAccount>>(
    `${BASE}/fund-account/${accountId}/status`,
    { status }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
