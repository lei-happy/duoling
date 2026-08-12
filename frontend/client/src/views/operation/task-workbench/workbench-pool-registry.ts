/**
 * 调度工作台 — 按「状态池」注册列表形态
 *
 * 每个池独立配置：筛选用 status、筛选字段、行内主动作、列顺序与表头文案、默认排序、
 * 工具栏形态。
 *
 * **预警不在这里判定**：所有阈值、级别与命中规则都由后端 `biz_task_alert` 产出，
 * 列表行只读 `row.alertLevel`。前端曾经自带一套 `loadOverdue` / `stageAlertHours`
 * 判定，结果是「列表标红的行，卡片可能算在常里」——两套口径必然对不上，已移除。
 *
 * task-pool.vue 只负责渲染，不再包含任何 `if (poolKey === 'xxx')` 分支；
 * 新增或调整一个状态阶段，只需要改本文件（除非引入了全新的列类型）。
 */

import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
import type { TaskAlertLevelFilter, TaskParam } from '@/api/operation/task/model';
import type { TaskActionKey } from '../task/task-actions';
import { resolveTaskListActionColumnMinWidth } from '../task/task-actions';
import { TASK_STATUS } from '../task/status-config';
import type { WorkbenchFilterFieldId } from './workbench-filter-registry';

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
  /** 本阶段已停留时长（来自 stageEnteredAt） */
  | 'stageDuration'
  /** 预警超时时长（来自后端 alertOverdueMinutes） */
  | 'alertOverdue'
  | 'status'
  | 'action';

/** KPI 卡片的「全部 / 常 / 关注 / 严重」子集 */
export type WorkbenchListSubset = 'all' | 'normal' | 'warn' | 'critical';

/** 子集 → 列表查询参数。六个阶段口径一致，不需要逐池配置。 */
export const buildSubsetQuery = (
  subset: Exclude<WorkbenchListSubset, 'all'>
): Partial<TaskParam> => ({ alertLevel: subset as TaskAlertLevelFilter });

/** 任务 status → 工作台 pool key（用于按单号跨状态搜索后自动切换阶段卡） */
export const TASK_STATUS_TO_POOL_KEY: Record<number, string> = {
  [TASK_STATUS.PENDING_ASSIGN]: 'pending-assign',
  [TASK_STATUS.PENDING_DISPATCH]: 'pending-dispatch',
  [TASK_STATUS.DISPATCHED]: 'pending-load',
  [TASK_STATUS.LOADED]: 'pending-depart',
  [TASK_STATUS.ON_WAY]: 'on-way',
  [TASK_STATUS.ARRIVED]: 'pending-deliver'
};

/**
 * 历史 pool key 兼容映射。
 *
 * 「在途中」原本合并了 已装车(2) + 在途(3)，现已拆成「待发车 / 在途」两个池；
 * 旧外链 `?tab=on-way` 落到在途，`?tab=pending-sign` 落到待交车。
 */
const LEGACY_POOL_KEY_ALIAS: Record<string, string> = {
  'pending-sign': 'pending-deliver'
};

export const normalizeWorkbenchPoolKey = (key?: string): string | undefined =>
  key ? (LEGACY_POOL_KEY_ALIAS[key] ?? key) : undefined;

export const resolveWorkbenchPoolKey = (status?: number): string | undefined =>
  status == null ? undefined : TASK_STATUS_TO_POOL_KEY[status];

export interface WorkbenchPool {
  /** 与 KPI 卡片、路由缓存 key 一致 */
  key: string;
  /** 展示用（待办视角：待分配 / 待派车 / …） */
  label: string;
  /** 本池对应的任务状态（拆池后恒为单值，服务端可直接分页排序） */
  status: number;
  primaryActionKey: TaskActionKey | null;
  /**
   * 本池启用哪些筛选字段。**顺序不生效** —— 渲染次序由 workbench-filter-registry
   * 的全局槽位表决定，保证同一字段在所有阶段处于同一位置。
   */
  filterFields: WorkbenchFilterFieldId[];
  columns: WorkbenchColumnId[];
  /** 表头覆盖（未写的用默认文案；只写短词，解释放 `columnTips`） */
  columnLabels?: Partial<Record<WorkbenchColumnId, string>>;
  /** 表头问号提示覆盖（未写的用 `COL_TIP` 默认文案） */
  columnTips?: Partial<Record<WorkbenchColumnId, string>>;
  defaultSort: { prop: string; order: 'ascending' | 'descending' };
  toolbar?: {
    /** 是否展示「批量 + 主动作」按钮，默认 false */
    batchPrimary?: boolean;
    /** 是否展示工具栏「刷新」按钮，默认 false（筛选区已有搜索/重置） */
    refresh?: boolean;
  };
  /** 操作列宽度覆盖（一般不填，默认按「首项 + 更多」估算，见 §1.6） */
  actionColumnWidth?: number;
  /** 台数是否可点，打开与计划列表一致的商品车明细（拉取挂接明细） */
  quantityOpenCargoDetail?: boolean;
}

/**
 * 表头文案：一律用「短词 + 表头问号提示」，**不允许**在 label 里写括号解释，
 * 括号会把表头撑长并被 ele-pro-table 截断成「计划到货（到达参...」。
 */
const COL: Record<WorkbenchColumnId, string> = {
  selection: '',
  taskNo: '任务单号',
  carrierType: '承运方式',
  carrierName: '承运方',
  plateNumber: '车牌号',
  route: '运输线路',
  carrierResource: '承运运力',
  waybillCount: '关联计划',
  totalQuantity: '台数',
  plannedLoadTime: '计划装车',
  plannedArriveTime: '计划到货',
  actualLoadTime: '实际装车',
  createdAt: '制单时间',
  stageDuration: '停留时长',
  alertOverdue: '超时时长',
  status: '状态',
  action: '操作'
};

/** 表头问号提示的默认文案（池内可用 `columnTips` 覆盖成本阶段的说法） */
const COL_TIP: Partial<Record<WorkbenchColumnId, string>> = {
  carrierType: '自有车、社会运力或承运商',
  carrierName: '自有车显示司机，承运商显示承运商名称',
  carrierResource: '自有车、社会运力显示司机与车牌；承运商显示承运商名称',
  waybillCount: '本任务关联的计划单数量',
  totalQuantity: '本任务承运的商品车总台数',
  plannedLoadTime: '计划开始装车的时间，已触发预警会标色',
  plannedArriveTime: '计划送达目的地的时间，已触发预警会标色',
  actualLoadTime: '实际完成装车的时间',
  stageDuration: '进入当前阶段至今的时长',
  alertOverdue: '已超过应完成时间多久，可排序，优先处理拖得最久的'
};

/**
 * 列 id → 表格里的字段名（prop / columnKey）。
 * 仅 `stageDuration` 与 id 不同（按进入阶段的时间排序），其余同名。
 */
const COL_FIELD: Partial<Record<WorkbenchColumnId, string>> = {
  stageDuration: 'stageEnteredAt',
  alertOverdue: 'alertOverdueMinutes'
};

/**
 * 操作列 minWidth：与任务单台账共用同一估算口径（开发手册 §1.6），
 * 保证「分配承运 + 更多」这类最坏外显不被裁切。
 */
export function resolveActionColumnMinWidth(pool: WorkbenchPool): number {
  return pool.actionColumnWidth ?? resolveTaskListActionColumnMinWidth();
}

/** 供 task-pool 表头 slot 反查提示：字段名 → 提示文案 */
export function buildColumnTipMap(pool: WorkbenchPool): Record<string, string> {
  const tips = { ...COL_TIP, ...pool.columnTips };
  const map: Record<string, string> = {};
  for (const id of pool.columns) {
    const tip = tips[id];
    if (tip) map[COL_FIELD[id] ?? id] = tip;
  }
  return map;
}

export const WORKBENCH_POOLS: WorkbenchPool[] = [
  {
    key: 'pending-assign',
    label: '待分配',
    status: TASK_STATUS.PENDING_ASSIGN,
    primaryActionKey: 'assign-carrier',
    filterFields: [
      'keyword',
      'originKeyword',
      'destinationKeyword',
      'customerId',
      'timeRange'
    ],
    toolbar: { batchPrimary: true },
    quantityOpenCargoDetail: true,
    columns: [
      'selection',
      'taskNo',
      'route',
      'waybillCount',
      'totalQuantity',
      'plannedLoadTime',
      'stageDuration',
      'alertOverdue',
      'action'
    ],
    columnTips: {
      plannedLoadTime: '计划开始装车的时间，越近的越该优先分配运力'
    },
    defaultSort: { prop: 'createdAt', order: 'descending' }
  },
  {
    key: 'pending-dispatch',
    label: '待派车',
    status: TASK_STATUS.PENDING_DISPATCH,
    primaryActionKey: 'dispatch',
    filterFields: [
      'keyword',
      'originKeyword',
      'destinationKeyword',
      'carrierType',
      'carrierId',
      'timeRange'
    ],
    quantityOpenCargoDetail: true,
    columns: [
      'taskNo',
      'carrierType',
      'carrierName',
      'route',
      'waybillCount',
      'totalQuantity',
      'plannedLoadTime',
      'stageDuration',
      'alertOverdue',
      'action'
    ],
    columnTips: {
      plannedLoadTime: '计划开始装车的时间，需要在这之前派好车'
    },
    defaultSort: { prop: 'plannedLoadTime', order: 'ascending' }
  },
  {
    key: 'pending-load',
    label: '待装车',
    status: TASK_STATUS.DISPATCHED,
    primaryActionKey: 'confirm-load',
    filterFields: [
      'keyword',
      'originKeyword',
      'destinationKeyword',
      'carrierType',
      'carrierId',
      'plateNumber',
      'timeRange'
    ],
    columns: [
      'taskNo',
      'carrierType',
      'carrierName',
      'plateNumber',
      'route',
      'totalQuantity',
      'plannedLoadTime',
      'stageDuration',
      'alertOverdue',
      'status',
      'action'
    ],
    columnTips: {
      plannedLoadTime: '计划开始装车的时间，需要在这之前完成装车'
    },
    defaultSort: { prop: 'plannedLoadTime', order: 'ascending' }
  },
  {
    key: 'pending-depart',
    label: '待发车',
    status: TASK_STATUS.LOADED,
    primaryActionKey: 'depart',
    filterFields: [
      'keyword',
      'originKeyword',
      'destinationKeyword',
      'carrierType',
      'plateNumber',
      'timeRange'
    ],
    toolbar: { batchPrimary: true },
    columns: [
      'selection',
      'taskNo',
      'carrierType',
      'route',
      'carrierResource',
      'totalQuantity',
      'actualLoadTime',
      'plannedArriveTime',
      'stageDuration',
      'alertOverdue',
      'action'
    ],
    columnTips: {
      actualLoadTime: '实际完成装车的时间，装完越久没发车越该催'
    },
    defaultSort: { prop: 'actualLoadTime', order: 'ascending' }
  },
  {
    key: 'on-way',
    label: '在途',
    status: TASK_STATUS.ON_WAY,
    primaryActionKey: 'confirm-arrive',
    filterFields: [
      'keyword',
      'originKeyword',
      'destinationKeyword',
      'carrierType',
      'plateNumber',
      'timeRange'
    ],
    columns: [
      'taskNo',
      'carrierType',
      'route',
      'carrierResource',
      'totalQuantity',
      'actualLoadTime',
      'plannedArriveTime',
      'stageDuration',
      'alertOverdue',
      'status',
      'action'
    ],
    columnTips: {
      plannedArriveTime: '计划送达目的地的时间，超期未到达会标色'
    },
    defaultSort: { prop: 'plannedArriveTime', order: 'ascending' }
  },
  {
    key: 'pending-deliver',
    label: '待交车',
    status: TASK_STATUS.ARRIVED,
    primaryActionKey: 'confirm-sign',
    filterFields: [
      'keyword',
      'originKeyword',
      'destinationKeyword',
      'carrierType',
      'carrierId',
      'customerId',
      'timeRange'
    ],
    toolbar: { batchPrimary: true },
    columns: [
      'selection',
      'taskNo',
      'carrierType',
      'route',
      'carrierResource',
      'totalQuantity',
      'plannedArriveTime',
      'actualLoadTime',
      'stageDuration',
      'alertOverdue',
      'action'
    ],
    columnTips: {
      plannedArriveTime: '计划送达目的地的时间，可对照实际到达判断是否延误'
    },
    defaultSort: { prop: 'plannedArriveTime', order: 'ascending' }
  }
];

export const getWorkbenchPool = (key: string): WorkbenchPool | undefined => {
  const k = normalizeWorkbenchPoolKey(key);
  return WORKBENCH_POOLS.find((p) => p.key === k);
};

/** 服务端可排序字段白名单（与后端 page_tasks 的 sortField 白名单保持一致） */
export const WORKBENCH_SORTABLE_PROPS = [
  'createdAt',
  'plannedLoadTime',
  'plannedArriveTime',
  'actualLoadTime',
  'dispatchedAt',
  'stageEnteredAt',
  'alertOverdueMinutes'
] as const;

export type WorkbenchSortableProp = (typeof WORKBENCH_SORTABLE_PROPS)[number];

export const isSortableProp = (prop?: string): prop is WorkbenchSortableProp =>
  !!prop &&
  (WORKBENCH_SORTABLE_PROPS as readonly string[]).includes(prop);

export function buildWorkbenchTableColumns(pool: WorkbenchPool): Columns {
  const L = { ...COL, ...pool.columnLabels };
  const tips = buildColumnTipMap(pool);
  const actionW = resolveActionColumnMinWidth(pool);
  // ele-admin-plus 的 Column 类型未导出 type/prop/columnKey 等运行时合法字段，
  // 与计划列表（waybill-pool-registry）保持一致，用宽类型承载后再断言。
  const cols: Record<string, unknown>[] = [];

  /** 有提示的列统一走 tipHeader（表头短词 + 问号图标） */
  const withTip = (id: WorkbenchColumnId, col: Record<string, unknown>) =>
    tips[COL_FIELD[id] ?? id] ? { ...col, headerSlot: 'tipHeader' } : col;

  for (const id of pool.columns) {
    switch (id) {
      case 'selection':
        cols.push({ type: 'selection', width: 48, align: 'center' });
        break;
      case 'taskNo':
        cols.push({ prop: 'taskNo', label: L.taskNo, minWidth: 160 });
        break;
      case 'carrierType':
        cols.push(
          withTip(id, {
            prop: 'carrierType',
            label: L.carrierType,
            width: 110,
            align: 'center',
            slot: 'carrierType'
          })
        );
        break;
      case 'carrierName':
        cols.push(
          withTip(id, {
            columnKey: 'carrierName',
            label: L.carrierName,
            minWidth: 160,
            slot: 'carrierName'
          })
        );
        break;
      case 'plateNumber':
        cols.push({
          prop: 'plateNumber',
          label: L.plateNumber,
          width: 120,
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
        cols.push(
          withTip(id, {
            columnKey: 'carrierResource',
            label: L.carrierResource,
            minWidth: 180,
            slot: 'carrierResource'
          })
        );
        break;
      case 'waybillCount':
        cols.push(
          withTip(id, {
            prop: 'waybillCount',
            label: L.waybillCount,
            width: 116,
            align: 'center',
            slot: 'waybillCount'
          })
        );
        break;
      case 'totalQuantity':
        cols.push(
          withTip(id, {
            prop: 'totalQuantity',
            label: L.totalQuantity,
            width: 92,
            align: 'center',
            slot: 'totalQuantity'
          })
        );
        break;
      case 'plannedLoadTime':
        cols.push(
          withTip(id, {
            prop: 'plannedLoadTime',
            label: L.plannedLoadTime,
            width: 186,
            align: 'center',
            sortable: 'custom',
            slot: 'plannedLoadTime'
          })
        );
        break;
      case 'plannedArriveTime':
        cols.push(
          withTip(id, {
            prop: 'plannedArriveTime',
            label: L.plannedArriveTime,
            width: 186,
            align: 'center',
            sortable: 'custom',
            slot: 'plannedArriveTime'
          })
        );
        break;
      case 'actualLoadTime':
        cols.push(
          withTip(id, {
            prop: 'actualLoadTime',
            label: L.actualLoadTime,
            width: 186,
            align: 'center',
            sortable: 'custom',
            slot: 'actualLoadTime'
          })
        );
        break;
      case 'createdAt':
        cols.push({
          prop: 'createdAt',
          label: L.createdAt,
          width: 176,
          align: 'center',
          sortable: 'custom',
          slot: 'createdAt'
        });
        break;
      case 'stageDuration':
        cols.push(
          withTip(id, {
            prop: 'stageEnteredAt',
            label: L.stageDuration,
            width: 136,
            align: 'center',
            sortable: 'custom',
            slot: 'stageDuration'
          })
        );
        break;
      case 'alertOverdue':
        cols.push(
          withTip(id, {
            prop: 'alertOverdueMinutes',
            label: L.alertOverdue,
            width: 128,
            align: 'center',
            sortable: 'custom',
            slot: 'alertOverdue'
          })
        );
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
          // fixed 右列不会按内容自适应，用估算下限兜住「首项 + 更多」
          minWidth: actionW,
          width: actionW,
          align: 'center',
          fixed: 'right',
          resizable: false,
          slot: 'action'
        });
        break;
      default:
        break;
    }
  }
  return cols as Columns;
}
