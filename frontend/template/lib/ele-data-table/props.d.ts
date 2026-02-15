import { PropType, ExtractPropTypes } from 'vue';
import { DataKey, DataItem, Column, Columns, Sorter, Filter, TableEmptyProps, RowClickChecked, RowKey } from './types';

declare const normalizeProps: Omit<{
    data: {
        type: PropType<any[]>;
        default: () => never[];
    };
    size: {
        readonly type: PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "" | "small" | "default" | "large", never>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    width: (NumberConstructor | StringConstructor)[];
    height: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    fit: {
        type: BooleanConstructor;
        default: boolean;
    };
    stripe: BooleanConstructor;
    border: BooleanConstructor;
    rowKey: PropType<import('element-plus/es/components/table/index').TableProps<any>["rowKey"]>;
    showHeader: {
        type: BooleanConstructor;
        default: boolean;
    };
    showSummary: BooleanConstructor;
    sumText: StringConstructor;
    summaryMethod: PropType<import('element-plus/es/components/table/index').TableProps<any>["summaryMethod"]>;
    rowClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["rowClassName"]>;
    rowStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["rowStyle"]>;
    cellClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["cellClassName"]>;
    cellStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["cellStyle"]>;
    headerRowClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowClassName"]>;
    headerRowStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowStyle"]>;
    headerCellClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellClassName"]>;
    headerCellStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellStyle"]>;
    highlightCurrentRow: BooleanConstructor;
    currentRowKey: (NumberConstructor | StringConstructor)[];
    emptyText: StringConstructor;
    expandRowKeys: PropType<import('element-plus/es/components/table/index').TableProps<any>["expandRowKeys"]>;
    defaultExpandAll: BooleanConstructor;
    defaultSort: PropType<import('element-plus/es/components/table/index').TableProps<any>["defaultSort"]>;
    tooltipEffect: StringConstructor;
    tooltipOptions: PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipOptions"]>;
    spanMethod: PropType<import('element-plus/es/components/table/index').TableProps<any>["spanMethod"]>;
    selectOnIndeterminate: {
        type: BooleanConstructor;
        default: boolean;
    };
    indent: {
        type: NumberConstructor;
        default: number;
    };
    treeProps: {
        type: PropType<import('element-plus/es/components/table/index').TableProps<any>["treeProps"]>;
        default: () => {
            hasChildren: string;
            children: string;
            checkStrictly: boolean;
        };
    };
    lazy: BooleanConstructor;
    load: PropType<import('element-plus/es/components/table/index').TableProps<any>["load"]>;
    style: {
        type: PropType<import('vue').CSSProperties>;
        default: () => {};
    };
    className: {
        type: StringConstructor;
        default: string;
    };
    tableLayout: {
        type: PropType<"fixed" | "auto">;
        default: string;
    };
    scrollbarAlwaysOn: BooleanConstructor;
    flexible: BooleanConstructor;
    showOverflowTooltip: PropType<import('element-plus/es/components/table/index').TableProps<any>["showOverflowTooltip"]>;
    tooltipFormatter: PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipFormatter"]>;
    appendFilterPanelTo: StringConstructor;
    scrollbarTabindex: {
        type: (NumberConstructor | StringConstructor)[];
        default: undefined;
    };
    allowDragLastColumn: {
        type: BooleanConstructor;
        default: boolean;
    };
    preserveExpandedContent: BooleanConstructor;
    nativeScrollbar: BooleanConstructor;
}, "style">;
/**
 * 属性
 */
export declare const dataTableProps: {
    stripe: {
        type: BooleanConstructor;
        default: null;
    };
    border: {
        type: BooleanConstructor;
        default: null;
    };
    rowKey: {
        type: PropType<RowKey>;
        required: boolean;
    };
    /** 列配置 */
    columns: {
        type: PropType<Columns>;
        required: boolean;
    };
    /** 起始编号 */
    pageIndex: NumberConstructor;
    /** 空数据时显示的错误文本 */
    errorText: StringConstructor;
    /** 表头内容超出省略 */
    headerEllipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 插槽不渲染非正常的调用 */
    slotNormalize: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 设置粘性头部 */
    sticky: BooleanConstructor;
    /** 是否显示下边框线 */
    bottomLine: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 空组件属性 */
    emptyProps: {
        type: PropType<TableEmptyProps>;
        default: () => null;
    };
    /** 多选时行点击选中 */
    rowClickChecked: PropType<RowClickChecked>;
    /** 单选选中是否保留不存在的数据 */
    reserveCurrent: BooleanConstructor;
    /** 多选选中行的值 */
    selectedRowKeys: PropType<DataKey[]>;
    /** 缓存数据 */
    cacheData: PropType<DataItem[]>;
    data: {
        type: PropType<any[]>;
        default: () => never[];
    };
    height: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    tableLayout: {
        type: PropType<"fixed" | "auto">;
        default: string;
    };
    width: (NumberConstructor | StringConstructor)[];
    size: {
        readonly type: PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "" | "small" | "default" | "large", never>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    fit: {
        type: BooleanConstructor;
        default: boolean;
    };
    lazy: BooleanConstructor;
    className: {
        type: StringConstructor;
        default: string;
    };
    emptyText: StringConstructor;
    showHeader: {
        type: BooleanConstructor;
        default: boolean;
    };
    showSummary: BooleanConstructor;
    sumText: StringConstructor;
    summaryMethod: PropType<import('element-plus/es/components/table/index').TableProps<any>["summaryMethod"]>;
    rowClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["rowClassName"]>;
    rowStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["rowStyle"]>;
    cellClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["cellClassName"]>;
    cellStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["cellStyle"]>;
    headerRowClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowClassName"]>;
    headerRowStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowStyle"]>;
    headerCellClassName: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellClassName"]>;
    headerCellStyle: PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellStyle"]>;
    highlightCurrentRow: BooleanConstructor;
    currentRowKey: (NumberConstructor | StringConstructor)[];
    expandRowKeys: PropType<import('element-plus/es/components/table/index').TableProps<any>["expandRowKeys"]>;
    defaultExpandAll: BooleanConstructor;
    defaultSort: PropType<import('element-plus/es/components/table/index').TableProps<any>["defaultSort"]>;
    tooltipEffect: StringConstructor;
    tooltipOptions: PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipOptions"]>;
    spanMethod: PropType<import('element-plus/es/components/table/index').TableProps<any>["spanMethod"]>;
    selectOnIndeterminate: {
        type: BooleanConstructor;
        default: boolean;
    };
    indent: {
        type: NumberConstructor;
        default: number;
    };
    treeProps: {
        type: PropType<import('element-plus/es/components/table/index').TableProps<any>["treeProps"]>;
        default: () => {
            hasChildren: string;
            children: string;
            checkStrictly: boolean;
        };
    };
    load: PropType<import('element-plus/es/components/table/index').TableProps<any>["load"]>;
    scrollbarAlwaysOn: BooleanConstructor;
    flexible: BooleanConstructor;
    showOverflowTooltip: PropType<import('element-plus/es/components/table/index').TableProps<any>["showOverflowTooltip"]>;
    tooltipFormatter: PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipFormatter"]>;
    appendFilterPanelTo: StringConstructor;
    scrollbarTabindex: {
        type: (NumberConstructor | StringConstructor)[];
        default: undefined;
    };
    allowDragLastColumn: {
        type: BooleanConstructor;
        default: boolean;
    };
    preserveExpandedContent: BooleanConstructor;
    nativeScrollbar: BooleanConstructor;
};
export type DataTableProps = ExtractPropTypes<typeof dataTableProps>;
/**
 * ElTable 的事件
 */
export declare const elDataTableEmits: {
    select: (_selection: DataItem[], _row: DataItem) => boolean;
    selectAll: (_selection: DataItem[]) => boolean;
    selectionChange: (_selection: DataItem[]) => boolean;
    cellMouseEnter: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellMouseLeave: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellClick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellDblclick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellContextmenu: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    rowClick: (_row: DataItem, _column: Column, _e: MouseEvent, _disabled?: boolean, _selection?: DataItem[]) => boolean;
    rowContextmenu: (_row: DataItem, _column: Column, _e: MouseEvent) => boolean;
    rowDblclick: (_row: DataItem, _column: Column, _e: MouseEvent) => boolean;
    headerClick: (_column: Column, _e: MouseEvent) => boolean;
    headerContextmenu: (_column: Column, _e: MouseEvent) => boolean;
    sortChange: (_sorter: Sorter) => boolean;
    filterChange: (_filter: Filter) => boolean;
    currentChange: (_current?: DataItem | null, _old?: DataItem | null) => boolean;
    headerDragend: (_width: number, _old: number, _column: Column, _e: MouseEvent) => boolean;
    expandChange: (_row: DataItem, _expanded: boolean) => boolean;
    scroll: (_option: {
        scrollLeft: number;
        scrollTop: number;
    }) => boolean;
};
/**
 * 事件
 */
export declare const dataTableEmits: {
    /** 更新单选选中行的值 */
    'update:currentRowKey': (_currentRowKey?: DataKey) => boolean;
    /** 更新多选选中行的值 */
    'update:selectedRowKeys': (_selectedRowKeys?: DataKey[]) => boolean;
    select: (_selection: DataItem[], _row: DataItem) => boolean;
    selectAll: (_selection: DataItem[]) => boolean;
    selectionChange: (_selection: DataItem[]) => boolean;
    cellMouseEnter: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellMouseLeave: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellClick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellDblclick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellContextmenu: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    rowClick: (_row: DataItem, _column: Column, _e: MouseEvent, _disabled?: boolean, _selection?: DataItem[]) => boolean;
    rowContextmenu: (_row: DataItem, _column: Column, _e: MouseEvent) => boolean;
    rowDblclick: (_row: DataItem, _column: Column, _e: MouseEvent) => boolean;
    headerClick: (_column: Column, _e: MouseEvent) => boolean;
    headerContextmenu: (_column: Column, _e: MouseEvent) => boolean;
    sortChange: (_sorter: Sorter) => boolean;
    filterChange: (_filter: Filter) => boolean;
    currentChange: (_current?: DataItem | null, _old?: DataItem | null) => boolean;
    headerDragend: (_width: number, _old: number, _column: Column, _e: MouseEvent) => boolean;
    expandChange: (_row: DataItem, _expanded: boolean) => boolean;
    scroll: (_option: {
        scrollLeft: number;
        scrollTop: number;
    }) => boolean;
};
export type DataTableEmitsType = typeof dataTableEmits;
/**
 * 表格组件属性名
 */
export type TablePropKeys = Array<keyof typeof normalizeProps>;
export type DataTablePropKeys = Array<keyof typeof dataTableProps>;
export declare const tablePropKeys: TablePropKeys;
export declare const dataTablePropKeys: DataTableProps;
export {};
