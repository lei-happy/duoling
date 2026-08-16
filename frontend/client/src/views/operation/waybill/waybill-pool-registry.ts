/**
 * 计划工作台 — 按「状态池」注册列表形态
 *
 * 每个池独立配置：筛选项、行内动作、列顺序、默认排序、是否允许批量主动作。
 * 新增状态或改表头时只改本文件 + waybill-pool 中对应 slot（若有新列类型）。
 *
 * 状态空间参考 backend WaybillStateMachine + 实际落库行为：
 *   0 待确认（新建即落 0，需要运营点击「确认」推进到 1，UI 上独立出卡）
 *   1 待调度 / 2 调度中 / 3 运输中 / 4 待交车 / 5 已交车 / 6 已回单 / 7 已关闭
 *
 * 4 待交车 / 5 已交车 与 task.status 解耦，强调"客户视角的票据流转"：
 *   - 4 待交车 = 全量货物已到达，等交付客户
 *   - 5 已交车 = 全量货物已交车，计划对客户层面已闭环
 *   - 6 已回单 = 交车回单返还货主（人工动作，回单台账在「回单签收」页操作）
 *   - 7 已关闭 = 终态（原 6 后移）
 */

import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';

/** 与 waybill-pool-filter 模板中渲染分支一一对应 */
export type WaybillFilterField =
  | 'keyword'
  | 'customer'
  | 'origin'
  | 'destination'
  | 'vehicle'
  | 'vin'
  | 'createdRange';

/** 工作台统一筛选项（各状态池字段的并集，避免切换阶段时筛选栏重建/丢失条件） */
export const UNIFIED_WAYBILL_FILTER_FIELDS: WaybillFilterField[] = [
  'keyword',
  'customer',
  'origin',
  'destination',
  'vehicle',
  'vin',
  'createdRange'
];

/** 计划 status → 工作台 pool key（用于按计划号跨状态搜索后自动切换阶段卡） */
export const WAYBILL_STATUS_TO_POOL_KEY: Record<number, string> = {
  0: 'pending-confirm',
  1: 'pending-dispatch',
  2: 'scheduling',
  3: 'in-transit',
  4: 'delivered',
  5: 'completed',
  6: 'receipted',
  7: 'closed'
};

/** 与 waybill-pool 模板中 #slot 一一对应 */
export type WaybillColumnId =
  | 'selection'
  | 'waybillNo'
  | 'customerName'
  | 'origin'
  | 'destination'
  | 'vehicleInfo'
  | 'quantity'
  | 'allocatedQuantity'
  | 'freightAmount'
  | 'calcStatus'
  | 'isLocked'
  | 'status'
  | 'createdBy'
  | 'createdAt'
  | 'action';

/**
 * 行内操作 key（与 waybill-pool 中 actionItems 内回调一一对应）
 *
 * - `edit` 修改、`confirm` 确认（仅 1 待调度可推进到 2）
 * - `detail` 详情、`freight-detail` 计算明细
 * - `recalc` 重算、`lock` 锁定、`unlock` 解锁
 * - `remove` 删除
 */
export type WaybillRowActionKey =
  | 'edit'
  | 'confirm'
  | 'detail'
  | 'freight-detail'
  | 'recalc'
  | 'lock'
  | 'unlock'
  | 'remove';

export interface WaybillPool {
  /** 与卡片 key、缓存 key 对齐 */
  key: string;
  /** 展示用，与卡片标题一致 */
  label: string;
  /** 1~6 单值，对应 WaybillStateMachine */
  status: number;
  /** 仅渲染列出的筛选项 */
  filterFields: WaybillFilterField[];
  /** 列顺序由数组决定 */
  columns: WaybillColumnId[];
  /** 表头覆盖（未写的用默认文案） */
  columnLabels?: Partial<Record<WaybillColumnId, string>>;
  /**
   * 行内动作顺序（对齐菜单按钮 sort_order + 业务优先级）。
   * 组装规则见开发手册「17.列表操作列按钮规范」：过滤后 ≤2 平铺，≥3 为首项 + 更多。
   */
  rowActions: WaybillRowActionKey[];
  defaultSort: { prop: string; order: 'ascending' | 'descending' };
  /** 是否展示「批量确认」工具栏按钮（仅 1 待调度=true） */
  allowBatchConfirm?: boolean;
  /**
   * 操作列 minWidth 覆盖值（一般不必填）。
   * 默认按 rowActions 估算外显文案宽度，见 `resolveActionColumnMinWidth`。
   */
  actionColumnWidth?: number;
}

/** 与 waybill-pool buildAction 文案对齐，供操作列宽度估算 */
const ACTION_TITLE: Record<WaybillRowActionKey, string> = {
  edit: '修改',
  confirm: '确认',
  detail: '详情',
  'freight-detail': '计算明细',
  recalc: '重算',
  lock: '锁定',
  unlock: '解锁',
  remove: '删除'
};

/** 带图标的 link 占用宽度（偏保守，避免裁切「更多」箭头） */
function estimateActionLinkWidth(title: string): number {
  return 20 + title.length * 14 + 12;
}

/**
 * 操作列 minWidth：按「过滤前最坏外显」估算（≤2 平铺 / ≥3 首项+更多）。
 * fixed 右列无法真正内容自适应，须给足下限。
 */
export function resolveActionColumnMinWidth(pool: WaybillPool): number {
  if (pool.actionColumnWidth != null) return pool.actionColumnWidth;
  const keys = pool.rowActions;
  const pad = 28;
  const divider = 17;
  const moreW = 68; // 「更多」+ 下拉箭头
  if (keys.length === 0) return 72;
  if (keys.length === 1) {
    return Math.max(80, estimateActionLinkWidth(ACTION_TITLE[keys[0]!]) + pad);
  }
  if (keys.length === 2) {
    return (
      estimateActionLinkWidth(ACTION_TITLE[keys[0]!]) +
      divider +
      estimateActionLinkWidth(ACTION_TITLE[keys[1]!]) +
      pad
    );
  }
  return (
    estimateActionLinkWidth(ACTION_TITLE[keys[0]!]) + divider + moreW + pad
  );
}

const COL: Record<WaybillColumnId, string> = {
  selection: '',
  waybillNo: '计划编号',
  customerName: '客户名称',
  origin: '出发地',
  destination: '目的地',
  vehicleInfo: '品牌/车型',
  quantity: '台数',
  allocatedQuantity: '已调度',
  freightAmount: '运费金额',
  calcStatus: '计算状态',
  isLocked: '锁定',
  status: '状态',
  createdBy: '创建人',
  createdAt: '创建时间',
  action: '操作'
};

export const WAYBILL_POOLS: WaybillPool[] = [
  {
    key: 'pending-confirm',
    label: '待确认',
    status: 0,
    filterFields: [
      'keyword',
      'customer',
      'origin',
      'destination',
      'createdRange'
    ],
    columns: [
      'selection',
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'freightAmount',
      'calcStatus',
      'isLocked',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    // edit / remove 对齐菜单 business:waybill:edit|delete；其余暂无独立权限点
    rowActions: [
      'edit',
      'confirm',
      'detail',
      'freight-detail',
      'recalc',
      'lock',
      'unlock',
      'remove'
    ],
    defaultSort: { prop: 'createdAt', order: 'descending' },
    allowBatchConfirm: true
  },
  {
    key: 'pending-dispatch',
    label: '待调度',
    status: 1,
    filterFields: [
      'keyword',
      'customer',
      'origin',
      'destination',
      'createdRange'
    ],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'allocatedQuantity',
      'freightAmount',
      'calcStatus',
      'isLocked',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    // edit 对齐菜单 business:waybill:edit；remove 靠后对齐 delete
    rowActions: [
      'edit',
      'detail',
      'freight-detail',
      'recalc',
      'lock',
      'unlock',
      'remove'
    ],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'scheduling',
    label: '调度中',
    status: 2,
    filterFields: ['keyword', 'customer', 'origin', 'destination'],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'allocatedQuantity',
      'freightAmount',
      'calcStatus',
      'isLocked',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    // 无编辑：detail 靠前，保证外显「详情 + 更多」
    rowActions: ['detail', 'freight-detail', 'recalc', 'lock', 'unlock'],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'in-transit',
    label: '运输中',
    status: 3,
    filterFields: ['keyword', 'customer', 'origin', 'destination'],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'allocatedQuantity',
      'freightAmount',
      'calcStatus',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    rowActions: ['detail', 'freight-detail'],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'delivered',
    label: '待交车',
    status: 4,
    filterFields: [
      'keyword',
      'customer',
      'origin',
      'destination',
      'createdRange'
    ],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'freightAmount',
      'calcStatus',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    rowActions: ['detail', 'freight-detail'],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'completed',
    label: '已交车',
    status: 5,
    filterFields: [
      'keyword',
      'customer',
      'origin',
      'destination',
      'createdRange'
    ],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'freightAmount',
      'calcStatus',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    rowActions: ['detail', 'freight-detail'],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'receipted',
    label: '已回单',
    status: 6,
    filterFields: [
      'keyword',
      'customer',
      'origin',
      'destination',
      'createdRange'
    ],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'vehicleInfo',
      'quantity',
      'freightAmount',
      'calcStatus',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    rowActions: ['detail', 'freight-detail'],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'closed',
    label: '已关闭',
    status: 7,
    filterFields: ['keyword', 'customer', 'createdRange'],
    columns: [
      'waybillNo',
      'customerName',
      'origin',
      'destination',
      'quantity',
      'status',
      'createdBy',
      'createdAt',
      'action'
    ],
    rowActions: ['detail'],
    defaultSort: { prop: 'createdAt', order: 'descending' }
  }
];

export const getWaybillPool = (key: string): WaybillPool | undefined =>
  WAYBILL_POOLS.find((p) => p.key === key);

/**
 * 把 pool.columns 翻译成 ele-pro-table 的 Columns。
 *
 * 注意：本函数只产出"通用结构"，所有单元格渲染仍交由 waybill-pool.vue 的 slot 完成，
 * 这样新增/修改列的视觉只在一处维护。
 */
export function buildWaybillTableColumns(pool: WaybillPool): Columns {
  const L = { ...COL, ...pool.columnLabels };
  const actionMinW = resolveActionColumnMinWidth(pool);
  // ele-admin-plus 的 Column 类型对 type/prop/columnKey 等运行时合法字段未导出，
  // 临时用 Record<string, unknown>[] 承载（同 task-workbench/workbench-pool-registry.ts 现状）。
  const cols: Record<string, unknown>[] = [];

  for (const id of pool.columns) {
    switch (id) {
      case 'selection':
        cols.push({
          type: 'selection',
          width: 48,
          align: 'center',
          resizable: false
        });
        break;
      case 'waybillNo':
        cols.push({
          prop: 'waybillNo',
          label: L.waybillNo,
          minWidth: 168,
          slot: 'waybillNo'
        });
        break;
      case 'customerName':
        cols.push({
          prop: 'customerName',
          label: L.customerName,
          minWidth: 210,
          slot: 'customerName'
        });
        break;
      case 'origin':
        cols.push({
          prop: 'origin',
          label: L.origin,
          minWidth: 200,
          slot: 'origin'
        });
        break;
      case 'destination':
        cols.push({
          prop: 'destination',
          label: L.destination,
          minWidth: 200,
          slot: 'destination'
        });
        break;
      case 'vehicleInfo':
        cols.push({
          columnKey: 'vehicleInfo',
          label: L.vehicleInfo,
          minWidth: 120,
          slot: 'vehicleInfo'
        });
        break;
      case 'quantity':
        cols.push({
          columnKey: 'quantity',
          prop: 'quantity',
          label: L.quantity,
          width: 88,
          align: 'center',
          slot: 'quantity'
        });
        break;
      case 'allocatedQuantity':
        cols.push({
          columnKey: 'allocatedQuantity',
          prop: 'allocatedQuantity',
          label: L.allocatedQuantity,
          width: 96,
          align: 'center',
          slot: 'allocatedQuantity'
        });
        break;
      case 'freightAmount':
        cols.push({
          prop: 'freightAmount',
          label: L.freightAmount,
          minWidth: 100,
          align: 'right'
        });
        break;
      case 'calcStatus':
        cols.push({
          prop: 'calcStatus',
          label: L.calcStatus,
          width: 100,
          align: 'center',
          slot: 'calcStatus'
        });
        break;
      case 'isLocked':
        cols.push({
          prop: 'isLocked',
          label: L.isLocked,
          width: 64,
          align: 'center',
          slot: 'isLocked'
        });
        break;
      case 'status':
        cols.push({
          prop: 'status',
          label: L.status,
          width: 90,
          align: 'center',
          slot: 'status'
        });
        break;
      case 'createdBy':
        cols.push({
          prop: 'createdByName',
          label: L.createdBy,
          width: 96,
          align: 'center',
          slot: 'createdBy'
        });
        break;
      case 'createdAt':
        cols.push({
          prop: 'createdAt',
          label: L.createdAt,
          width: 170,
          align: 'center',
          slot: 'createdAt'
        });
        break;
      case 'action':
        cols.push({
          columnKey: 'action',
          label: L.action,
          // fixed 右列无法内容自适应：用估算 minWidth，禁止用过小的固定 width
          minWidth: actionMinW,
          width: actionMinW,
          align: 'center',
          slot: 'action',
          fixed: 'right',
          resizable: false,
          hideInPrint: true,
          hideInExport: true
        });
        break;
      default:
        break;
    }
  }
  return cols as Columns;
}
