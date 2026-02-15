import { Emitter } from '../ele-app/types';
import { ElTableInstance } from '../ele-app/el';
import { getValue } from '../utils/common';
import { DataTableEmitsType } from './props';
import { DataKey, DataItem, Column, Columns, Sorter, Filter, GetInstance, TableMethods, ShowOverflowTooltip, TooltipEffect, TooltipOptions, RowClass, RowKey } from './types';

export { getValue };
/**
 * 获取行的类名
 * @param rowClass 自定义行类名
 * @param param 方法类型的参数
 */
export declare function getRowClass(rowClass: RowClass | undefined, param: Parameters<Exclude<RowClass, string | undefined>>[0]): string | undefined;
/**
 * 获取行的类名
 * @param rowClass 自定义行类名
 * @param param 方法类型的参数
 */
export declare function getBodyRowClass(rowClass: RowClass | undefined, param: Parameters<Exclude<RowClass, string | undefined>>[0]): string;
/**
 * 获取表头行的类名
 * @param rowClass 自定义行类名
 * @param param 方法类型的参数
 * @param ellipsis 是否单行省略
 */
export declare function getHeadRowClass(rowClass: RowClass | undefined, param: Parameters<Exclude<RowClass, string | undefined>>[0], ellipsis: boolean): string;
/**
 * 获取全局溢出提示组件属性
 * @param showOverflowTooltip 溢出提示组件属性
 * @param tooltipEffect 溢出提示组件主题
 * @param tooltipOptions 溢出提示组件配置
 */
export declare function getGlobalTooltipProps(showOverflowTooltip?: ShowOverflowTooltip, tooltipEffect?: TooltipEffect, tooltipOptions?: TooltipOptions): ShowOverflowTooltip;
/**
 * 合并提示组件相关属性
 * @param props 单元格提示组件属性
 * @param globalProps 表格提示组件属性
 */
export declare function mergeTooltipProps(props?: ShowOverflowTooltip, globalProps?: ShowOverflowTooltip): Exclude<ShowOverflowTooltip, true>;
/**
 * 获取单元格提示组件属性
 * @param props 单元格提示组件属性
 * @param globalProps 表格提示组件属性
 */
export declare function getTooltipProps(props?: ShowOverflowTooltip, globalProps?: ShowOverflowTooltip): ShowOverflowTooltip;
/**
 * 切换表格指定数据的选中状态
 * @param tableRef 表格实例
 * @param row 数据
 * @param selected 选中状态
 */
export declare function toggleRowSelectionPro(tableRef: ElTableInstance | undefined, row: DataItem, selected: boolean): void;
/**
 * 获取表格筛选值
 * @param tableRef 表格实例
 */
export declare function getTableFilter(tableRef?: ElTableInstance): Filter | undefined;
/**
 * 获取含表格状态的列配置
 * @param cols 表格的列
 * @param sorter 当前排序状态
 * @param filter 当前筛选状态
 */
export declare function getStateCols(cols: Columns, sorter?: Sorter, filter?: Filter): {
    cols: Columns;
    sorter?: undefined;
} | {
    cols: Columns;
    sorter: Sorter | undefined;
};
/**
 * 获取判断多选是否可选择的方法
 * @param columns 列配置
 */
export declare function getSelectableFunction(columns?: Columns): ((row: any, index: number) => boolean) | null | undefined;
/**
 * 判断行是否禁止多选
 * @param row 行数据
 * @param index 行索引
 * @param columns 列配置
 */
export declare function isDisableRow(row: DataItem, index: number, columns?: Columns): boolean;
/**
 * 判断是否保存不存在的选中数据
 * @param columns 列配置
 */
export declare function isReserveChecked(columns?: Columns): boolean;
/**
 * 用于根据列的固定值排序
 * @param fixed 固定值
 */
export declare function getColFixedNumber(fixed?: boolean | string): 0 | 1 | 2;
/**
 * 获取列类名
 * @param col 列属性
 */
export declare function getCellClass(col: Column): string | undefined;
/**
 * 获取列筛选下拉框类名
 * @param filterClassName 自定义类名
 */
export declare function getFilterPopperClass(filterClassName?: string): string;
/**
 * 获取数据值
 * @param rows 数据
 * @param rowKey 值键名
 */
export declare function getRowKeys(rows: DataItem[] | undefined, rowKey: RowKey): DataKey[];
/**
 * 获取值对应的数据
 * @param key 值
 * @param data 全部数据
 * @param rowKey 值键名
 * @param childrenField 子级数据键名
 */
export declare function getRowByKey(key: DataKey, data?: DataItem[], rowKey?: RowKey, childrenField?: string): DataItem | undefined;
/**
 * 获取平铺后的数据值和数据
 * @param data 表格数据
 * @param rowKey 数据值字段名
 * @param childrenField 子级字段名
 */
export declare function getKeysAndList(data?: DataItem[], rowKey?: RowKey, childrenField?: string): [DataKey[], DataItem[]];
/**
 * 判断值是否改变
 * @param value1 值
 * @param value2 新值
 */
export declare function valueIsChanged<T>(value1?: T | null, value2?: T | null): boolean;
/**
 * 判断数组数据是否改变
 * @param list1 数组
 * @param list2 新数组
 */
export declare function arrayIsChanged<T>(list1?: T[] | null, list2?: T[] | null): boolean;
/**
 * 使用粘性表头
 */
export declare function useStickyHeader(): {
    isLayoutFixedHead: import('vue').ComputedRef<boolean | undefined>;
    isLayoutMaximized: import('vue').ComputedRef<boolean | undefined>;
};
/**
 * 表格实例方法统一处理
 * @param getInstance 获取表格实例方法
 */
export declare function useMethods(getInstance: GetInstance): TableMethods;
/**
 * 表格事件统一处理
 * @param emit 事件触发器
 */
export declare function useEmits(emit: Emitter<DataTableEmitsType>): {
    /** 新增的事件 */
    'onUpdate:currentRowKey': (currentRowKey?: DataKey) => void;
    'onUpdate:selectedRowKeys': (selectedRowKeys: DataKey[]) => void;
    onSelect: (_selection: DataItem[], _row: DataItem) => any;
    onScroll: (_option: {
        scrollLeft: number;
        scrollTop: number;
    }) => any;
    onSelectAll: (_selection: DataItem[]) => any;
    onSelectionChange: (_selection: DataItem[]) => any;
    onCellMouseEnter: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any;
    onCellMouseLeave: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any;
    onCellClick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any;
    onCellDblclick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any;
    onCellContextmenu: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any;
    onRowClick: (_row: DataItem, _column: Column, _e: MouseEvent, _disabled?: boolean | undefined, _selection?: DataItem[] | undefined) => any;
    onRowContextmenu: (_row: DataItem, _column: Column, _e: MouseEvent) => any;
    onRowDblclick: (_row: DataItem, _column: Column, _e: MouseEvent) => any;
    onHeaderClick: (_column: Column, _e: MouseEvent) => any;
    onHeaderContextmenu: (_column: Column, _e: MouseEvent) => any;
    onSortChange: (_sorter: Sorter) => any;
    onFilterChange: (_filter: Filter) => any;
    onCurrentChange: (_current?: DataItem | null | undefined, _old?: DataItem | null | undefined) => any;
    onHeaderDragend: (_width: number, _old: number, _column: Column, _e: MouseEvent) => any;
    onExpandChange: (_row: DataItem, _expanded: boolean) => any;
};
