import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type {
  CostPolicy,
  CostPolicyParam,
  CostRule,
  CostRuleWithPolicy,
  CostRuleCenterParam,
  CostMeta,
  TaskCostResult,
  TaskCostPreviewRequest
} from './model';

/** 分页查询成本政策 */
export async function pagePolicies(params: CostPolicyParam) {
  const res = await request.get<ApiResult<PageResult<CostPolicy>>>(
    '/billing/cost-policy',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 政策详情（含规则列表） */
export async function getPolicy(id: number) {
  const res = await request.get<ApiResult<CostPolicy>>(
    `/billing/cost-policy/${id}`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addPolicy(data: CostPolicy) {
  const res = await request.post<ApiResult<CostPolicy>>(
    '/billing/cost-policy',
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updatePolicy(data: CostPolicy) {
  const res = await request.put<ApiResult<CostPolicy>>(
    `/billing/cost-policy/${data.id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function activatePolicy(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/cost-policy/${id}/activate`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function terminatePolicy(id: number) {
  const res = await request.put<ApiResult<unknown>>(
    `/billing/cost-policy/${id}/terminate`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removePolicy(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/billing/cost-policy/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 政策下费用规则 */
export async function listRules(policyId: number) {
  const res = await request.get<ApiResult<CostRule[]>>(
    `/billing/cost-policy/${policyId}/rule`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function addRule(policyId: number, data: CostRule) {
  const res = await request.post<ApiResult<CostRule>>(
    `/billing/cost-policy/${policyId}/rule`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function updateRule(id: number, data: CostRule) {
  const res = await request.put<ApiResult<CostRule>>(
    `/billing/cost-rule/${id}`,
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function removeRule(id: number) {
  const res = await request.delete<ApiResult<unknown>>(
    `/billing/cost-rule/${id}`
  );
  if (res.data.code === 0) {
    return res.data.message;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 费用中心：跨政策查询全部费用规则 */
export async function listCostRulesCrossPolicy(params: CostRuleCenterParam) {
  const res = await request.get<ApiResult<CostRuleWithPolicy[]>>(
    '/billing/cost-rule',
    { params }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export async function recalculateAffectedByRule(id: number) {
  const res = await request.post<
    ApiResult<{ affectedTaskCount: number; enqueuedTaskCount: number }>
  >(`/billing/cost-rule/${id}/recalculate-affected`);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

export interface CostRuleConflictPayload {
  ruleId?: number;
  policyId: number;
  feeType: string;
  originRegionId?: number | null;
  destinationRegionId?: number | null;
  brandId?: number | null;
  seriesId?: number | null;
  priceType?: number;
  effectiveDate?: string | null;
  expiryDate?: string | null;
}

export async function checkRuleConflict(payload: CostRuleConflictPayload) {
  const res = await request.post<
    ApiResult<{
      conflicts: unknown[];
      hasError: boolean;
      count: number;
    }>
  >('/billing/cost-rule/check-conflict', payload);
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 元数据（费用类型 / 计价方式） */
export async function getCostMeta() {
  const res = await request.get<ApiResult<CostMeta>>('/billing/cost-meta');
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 任务成本试算（不落库） */
export async function previewTaskCost(data: TaskCostPreviewRequest) {
  const res = await request.post<ApiResult<TaskCostResult>>(
    '/billing/task-cost/preview',
    data
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 任务成本正式重算（落库） */
export async function recalculateTaskCost(taskId: number) {
  const res = await request.post<ApiResult<TaskCostResult>>(
    `/billing/task/${taskId}/cost/recalculate`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 查询任务当前有效成本结果 */
export async function getTaskCostResult(taskId: number) {
  const res = await request.get<ApiResult<TaskCostResult | null>>(
    `/billing/task/${taskId}/cost-result`
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}
