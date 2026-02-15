import { Ref } from 'vue';
import { ElTableInstance } from '../ele-app/el';
import { DataKey, DataItem, Column, Columns, Sorter, Filter } from './types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    stripe: {
        type: BooleanConstructor;
        default: null;
    };
    border: {
        type: BooleanConstructor;
        default: null;
    };
    rowKey: {
        type: import('vue').PropType<import('./types').RowKey>;
        required: boolean;
    };
    columns: {
        type: import('vue').PropType<Columns>;
        required: boolean;
    };
    pageIndex: NumberConstructor;
    errorText: StringConstructor;
    headerEllipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    slotNormalize: {
        type: BooleanConstructor;
        default: boolean;
    };
    sticky: BooleanConstructor;
    bottomLine: {
        type: BooleanConstructor;
        default: boolean;
    };
    emptyProps: {
        type: import('vue').PropType<import('./types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: import('vue').PropType<import('./types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: import('vue').PropType<DataKey[]>;
    cacheData: import('vue').PropType<DataItem[]>;
    data: {
        type: import('vue').PropType<any[]>;
        default: () => never[];
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
    width: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    lazy: BooleanConstructor;
    className: {
        type: StringConstructor;
        default: string;
    };
    height: (NumberConstructor | StringConstructor)[];
    emptyText: StringConstructor;
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
    tableLayout: {
        type: import('vue').PropType<"fixed" | "auto">;
        default: string;
    };
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
}>, {
    clearSort: () => void;
    clearSelection: () => void;
    toggleRowSelection: (row: DataItem, selected?: boolean, ignoreSelectable?: boolean) => void;
    setCurrentRow: (row?: DataItem | null) => void;
    setCurrentRowKey: (key?: DataKey | null) => void;
    getCurrentRow: () => DataItem | undefined;
    setSelectedRows: (rows?: DataItem[]) => void;
    setSelectedRowKeys: (keys?: DataKey[]) => void;
    toggleRowExpansionAll: (expanded?: boolean) => void;
    updateSelectedAndChecked: () => void;
    tableRef: Ref<ElTableInstance, ElTableInstance>;
    getSelectionRows: () => DataItem[] | undefined;
    toggleAllSelection: () => void;
    toggleRowExpansion: (row: DataItem, expanded?: boolean) => void;
    clearFilter: (columnKeys?: string[]) => void;
    doLayout: () => void;
    sort: (prop: string, order: string) => void;
    scrollTo: (options: number | ScrollToOptions, yCoord?: number) => void;
    setScrollTop: (top?: number) => void;
    setScrollLeft: (left?: number) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    'update:currentRowKey': (_currentRowKey?: DataKey) => boolean;
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
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    stripe: {
        type: BooleanConstructor;
        default: null;
    };
    border: {
        type: BooleanConstructor;
        default: null;
    };
    rowKey: {
        type: import('vue').PropType<import('./types').RowKey>;
        required: boolean;
    };
    columns: {
        type: import('vue').PropType<Columns>;
        required: boolean;
    };
    pageIndex: NumberConstructor;
    errorText: StringConstructor;
    headerEllipsis: {
        type: BooleanConstructor;
        default: boolean;
    };
    slotNormalize: {
        type: BooleanConstructor;
        default: boolean;
    };
    sticky: BooleanConstructor;
    bottomLine: {
        type: BooleanConstructor;
        default: boolean;
    };
    emptyProps: {
        type: import('vue').PropType<import('./types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: import('vue').PropType<import('./types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: import('vue').PropType<DataKey[]>;
    cacheData: import('vue').PropType<DataItem[]>;
    data: {
        type: import('vue').PropType<any[]>;
        default: () => never[];
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
    width: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    lazy: BooleanConstructor;
    className: {
        type: StringConstructor;
        default: string;
    };
    height: (NumberConstructor | StringConstructor)[];
    emptyText: StringConstructor;
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
    tableLayout: {
        type: import('vue').PropType<"fixed" | "auto">;
        default: string;
    };
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
}>> & Readonly<{
    onSelect?: ((_selection: DataItem[], _row: DataItem) => any) | undefined;
    onScroll?: ((_option: {
        scrollLeft: number;
        scrollTop: number;
    }) => any) | undefined;
    onFilterChange?: ((_filter: Filter) => any) | undefined;
    onCellClick?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onCellContextmenu?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onExpandChange?: ((_row: DataItem, _expanded: boolean) => any) | undefined;
    onCellDblclick?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    "onUpdate:currentRowKey"?: ((_currentRowKey?: DataKey | undefined) => any) | undefined;
    "onUpdate:selectedRowKeys"?: ((_selectedRowKeys?: DataKey[] | undefined) => any) | undefined;
    onSelectAll?: ((_selection: DataItem[]) => any) | undefined;
    onSelectionChange?: ((_selection: DataItem[]) => any) | undefined;
    onCellMouseEnter?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onCellMouseLeave?: ((_row: DataItem, _column: Column, _cell: HTMLTableCellElement, _e: MouseEvent) => any) | undefined;
    onRowClick?: ((_row: DataItem, _column: Column, _e: MouseEvent, _disabled?: boolean | undefined, _selection?: DataItem[] | undefined) => any) | undefined;
    onRowContextmenu?: ((_row: DataItem, _column: Column, _e: MouseEvent) => any) | undefined;
    onRowDblclick?: ((_row: DataItem, _column: Column, _e: MouseEvent) => any) | undefined;
    onHeaderClick?: ((_column: Column, _e: MouseEvent) => any) | undefined;
    onHeaderContextmenu?: ((_column: Column, _e: MouseEvent) => any) | undefined;
    onSortChange?: ((_sorter: Sorter) => any) | undefined;
    onCurrentChange?: ((_current?: DataItem | null | undefined, _old?: DataItem | null | undefined) => any) | undefined;
    onHeaderDragend?: ((_width: number, _old: number, _column: Column, _e: MouseEvent) => any) | undefined;
}>, {
    data: any[];
    fit: boolean;
    border: boolean;
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
    tableLayout: "fixed" | "auto";
    scrollbarAlwaysOn: boolean;
    flexible: boolean;
    scrollbarTabindex: string | number;
    allowDragLastColumn: boolean;
    preserveExpandedContent: boolean;
    nativeScrollbar: boolean;
    sticky: boolean;
    headerEllipsis: boolean;
    slotNormalize: boolean;
    bottomLine: boolean;
    emptyProps: import('./types').TableEmptyProps;
    reserveCurrent: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
