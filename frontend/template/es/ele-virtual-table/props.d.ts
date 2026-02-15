import { ExtractPropTypes } from 'vue';
import { ScrollPos } from './types';

/**
 * 属性
 */
export declare const virtualTableProps: {
    /** 行高 */
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
    selectedRowKeys: import('vue').PropType<import('../ele-data-table/types').DataKey[]>;
    cacheData: import('vue').PropType<import('../ele-data-table/types').DataItem[]>;
    data: {
        type: import('vue').PropType<any[]>;
        default: () => never[];
    };
    height: (NumberConstructor | StringConstructor)[];
    maxHeight: (NumberConstructor | StringConstructor)[];
    tableLayout: {
        type: import('vue').PropType<"fixed" | "auto">;
        default: string;
    };
    width: (NumberConstructor | StringConstructor)[];
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
};
export type VirtualTableProps = ExtractPropTypes<typeof virtualTableProps>;
/**
 * 事件
 */
export declare const virtualTableEmits: {
    endEeached: (_params: any) => boolean;
    scroll: (_params: ScrollPos) => boolean;
    rowsRendered: (_params: any) => boolean;
    'update:currentRowKey': (_currentRowKey?: import('../ele-data-table/types').DataKey) => boolean;
    'update:selectedRowKeys': (_selectedRowKeys?: import('../ele-data-table/types').DataKey[]) => boolean;
    select: (_selection: import('../ele-data-table/types').DataItem[], _row: import('../ele-data-table/types').DataItem) => boolean;
    selectAll: (_selection: import('../ele-data-table/types').DataItem[]) => boolean;
    selectionChange: (_selection: import('../ele-data-table/types').DataItem[]) => boolean;
    cellMouseEnter: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellMouseLeave: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellClick: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellDblclick: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    cellContextmenu: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _cell: HTMLTableCellElement, _e: MouseEvent) => boolean;
    rowClick: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _e: MouseEvent, _disabled?: boolean, _selection?: import('../ele-data-table/types').DataItem[]) => boolean;
    rowContextmenu: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _e: MouseEvent) => boolean;
    rowDblclick: (_row: import('../ele-data-table/types').DataItem, _column: import('../ele-data-table/types').Column, _e: MouseEvent) => boolean;
    headerClick: (_column: import('../ele-data-table/types').Column, _e: MouseEvent) => boolean;
    headerContextmenu: (_column: import('../ele-data-table/types').Column, _e: MouseEvent) => boolean;
    sortChange: (_sorter: import('../ele-data-table/types').Sorter) => boolean;
    filterChange: (_filter: import('../ele-data-table/types').Filter) => boolean;
    currentChange: (_current?: import('../ele-data-table/types').DataItem | null, _old?: import('../ele-data-table/types').DataItem | null) => boolean;
    headerDragend: (_width: number, _old: number, _column: import('../ele-data-table/types').Column, _e: MouseEvent) => boolean;
    expandChange: (_row: import('../ele-data-table/types').DataItem, _expanded: boolean) => boolean;
};
