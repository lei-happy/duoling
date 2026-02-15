import { Ref } from 'vue';
import { EleDataTableProps, EleToolbarProps } from '../ele-app/plus';
import { DataItem, Column, Columns, Sorter, Filter, RowKey } from '../ele-data-table/types';
import { ReloadFunction, DoneParams, TableTool, FetchFunction, TableViewInstance, ExportConfig, PrintConfig, TableExportParams } from './types';

declare function __VLS_template(): any;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    rowKey: {
        type: import('vue').PropType<RowKey>;
        required: boolean;
    };
    loading: BooleanConstructor;
    datasource: {
        type: import('vue').PropType<import('./types').Datasource>;
        required: boolean;
    };
    where: import('vue').PropType<import('./types').Where>;
    request: import('vue').PropType<import('./types').RequestOption>;
    response: import('vue').PropType<import('./types').ResponseOption>;
    parseData: import('vue').PropType<import('./types').ParseData>;
    loadOnCreated: {
        type: BooleanConstructor;
        default: boolean;
    };
    loadOnChanged: {
        type: BooleanConstructor;
        default: boolean;
    };
    selections: import('vue').PropType<DataItem[]>;
    current: import('vue').PropType<DataItem | null>;
    toolbar: {
        type: import('vue').PropType<boolean | EleToolbarProps>;
        default: () => null;
    };
    tools: {
        type: import('vue').PropType<TableTool[] | boolean>;
        default: () => null;
    };
    columnSortable: {
        type: BooleanConstructor;
        default: boolean;
    };
    columnFixed: {
        type: BooleanConstructor;
        default: boolean;
    };
    maximizedIndex: NumberConstructor;
    maximizedHeight: (NumberConstructor | StringConstructor)[];
    tableStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    footerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    pagination: {
        type: import('vue').PropType<boolean | import('./types').TablePagination>;
        default: () => null;
    };
    loadingProps: import('vue').PropType<import('../ele-app/plus').EleLoadingProps>;
    cacheKey: StringConstructor;
    virtual: BooleanConstructor;
    rowHeight: NumberConstructor;
    locale: import('vue').PropType<Partial<import('./types').TableLocale>>;
    exportConfig: import('vue').PropType<ExportConfig>;
    printConfig: import('vue').PropType<PrintConfig>;
    maximized: BooleanConstructor;
    height: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    tableLayout: {
        type: import('vue').PropType<"fixed" | "auto">;
        default: string;
    };
    width: (NumberConstructor | StringConstructor)[];
    border: {
        type: BooleanConstructor;
        default: null;
    };
    columns: {
        type: import('vue').PropType<Columns>;
        required: boolean;
    };
    size: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "" | "small" | "default" | "large", never>>;
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
    summaryMethod: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["summaryMethod"]>;
    rowClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["rowClassName"]>;
    rowStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["rowStyle"]>;
    cellClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["cellClassName"]>;
    cellStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["cellStyle"]>;
    headerRowClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowClassName"]>;
    headerRowStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowStyle"]>;
    headerCellClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellClassName"]>;
    headerCellStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellStyle"]>;
    highlightCurrentRow: BooleanConstructor;
    currentRowKey: (NumberConstructor | StringConstructor)[];
    expandRowKeys: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["expandRowKeys"]>;
    defaultExpandAll: BooleanConstructor;
    defaultSort: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["defaultSort"]>;
    tooltipEffect: StringConstructor;
    tooltipOptions: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipOptions"]>;
    spanMethod: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["spanMethod"]>;
    selectOnIndeterminate: {
        type: BooleanConstructor;
        default: boolean;
    };
    indent: {
        type: NumberConstructor;
        default: number;
    };
    treeProps: {
        type: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["treeProps"]>;
        default: () => {
            hasChildren: string;
            children: string;
            checkStrictly: boolean;
        };
    };
    load: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["load"]>;
    scrollbarAlwaysOn: BooleanConstructor;
    flexible: BooleanConstructor;
    showOverflowTooltip: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["showOverflowTooltip"]>;
    tooltipFormatter: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipFormatter"]>;
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
        type: import('vue').PropType<import('../ele-data-table/types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: import('vue').PropType<import('../ele-data-table/types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: import('vue').PropType<import('../ele-data-table/types').DataKey[]>;
}>, {
    tableViewRef: Ref<TableViewInstance, TableViewInstance>;
    reload: ReloadFunction;
    getData: () => DataItem[];
    setData: (data: DataItem[]) => void;
    fetch: FetchFunction;
    openPrintModal: () => void;
    printData: (params?: TableExportParams) => void;
    openExportModal: () => void;
    exportData: (params?: TableExportParams) => void;
    getTableRef: () => TableViewInstance | undefined;
    tableData: Ref<{
        [x: string]: any;
        [x: number]: any;
        [x: symbol]: any;
        _isMock?: boolean | undefined;
    }[], DataItem[] | {
        [x: string]: any;
        [x: number]: any;
        [x: symbol]: any;
        _isMock?: boolean | undefined;
    }[]>;
    tableLoading: Ref<boolean, boolean>;
    tableProps: import('vue').ComputedRef<EleDataTableProps>;
    reloadTable: () => void;
    goPageByRowKey: (key: unknown) => void;
    clearSelection: () => void;
    getSelectionRows: () => DataItem[] | undefined;
    toggleRowSelection: (row: DataItem, selected?: boolean, ignoreSelectable?: boolean) => void;
    toggleAllSelection: () => void;
    toggleRowExpansion: (row: DataItem, expanded?: boolean) => void;
    setCurrentRow: (row?: DataItem | null) => void;
    clearSort: () => void;
    clearFilter: (columnKeys?: string[]) => void;
    doLayout: () => void;
    sort: (prop: string, order: string) => void;
    scrollTo: (options: number | ScrollToOptions, yCoord?: number) => void;
    setScrollTop: (top?: number) => void;
    setScrollLeft: (left?: number) => void;
    setCurrentRowKey: (key?: import('../ele-data-table/types').DataKey | null) => void;
    getCurrentRow: () => DataItem | undefined;
    setSelectedRows: (rows?: DataItem[]) => void;
    setSelectedRowKeys: (keys?: import('../ele-data-table/types').DataKey[], rows?: DataItem[]) => void;
    toggleRowExpansionAll: (expanded?: boolean) => void;
    updateSelectedAndChecked: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    select: (_selection: DataItem[], _row: DataItem) => void;
    done: (_result: DoneParams<DataItem>, _parent?: DataItem | undefined) => void;
    scroll: (_params: import('element-plus/es/components/table-v2/src/composables/use-scrollbar').ScrollPos) => void;
    "update:currentRowKey": (_currentRowKey?: import('../ele-data-table/types').DataKey | undefined) => void;
    "update:selectedRowKeys": (_selectedRowKeys?: import('../ele-data-table/types').DataKey[] | undefined) => void;
    selectAll: (_selection: DataItem[]) => void;
    selectionChange: (_selection: DataItem[]) => void;
    cellMouseEnter: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => void;
    cellMouseLeave: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => void;
    cellClick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => void;
    cellDblclick: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => void;
    cellContextmenu: (_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => void;
    rowClick: (_row: DataItem, _column: Column, _e: MouseEvent, _disabled?: boolean | undefined, _selection?: DataItem[] | undefined) => void;
    rowContextmenu: (_row: DataItem, _column: Column, _e: MouseEvent) => void;
    rowDblclick: (_row: DataItem, _column: Column, _e: MouseEvent) => void;
    headerClick: (_column: Column, _e: MouseEvent) => void;
    headerContextmenu: (_column: Column, _e: MouseEvent) => void;
    sortChange: (_sorter: Sorter) => void;
    filterChange: (_filter: Filter) => void;
    currentChange: (_current?: DataItem | null | undefined, _old?: DataItem | null | undefined) => void;
    headerDragend: (_width: number, _old: number, _column: Column, _e: MouseEvent) => void;
    expandChange: (_row: DataItem, _expanded: boolean) => void;
    endEeached: (_params: any) => void;
    rowsRendered: (_params: any) => void;
    refresh: () => void;
    "update:selections": (_selections: DataItem[]) => void;
    "update:current": (_current?: DataItem | null | undefined) => void;
    columnsChange: (_columns: Columns, _tableColumns: Columns, _isReset: boolean) => void;
    sizeChange: (_size: "" | "small" | "default" | "large" | undefined) => void;
    maximizedChange: (_maximized: boolean) => void;
    "update:maximized": (_maximized: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    rowKey: {
        type: import('vue').PropType<RowKey>;
        required: boolean;
    };
    loading: BooleanConstructor;
    datasource: {
        type: import('vue').PropType<import('./types').Datasource>;
        required: boolean;
    };
    where: import('vue').PropType<import('./types').Where>;
    request: import('vue').PropType<import('./types').RequestOption>;
    response: import('vue').PropType<import('./types').ResponseOption>;
    parseData: import('vue').PropType<import('./types').ParseData>;
    loadOnCreated: {
        type: BooleanConstructor;
        default: boolean;
    };
    loadOnChanged: {
        type: BooleanConstructor;
        default: boolean;
    };
    selections: import('vue').PropType<DataItem[]>;
    current: import('vue').PropType<DataItem | null>;
    toolbar: {
        type: import('vue').PropType<boolean | EleToolbarProps>;
        default: () => null;
    };
    tools: {
        type: import('vue').PropType<TableTool[] | boolean>;
        default: () => null;
    };
    columnSortable: {
        type: BooleanConstructor;
        default: boolean;
    };
    columnFixed: {
        type: BooleanConstructor;
        default: boolean;
    };
    maximizedIndex: NumberConstructor;
    maximizedHeight: (NumberConstructor | StringConstructor)[];
    tableStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    footerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    pagination: {
        type: import('vue').PropType<boolean | import('./types').TablePagination>;
        default: () => null;
    };
    loadingProps: import('vue').PropType<import('../ele-app/plus').EleLoadingProps>;
    cacheKey: StringConstructor;
    virtual: BooleanConstructor;
    rowHeight: NumberConstructor;
    locale: import('vue').PropType<Partial<import('./types').TableLocale>>;
    exportConfig: import('vue').PropType<ExportConfig>;
    printConfig: import('vue').PropType<PrintConfig>;
    maximized: BooleanConstructor;
    height: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    tableLayout: {
        type: import('vue').PropType<"fixed" | "auto">;
        default: string;
    };
    width: (NumberConstructor | StringConstructor)[];
    border: {
        type: BooleanConstructor;
        default: null;
    };
    columns: {
        type: import('vue').PropType<Columns>;
        required: boolean;
    };
    size: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "" | "small" | "default" | "large", never>>;
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
    summaryMethod: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["summaryMethod"]>;
    rowClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["rowClassName"]>;
    rowStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["rowStyle"]>;
    cellClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["cellClassName"]>;
    cellStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["cellStyle"]>;
    headerRowClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowClassName"]>;
    headerRowStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerRowStyle"]>;
    headerCellClassName: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellClassName"]>;
    headerCellStyle: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["headerCellStyle"]>;
    highlightCurrentRow: BooleanConstructor;
    currentRowKey: (NumberConstructor | StringConstructor)[];
    expandRowKeys: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["expandRowKeys"]>;
    defaultExpandAll: BooleanConstructor;
    defaultSort: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["defaultSort"]>;
    tooltipEffect: StringConstructor;
    tooltipOptions: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipOptions"]>;
    spanMethod: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["spanMethod"]>;
    selectOnIndeterminate: {
        type: BooleanConstructor;
        default: boolean;
    };
    indent: {
        type: NumberConstructor;
        default: number;
    };
    treeProps: {
        type: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["treeProps"]>;
        default: () => {
            hasChildren: string;
            children: string;
            checkStrictly: boolean;
        };
    };
    load: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["load"]>;
    scrollbarAlwaysOn: BooleanConstructor;
    flexible: BooleanConstructor;
    showOverflowTooltip: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["showOverflowTooltip"]>;
    tooltipFormatter: import('vue').PropType<import('element-plus/es/components/table/index').TableProps<any>["tooltipFormatter"]>;
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
        type: import('vue').PropType<import('../ele-data-table/types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: import('vue').PropType<import('../ele-data-table/types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: import('vue').PropType<import('../ele-data-table/types').DataKey[]>;
}>> & Readonly<{
    onSelect?: ((_selection: DataItem[], _row: DataItem) => any) | undefined;
    onDone?: ((_result: DoneParams<DataItem>, _parent?: DataItem | undefined) => any) | undefined;
    onScroll?: ((_params: import('element-plus/es/components/table-v2/src/composables/use-scrollbar').ScrollPos) => any) | undefined;
    "onUpdate:currentRowKey"?: ((_currentRowKey?: import('../ele-data-table/types').DataKey | undefined) => any) | undefined;
    "onUpdate:selectedRowKeys"?: ((_selectedRowKeys?: import('../ele-data-table/types').DataKey[] | undefined) => any) | undefined;
    onSelectAll?: ((_selection: DataItem[]) => any) | undefined;
    onSelectionChange?: ((_selection: DataItem[]) => any) | undefined;
    onCellMouseEnter?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onCellMouseLeave?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onCellClick?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onCellDblclick?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onCellContextmenu?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onRowClick?: ((_row: DataItem, _column: Column, _e: MouseEvent, _disabled?: boolean | undefined, _selection?: DataItem[] | undefined) => any) | undefined;
    onRowContextmenu?: ((_row: DataItem, _column: Column, _e: MouseEvent) => any) | undefined;
    onRowDblclick?: ((_row: DataItem, _column: Column, _e: MouseEvent) => any) | undefined;
    onHeaderClick?: ((_column: Column, _e: MouseEvent) => any) | undefined;
    onHeaderContextmenu?: ((_column: Column, _e: MouseEvent) => any) | undefined;
    onSortChange?: ((_sorter: Sorter) => any) | undefined;
    onFilterChange?: ((_filter: Filter) => any) | undefined;
    onCurrentChange?: ((_current?: DataItem | null | undefined, _old?: DataItem | null | undefined) => any) | undefined;
    onHeaderDragend?: ((_width: number, _old: number, _column: Column, _e: MouseEvent) => any) | undefined;
    onExpandChange?: ((_row: DataItem, _expanded: boolean) => any) | undefined;
    onEndEeached?: ((_params: any) => any) | undefined;
    onRowsRendered?: ((_params: any) => any) | undefined;
    onRefresh?: (() => any) | undefined;
    "onUpdate:selections"?: ((_selections: DataItem[]) => any) | undefined;
    "onUpdate:current"?: ((_current?: DataItem | null | undefined) => any) | undefined;
    onColumnsChange?: ((_columns: Columns, _tableColumns: Columns, _isReset: boolean) => any) | undefined;
    onSizeChange?: ((_size: "" | "small" | "default" | "large" | undefined) => any) | undefined;
    onMaximizedChange?: ((_maximized: boolean) => any) | undefined;
    "onUpdate:maximized"?: ((_maximized: boolean) => any) | undefined;
}>, {
    tableLayout: "fixed" | "auto";
    border: boolean;
    loading: boolean;
    fit: boolean;
    lazy: boolean;
    className: string;
    stripe: boolean;
    showHeader: boolean;
    showSummary: boolean;
    highlightCurrentRow: boolean;
    defaultExpandAll: boolean;
    selectOnIndeterminate: boolean;
    indent: number;
    treeProps: import('element-plus/es/components/table/src/table/defaults').TreeProps | undefined;
    scrollbarAlwaysOn: boolean;
    flexible: boolean;
    scrollbarTabindex: string | number;
    allowDragLastColumn: boolean;
    preserveExpandedContent: boolean;
    nativeScrollbar: boolean;
    maximized: boolean;
    tools: boolean | string[];
    sticky: boolean;
    toolbar: boolean | EleToolbarProps;
    headerEllipsis: boolean;
    slotNormalize: boolean;
    bottomLine: boolean;
    emptyProps: import('../ele-data-table/types').TableEmptyProps;
    reserveCurrent: boolean;
    pagination: boolean | import('./types').TablePagination;
    loadOnCreated: boolean;
    loadOnChanged: boolean;
    columnSortable: boolean;
    columnFixed: boolean;
    virtual: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
