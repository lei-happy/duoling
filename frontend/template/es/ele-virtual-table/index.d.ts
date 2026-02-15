import { Ref } from 'vue';
import { ElTableV2Instance } from '../ele-app/el';
import { DataKey, DataItem, Column, Filter, OrderValue, Sorter } from '../ele-data-table/types';
import { ScrollStrategy, ScrollPos, VirtualRow } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: {
    row: DataItem | undefined;
    column: Column;
    $index: number | undefined;
}) => any>> & Partial<Record<string, (_: any) => any>> & {
    empty?(_: {
        text: string | undefined;
        error: string | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    rowHeight: NumberConstructor;
    stripe: {
        type: BooleanConstructor;
        default: null;
    };
    border: {
        type: BooleanConstructor;
        default: null;
    };
    rowKey: {
        type: import('vue').PropType<import('../ele-data-table/types').RowKey>;
        required: boolean;
    };
    columns: {
        type: import('vue').PropType<import('../ele-data-table/types').Columns>;
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
        type: import('vue').PropType<import('../ele-data-table/types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: import('vue').PropType<import('../ele-data-table/types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: import('vue').PropType<DataKey[]>;
    cacheData: import('vue').PropType<DataItem[]>;
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
    data: {
        type: import('vue').PropType<any[]>;
        default: () => never[];
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
    tableRef: Ref<ElTableV2Instance, ElTableV2Instance>;
    updateWrapSize: () => void;
    updateTableData: () => void;
    updateSelectedAndChecked: () => void;
    setSelectedRows: (rows?: DataItem[]) => void;
    setSelectedRowKeys: (keys?: DataKey[]) => void;
    toggleRowExpansionAll: (expanded?: boolean) => void;
    clearSelection: () => void;
    getSelectionRows: () => DataItem[];
    toggleRowSelection: (row: DataItem, selected?: boolean) => void;
    toggleAllSelection: () => void;
    toggleRowExpansion: (row: VirtualRow, expanded?: boolean) => void;
    setCurrentRow: (row?: DataItem | null) => void;
    setCurrentRowKey: (key?: DataKey | null) => void;
    getCurrentRow: () => DataItem | undefined;
    clearSort: () => void;
    clearFilter: (columnKeys?: string[]) => void;
    doLayout: (force?: boolean) => void;
    sort: (prop: string, order: OrderValue) => void;
    scrollTo: (options: number | ScrollToOptions, yCoord?: number) => void;
    setScrollTop: (top?: number) => void;
    setScrollLeft: (left?: number) => void;
    scrollToRow: (row: number, strategy: ScrollStrategy) => void;
    hideTooltip: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    select: (_selection: DataItem[], _row: DataItem) => void;
    scroll: (_params: ScrollPos) => void;
    "update:currentRowKey": (_currentRowKey?: DataKey | undefined) => void;
    "update:selectedRowKeys": (_selectedRowKeys?: DataKey[] | undefined) => void;
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
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    rowHeight: NumberConstructor;
    stripe: {
        type: BooleanConstructor;
        default: null;
    };
    border: {
        type: BooleanConstructor;
        default: null;
    };
    rowKey: {
        type: import('vue').PropType<import('../ele-data-table/types').RowKey>;
        required: boolean;
    };
    columns: {
        type: import('vue').PropType<import('../ele-data-table/types').Columns>;
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
        type: import('vue').PropType<import('../ele-data-table/types').TableEmptyProps>;
        default: () => null;
    };
    rowClickChecked: import('vue').PropType<import('../ele-data-table/types').RowClickChecked>;
    reserveCurrent: BooleanConstructor;
    selectedRowKeys: import('vue').PropType<DataKey[]>;
    cacheData: import('vue').PropType<DataItem[]>;
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
    data: {
        type: import('vue').PropType<any[]>;
        default: () => never[];
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
    onScroll?: ((_params: ScrollPos) => any) | undefined;
    "onUpdate:currentRowKey"?: ((_currentRowKey?: DataKey | undefined) => any) | undefined;
    "onUpdate:selectedRowKeys"?: ((_selectedRowKeys?: DataKey[] | undefined) => any) | undefined;
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
}>, {
    fit: boolean;
    border: boolean;
    lazy: boolean;
    className: string;
    data: any[];
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
    emptyProps: import('../ele-data-table/types').TableEmptyProps;
    reserveCurrent: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
