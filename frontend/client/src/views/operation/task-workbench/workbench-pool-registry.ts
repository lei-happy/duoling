/**
 * 调度工作台 — 按「状态池」注册列表形态
 *
 * 每个池独立配置：筛选用 status、行内主动作、列顺序与表头文案、默认排序、是否允许批量主动作。
 * 新增状态或改表头时只改本文件 + task-pool 中对应 slot（若有新列类型）。
 */

import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
import type { TaskActionKey } from '../task/task-actions';

/** 与 task-pool 模板中 #slot 一一对应 */
export type WorkbenchColumnId =
  | 'selection'
  | 'taskNo'
  | 'carrierType'
  /** 承运商 / 司机姓名（按 carrierType 分支展示） */
  | 'carrierName'
  /** 承运车辆 = 车牌（自有车 / 社会运力 / 承运商代填） */
  | 'plateNumber'
  | 'route'
  | 'carrierResource'
  | 'waybillCount'
  | 'totalQuantity'
  | 'plannedLoadTime'
  | 'plannedArriveTime'
  | 'actualLoadTime'
  | 'createdAt'
  | 'status'
  | 'action';

export type WorkbenchToolbarPreset = 'default' | 'pending-dispatch';

export interface WorkbenchPool {
  /** 与 KPI 卡片、路由缓存 key 一致 */
  key: string;
  /** 展示用（可与卡片文案对齐） */
  label: string;
  status: number | number[];
  primaryActionKey: TaskActionKey | null;
  columns: WorkbenchColumnId[];
  /** 表头覆盖（未写的用默认文案） */
  columnLabels?: Partial<Record<WorkbenchColumnId, string>>;
  defaultSort: { prop: string; order: 'ascending' | 'descending' };
  /** 是否展示「批量 + 主动作」工具栏按钮，默认 true */
  allowBatchPrimary?: boolean;
  /** 操作列宽度（行内链接数量不同） */
  actionColumnWidth?: number;
  /** 台数是否可点，打开与运单列表一致的商品车明细（拉取挂接明细） */
  quantityOpenCargoDetail?: boolean;
  /** 工具栏筛选布局：待派车为增强筛选项 */
  toolbarPreset?: WorkbenchToolbarPreset;
}

const COL: Record<WorkbenchColumnId, string> = {
  selection: '',
  taskNo: '任务单号',
  carrierType: '承运方式',
  carrierName: '承运商 / 司机',
  plateNumber: '承运车辆',
  route: '运输线路',
  carrierResource: '司机 / 车牌 / 承运商',
  waybillCount: '运单数',
  totalQuantity: '台数',
  plannedLoadTime: '计划装车',
  plannedArriveTime: '计划到货',
  actualLoadTime: '实际装车',
  createdAt: '制单时间',
  status: '状态',
  action: '操作'
};

export const WORKBENCH_POOLS: WorkbenchPool[] = [
  {
    key: 'pending-assign',
    label: '待分配',
    status: -1,
    primaryActionKey: 'assign-carrier',
    allowBatchPrimary: false,
    quantityOpenCargoDetail: true,
    toolbarPreset: 'pending-dispatch',
    actionColumnWidth: 200,
    columns: [
      'taskNo',
      'route',
      'waybillCount',
      'totalQuantity',
      'createdAt',
      'plannedLoadTime',
      'action'
    ],
    columnLabels: {
      plannedLoadTime: '计划装车（分配/派车参考）'
    },
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'pending-dispatch',
    label: '待派车',
    status: 0,
    primaryActionKey: 'dispatch',
    allowBatchPrimary: false,
    quantityOpenCargoDetail: true,
    toolbarPreset: 'pending-dispatch',
    actionColumnWidth: 200,
    columns: [
      'taskNo',
      'carrierType',
      'carrierName',
      'route',
      'waybillCount',
      'totalQuantity',
      'createdAt',
      'plannedLoadTime',
      'action'
    ],
    columnLabels: {
      carrierName: '承运方',
      plannedLoadTime: '计划装车（派车截止参考）'
    },
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'pending-load',
    label: '待装车',
    status: 1,
    primaryActionKey: 'confirm-load',
    allowBatchPrimary: false,
    actionColumnWidth: 240,
    toolbarPreset: 'pending-dispatch',
    columns: [
      'taskNo',
      'carrierType',
      'carrierName',
      'plateNumber',
      'route',
      'totalQuantity',
      'plannedLoadTime',
      'status',
      'action'
    ],
    columnLabels: {
      carrierName: '承运商',
      plateNumber: '承运车辆',
      plannedLoadTime: '计划装车'
    },
    defaultSort: { prop: 'plannedLoadTime', order: 'ascending' }
  },
  {
    key: 'on-way',
    label: '在途中',
    status: [2, 3],
    primaryActionKey: 'confirm-arrive',
    allowBatchPrimary: false,
    actionColumnWidth: 280,
    columns: [
      'taskNo',
      'carrierType',
      'route',
      'carrierResource',
      'totalQuantity',
      'plannedLoadTime',
      'plannedArriveTime',
      'status',
      'action'
    ],
    columnLabels: {
      plannedLoadTime: '计划装车',
      plannedArriveTime: '计划到货（到达参考）'
    },
    defaultSort: { prop: 'plannedArriveTime', order: 'ascending' }
  },
  {
    key: 'pending-sign',
    label: '待签收',
    status: 4,
    primaryActionKey: 'confirm-sign',
    actionColumnWidth: 240,
    columns: [
      'selection',
      'taskNo',
      'carrierType',
      'route',
      'carrierResource',
      'totalQuantity',
      'plannedArriveTime',
      'actualLoadTime',
      'status',
      'action'
    ],
    columnLabels: {
      plannedArriveTime: '计划到货',
      actualLoadTime: '实际装车'
    },
    defaultSort: { prop: 'plannedArriveTime', order: 'ascending' }
  }
];

export const getWorkbenchPool = (key: string): WorkbenchPool | undefined =>
  WORKBENCH_POOLS.find((p) => p.key === key);

export function buildWorkbenchTableColumns(pool: WorkbenchPool): Columns {
  const L = { ...COL, ...pool.columnLabels };
  const actionW = pool.actionColumnWidth ?? 240;
  const cols: Columns = [];

  for (const id of pool.columns) {
    switch (id) {
      case 'selection':
        cols.push({ type: 'selection', width: 48, align: 'center' });
        break;
      case 'taskNo':
        cols.push({ prop: 'taskNo', label: L.taskNo, minWidth: 160 });
        break;
      case 'carrierType':
        cols.push({
          prop: 'carrierType',
          label: L.carrierType,
          width: 96,
          align: 'center',
          slot: 'carrierType'
        });
        break;
      case 'carrierName':
        cols.push({
          columnKey: 'carrierName',
          label: L.carrierName,
          minWidth: 160,
          slot: 'carrierName'
        });
        break;
      case 'plateNumber':
        cols.push({
          prop: 'plateNumber',
          label: L.plateNumber,
          width: 130,
          align: 'center',
          slot: 'plateNumber'
        });
        break;
      case 'route':
        cols.push({
          columnKey: 'route',
          label: L.route,
          minWidth: 240,
          slot: 'route'
        });
        break;
      case 'carrierResource':
        cols.push({
          columnKey: 'carrierResource',
          label: L.carrierResource,
          minWidth: 180,
          slot: 'carrierResource'
        });
        break;
      case 'waybillCount':
        cols.push({
          prop: 'waybillCount',
          label: L.waybillCount,
          width: 88,
          align: 'center',
          slot: 'waybillCount'
        });
        break;
      case 'totalQuantity':
        cols.push({
          prop: 'totalQuantity',
          label: L.totalQuantity,
          width: pool.quantityOpenCargoDetail ? 88 : 70,
          align: 'center',
          slot: 'totalQuantity'
        });
        break;
      case 'plannedLoadTime':
        cols.push({
          prop: 'plannedLoadTime',
          label: L.plannedLoadTime,
          width: 168,
          align: 'center',
          slot: 'plannedLoadTime'
        });
        break;
      case 'plannedArriveTime':
        cols.push({
          prop: 'plannedArriveTime',
          label: L.plannedArriveTime,
          width: 168,
          align: 'center',
          slot: 'plannedArriveTime'
        });
        break;
      case 'actualLoadTime':
        cols.push({
          prop: 'actualLoadTime',
          label: L.actualLoadTime,
          width: 168,
          align: 'center',
          slot: 'actualLoadTime'
        });
        break;
      case 'createdAt':
        cols.push({
          prop: 'createdAt',
          label: L.createdAt,
          width: 168,
          align: 'center',
          slot: 'createdAt'
        });
        break;
      case 'status':
        cols.push({
          prop: 'status',
          label: L.status,
          width: 110,
          align: 'center',
          slot: 'status'
        });
        break;
      case 'action':
        cols.push({
          columnKey: 'action',
          label: L.action,
          width: actionW,
          align: 'center',
          fixed: 'right',
          slot: 'action'
        });
        break;
      default:
        break;
    }
  }
  return cols;
}
