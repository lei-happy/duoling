/** 智能配载 - 类型定义 */

/** 一键生成配载方案入参 */
export interface SmartStowageGeneratePayload {
  /** 运单号/客户关键字 */
  keyword?: string;
  customerId?: number;
  /** 起点关键字 */
  originKeyword?: string;
  /** 终点关键字 */
  destinationKeyword?: string;
  /** 品牌/车型关键字 */
  modelKeyword?: string;
  /** 候选拉取上限 */
  limit?: number;
  /** 目标板车车位数 */
  targetSpots?: number;
  /** 装载率下限(0-100) */
  minLoadRate?: number;
  /** 最多产出方案数 */
  maxPlans?: number;
  /** 打分权重覆盖 */
  weights?: Record<string, number>;
  /** 占位系数覆盖 { 车型关键字: 系数 } */
  occupyOverrides?: Record<string, number>;
}

/** 方案明细（商品车挂接候选） */
export interface SmartStowagePlanItem {
  id: number;
  waybillId: number;
  waybillCargoId: number;
  quantity: number;
  waybillNo?: string;
  customerName?: string;
  vehicleBrand?: string;
  vehicleModel?: string;
  vin?: string;
  origin?: string;
  destination?: string;
  occupyCoefficient: number;
}

/** 方案状态 0待采纳 1已采纳 2已忽略 */
export type SmartStowagePlanStatus = 0 | 1 | 2;

/** 推荐配载方案 */
export interface SmartStowagePlan {
  id: number;
  planTaskId: number;
  planNo: number;
  origin?: string;
  destination?: string;
  vehicleCount: number;
  occupiedSpots: number;
  targetSpots: number;
  loadRate: number;
  customerCount: number;
  waybillCount: number;
  score: number;
  reason?: string;
  status: SmartStowagePlanStatus;
  adoptedTaskId?: number | null;
  adoptedAt?: string | null;
  items: SmartStowagePlanItem[];
}

/** 生成任务 */
export interface SmartStowageTask {
  id: number;
  status: 'pending' | 'running' | 'success' | 'failed';
  candidateCount: number;
  planCount: number;
  adoptedCount: number;
  errorMessage?: string;
  triggeredByName?: string;
  startedAt?: string;
  finishedAt?: string;
  createdAt?: string;
}

/** 生成接口返回 */
export interface SmartStowageGenerateResult {
  task: SmartStowageTask;
  plans: SmartStowagePlan[];
}
