import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { EleLoadingProps, EleToolbarProps } from '../ele-app/plus';
import { DataItem, Columns, TableSize, RowKey } from '../ele-data-table/types';
import { default as TableTools } from './components/table-tools';
import { default as ToolExport } from './components/tool-export';
import { default as ToolPrint } from './components/tool-print';
import { Where, Datasource, RequestOption, ResponseOption, ParseData, DoneParams, TablePagination, TableTool, TableLocale, ExportConfig, PrintConfig } from './types';

/**
 * 属性
 */
export declare const proTableProps: {
    rowKey: {
        type: PropType<RowKey>;
        required: boolean;
    };
    /** 数据请求状态 */
    loading: BooleanConstructor;
    /** 数据源 */
    datasource: {
        type: PropType<Datasource>;
        required: boolean;
    };
    /** 默认请求参数 */
    where: PropType<Where>;
    /** 自定义请求参数名称 */
    request: PropType<RequestOption>;
    /** 自定义响应参数名称 */
    response: PropType<ResponseOption>;
    /** 自定义响应数据解析 */
    parseData: PropType<ParseData>;
    /** 初始是否请求数据 */
    loadOnCreated: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否在排序和筛选改变后自动刷新 */
    loadOnChanged: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 多选选中的数据 */
    selections: PropType<DataItem[]>;
    /** 单选选中的数据 */
    current: PropType<DataItem | null>;
    /** 是否开启顶部工具栏 */
    toolbar: {
        type: PropType<boolean | EleToolbarProps>;
        default: () => null;
    };
    /** 表头工具按钮布局 */
    tools: {
        type: PropType<TableTool[] | boolean>;
        default: () => null;
    };
    /** 列配置是否可拖拽排序 */
    columnSortable: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 列配置是否可固定列 */
    columnFixed: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 表格全屏时的层级 */
    maximizedIndex: NumberConstructor;
    /** 表格全屏状态的高度 */
    maximizedHeight: (NumberConstructor | StringConstructor)[];
    /** 自定义表格样式 */
    tableStyle: PropType<StyleValue>;
    /** 自定义底部样式 */
    footerStyle: PropType<StyleValue>;
    /** 分页组件 */
    pagination: {
        type: PropType<boolean | TablePagination>;
        default: () => null;
    };
    /** 自定义加载组件属性 */
    loadingProps: PropType<EleLoadingProps>;
    /** 列配置缓存名称 */
    cacheKey: StringConstructor;
    /** 是否虚拟滚动 */
    virtual: BooleanConstructor;
    /** 虚拟滚动表格行高 */
    rowHeight: NumberConstructor;
    /** 国际化 */
    locale: PropType<Partial<TableLocale>>;
    /** 导出配置 */
    exportConfig: PropType<ExportConfig>;
    /** 打印配置 */
    printConfig: PropType<PrintConfig>;
    /** 表格是否最大化状态 */
    maximized: BooleanConstructor;
    height: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    tableLayout: {
        type: PropType<"fixed" | "auto">;
        default: string;
    };
    width: (NumberConstructor | StringConstructor)[];
    border: {
        type: BooleanConstructor;
        default: null;
    };
    columns: {
        type: PropType<Columns>;
        required: boolean;
    };
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
    stripe: {
        type: BooleanConstructor;
        default: null;
    };
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
    sticky: BooleanConstructor;
    headerEllipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    slotNormalize: {
        type: BooleanConstructor;
        default: boolean;
    };
    bottomLine: {
        type: BooleanConstructor;
        default: boolean;
    };
    emptyProps: {
        type: PropType<import('../ele-data-table/types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: PropType<import('../ele-data-table/types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: PropType<import('../ele-data-table/types').DataKey[]>;
};
export type ProTableProps = ExtractPropTypes<typeof proTableProps>;
/**
 * 事件
 */
export declare const proTableEmits: {
    /** 表格数据请求完成事件 */
    done: (_result: DoneParams<DataItem>, _parent?: DataItem) => boolean;
    /** 更新多选选中数据 */
    'update:selections': (_selections: DataItem[]) => boolean;
    /** 更新单选选中数据 */
    'update:current': (_current?: DataItem | null) => boolean;
    /** 列配置改变事件 */
    columnsChange: (_columns: Columns, _tableColumns: Columns, _isReset: boolean) => boolean;
    /** 表格尺寸改变事件 */
    sizeChange: (_size: TableSize) => boolean;
    /** 表格最大化切换事件 */
    maximizedChange: (_maximized: boolean) => boolean;
    /** 表格最大化状态更新 */
    'update:maximized': (_maximized: boolean) => boolean;
    /** 数组数据源时刷新按钮点击事件 */
    refresh: () => boolean;
    endEeached: (_params: any) => boolean;
    scroll: (_params: import('element-plus/es/components/table-v2/src/composables/use-scrollbar').ScrollPos) => boolean;
    rowsRendered: (_params: any) => boolean;
    'update:currentRowKey': (_currentRowKey?: import('../ele-data-table/types').DataKey) => boolean;
    'update:selectedRowKeys': (_selectedRowKeys?: import('../ele-data-table/types').DataKey[]) => boolean;
    select: (_selection: DataItem[], _row: DataItem) => boolean;
    selectAll: (_selection: DataItem[]) => boolean;
    selectionChange: (_selection: DataItem[]) => boolean;
    cellMouseEnter: (_row: DataItem, _column: import('./types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellMouseLeave: (_row: DataItem, _column: import('./types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellClick: (_row: DataItem, _column: import('./types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellDblclick: (_row: DataItem, _column: import('./types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellContextmenu: (_row: DataItem, _column: import('./types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    rowClick: (_row: DataItem, _column: import('./types').Column, _e: MouseEvent, _disabled?: boolean, _selection?: DataItem[]) => boolean;
    rowContextmenu: (_row: DataItem, _column: import('./types').Column, _e: MouseEvent) => boolean;
    rowDblclick: (_row: DataItem, _column: import('./types').Column, _e: MouseEvent) => boolean;
    headerClick: (_column: import('./types').Column, _e: MouseEvent) => boolean;
    headerContextmenu: (_column: import('./types').Column, _e: MouseEvent) => boolean;
    sortChange: (_sorter: import('./types').Sorter) => boolean;
    filterChange: (_filter: import('./types').Filter) => boolean;
    currentChange: (_current?: DataItem | null, _old?: DataItem | null) => boolean;
    headerDragend: (_width: number, _old: number, _column: import('./types').Column, _e: MouseEvent) => boolean;
    expandChange: (_row: DataItem, _expanded: boolean) => boolean;
};
/**
 * 默认工具按钮实例
 */
export type TableToolsInstance = InstanceType<typeof TableTools> | null;
/**
 * 导出组件实例
 */
export type ToolExportInstance = InstanceType<typeof ToolExport> | null;
/**
 * 打印组件实例
 */
export type ToolPrintInstance = InstanceType<typeof ToolPrint> | null;
