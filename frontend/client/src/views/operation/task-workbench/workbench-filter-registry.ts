/**
 * 调度工作台 — 筛选字段注册表
 *
 * 每个阶段池关心的筛选条件并不相同（待分配还没有承运方，待交车不关心计划装车时间），
 * 因此把「字段」抽成独立描述，由 `WorkbenchPool.filterFields` 声明**用哪些**。
 *
 * ## 槽位规则（顺序不由池决定）
 *
 * 字段集合可变，但位置不能跟着变，否则用户每切一次阶段都要重新找输入框。所以：
 *
 * 1. **宽度统一**：所有字段共用 `FIELD_COL`，lg 下每行 4 个，不再分宽窄档。
 * 2. **共有字段锚定**：`group: 'common'` 的字段（任务单号 / 出发地 / 目的地）每个池都有，
 *    恒定占据第一行前三格，位置在任何阶段完全一致。
 * 3. **池专属字段顺延**：`group: 'pool'` 的字段从第一行第四格开始，按 `FIELD_ORDER`
 *    的全局次序排列 —— 池声明的先后顺序被忽略，避免同一字段在不同池里前后不一。
 * 4. **时间行独占末行**：时间维度(6) + 日期区间(12) + 搜索重置(6) = 24，由模板固定渲染，
 *    不受前面字段增减影响。
 *
 * 条件显隐字段（承运商）只会挤动它后面的池专属字段，共有字段与时间行不受影响。
 *
 * 新增一个筛选条件 = 在 WORKBENCH_FILTER_FIELDS 里加一条描述（含 group）+ 把 id
 * 放进 FIELD_ORDER 的合适位置 + 在需要的池里列出它。
 */

import { selectCarriers } from '@/api/partner/carrier';
import { selectCustomers } from '@/api/partner/customer';
import type { TaskParam } from '@/api/operation/task/model';
import { CARRIER_TYPE, CARRIER_TYPE_OPTIONS } from '../task/status-config';

export type WorkbenchFilterFieldId =
  | 'keyword'
  | 'carrierType'
  | 'carrierId'
  | 'plateNumber'
  | 'originKeyword'
  | 'destinationKeyword'
  | 'customerId'
  /** 复合字段：时间维度下拉 + 日期区间，始终排在末尾 */
  | 'timeRange';

/** 栅格占位（24 栅格制，与《06.列表筛选区布局规范》一致） */
export interface FilterFieldCol {
  lg: number;
  md: number;
  sm: number;
  xs: number;
}

/** 筛选表单的内部数据形态（各字段共用一个扁平对象，未启用的字段保持初始值） */
export interface WorkbenchFilterForm {
  keyword: string;
  carrierType: number | undefined;
  carrierId: number | undefined;
  plateNumber: string;
  originKeyword: string;
  destinationKeyword: string;
  customerId: number | undefined;
}

export interface RemoteOption {
  value: number;
  label: string;
}

/**
 * - `common`：每个阶段池都有，锚定在第一行前列，位置恒定
 * - `pool`：阶段池按需启用，排在共有字段之后
 */
export type WorkbenchFilterFieldGroup = 'common' | 'pool';

export interface WorkbenchFilterField {
  id: WorkbenchFilterFieldId;
  /** FloatingLabel 的 label（自带「请输入 / 请选择」前缀裁剪） */
  label: string;
  kind: 'input' | 'select' | 'remote-select';
  group: WorkbenchFilterFieldGroup;
  col: FilterFieldCol;
  /** kind='select' 的静态选项 */
  options?: ReadonlyArray<{ value: number; label: string }>;
  /** kind='remote-select' 的搜索函数 */
  search?: (keyword: string) => Promise<RemoteOption[]>;
  /** 条件显隐（如「承运商」仅在承运方式=承运商时出现） */
  visibleWhen?: (form: WorkbenchFilterForm) => boolean;
  /** 表单值 → 查询参数；返回空对象表示本次不参与筛选 */
  toParam: (form: WorkbenchFilterForm) => Partial<TaskParam>;
  /** 切换阶段池时是否保留已填值（公共字段保留，池专属字段清空） */
  sticky?: boolean;
}

/**
 * 全部筛选字段共用同一栅格：同一个条件在任何阶段都是同样的宽度。
 * lg 每行 4 个（4×6=24），md 每行 3 个（3×8=24）。
 */
export const FIELD_COL: FilterFieldCol = { lg: 6, md: 8, sm: 12, xs: 24 };

/** 时间维度下拉：与业务字段等宽，和日期区间、按钮凑满末行 */
export const TIME_FIELD_COL: FilterFieldCol = { lg: 6, md: 8, sm: 12, xs: 24 };

/** 日期区间：占两格，日期起止才不挤 */
export const TIME_RANGE_COL: FilterFieldCol = { lg: 12, md: 16, sm: 24, xs: 24 };

/** 搜索 / 重置：lg 下与时间区同行凑满 24，中小屏独占一行 */
export const ACTIONS_COL: FilterFieldCol = { lg: 6, md: 24, sm: 24, xs: 24 };

const trimmed = (v: string): string => (v ?? '').trim();

const searchCarrierOptions = async (
  keyword: string
): Promise<RemoteOption[]> => {
  const list = await selectCarriers(keyword);
  return (list || []).map((c) => ({
    value: c.id,
    label: c.shortName ? `${c.shortName} · ${c.carrierName}` : c.carrierName
  }));
};

const searchCustomerOptions = async (
  keyword: string
): Promise<RemoteOption[]> => {
  const list = await selectCustomers();
  const kw = keyword.trim().toLowerCase();
  return (list || [])
    .filter((c) => {
      if (!kw) return true;
      return [c.customerName, c.shortName, c.customerCode]
        .filter(Boolean)
        .some((t) => String(t).toLowerCase().includes(kw));
    })
    .map((c) => ({
      value: c.id,
      label: c.shortName ? `${c.shortName} · ${c.customerName}` : c.customerName
    }));
};

export const WORKBENCH_FILTER_FIELDS: Record<
  Exclude<WorkbenchFilterFieldId, 'timeRange'>,
  WorkbenchFilterField
> = {
  keyword: {
    id: 'keyword',
    label: '请输入任务单号 / 计划号',
    kind: 'input',
    group: 'common',
    col: FIELD_COL,
    sticky: true,
    toParam: (f) => (trimmed(f.keyword) ? { keyword: trimmed(f.keyword) } : {})
  },
  originKeyword: {
    id: 'originKeyword',
    label: '请输入出发地',
    kind: 'input',
    group: 'common',
    col: FIELD_COL,
    sticky: true,
    toParam: (f) =>
      trimmed(f.originKeyword) ? { originKeyword: trimmed(f.originKeyword) } : {}
  },
  destinationKeyword: {
    id: 'destinationKeyword',
    label: '请输入目的地',
    kind: 'input',
    group: 'common',
    col: FIELD_COL,
    sticky: true,
    toParam: (f) =>
      trimmed(f.destinationKeyword)
        ? { destinationKeyword: trimmed(f.destinationKeyword) }
        : {}
  },
  carrierType: {
    id: 'carrierType',
    label: '请选择承运方式',
    kind: 'select',
    group: 'pool',
    col: FIELD_COL,
    options: CARRIER_TYPE_OPTIONS.map((o) => ({
      value: o.value,
      label: o.label
    })),
    toParam: (f) => (f.carrierType != null ? { carrierType: f.carrierType } : {})
  },
  carrierId: {
    id: 'carrierId',
    label: '请选择承运商',
    kind: 'remote-select',
    group: 'pool',
    col: FIELD_COL,
    search: searchCarrierOptions,
    visibleWhen: (f) => f.carrierType === CARRIER_TYPE.CARRIER,
    toParam: (f) =>
      f.carrierType === CARRIER_TYPE.CARRIER && f.carrierId != null
        ? { carrierId: f.carrierId }
        : {}
  },
  plateNumber: {
    id: 'plateNumber',
    label: '请输入车牌号',
    kind: 'input',
    group: 'pool',
    col: FIELD_COL,
    toParam: (f) =>
      trimmed(f.plateNumber) ? { plateNumber: trimmed(f.plateNumber) } : {}
  },
  customerId: {
    id: 'customerId',
    label: '请选择客户',
    kind: 'remote-select',
    group: 'pool',
    col: FIELD_COL,
    search: searchCustomerOptions,
    toParam: (f) => (f.customerId != null ? { customerId: f.customerId } : {})
  }
};

/**
 * 渲染次序（全局唯一）。共有字段在前锚定，池专属字段按此表顺延，
 * 池里 `filterFields` 的书写顺序不参与排序。
 */
const FIELD_ORDER: Exclude<WorkbenchFilterFieldId, 'timeRange'>[] = [
  'keyword',
  'originKeyword',
  'destinationKeyword',
  'carrierType',
  'carrierId',
  'plateNumber',
  'customerId'
];

export const buildFilterFormDefaults = (): WorkbenchFilterForm => ({
  keyword: '',
  carrierType: void 0,
  carrierId: void 0,
  plateNumber: '',
  originKeyword: '',
  destinationKeyword: '',
  customerId: void 0
});

/** 池专属字段在切池时清空，公共字段（单号、线路）保留 */
export const resetNonStickyFields = (
  form: WorkbenchFilterForm,
  keepIds: WorkbenchFilterFieldId[]
): WorkbenchFilterForm => {
  const defaults = buildFilterFormDefaults();
  const next = { ...defaults };
  for (const id of keepIds) {
    if (id === 'timeRange') continue;
    const field = WORKBENCH_FILTER_FIELDS[id];
    if (field?.sticky) {
      (next as Record<string, unknown>)[id] = (
        form as unknown as Record<string, unknown>
      )[id];
    }
  }
  return next;
};

export const getFilterField = (
  id: WorkbenchFilterFieldId
): WorkbenchFilterField | undefined =>
  id === 'timeRange'
    ? undefined
    : WORKBENCH_FILTER_FIELDS[id as Exclude<WorkbenchFilterFieldId, 'timeRange'>];

/**
 * 本池要渲染的字段，按全局槽位次序输出（共有字段在前，池专属顺延）。
 *
 * `timeRange` 不在此列 —— 它由模板固定渲染在末行。
 */
export const resolveVisibleFilterFields = (
  poolFields: WorkbenchFilterFieldId[],
  form: WorkbenchFilterForm
): WorkbenchFilterField[] => {
  const enabled = new Set(poolFields);
  return FIELD_ORDER.filter((id) => enabled.has(id))
    .map((id) => WORKBENCH_FILTER_FIELDS[id])
    .filter((f) => (f.visibleWhen ? f.visibleWhen(form) : true));
};
