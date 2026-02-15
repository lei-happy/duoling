import { PropType } from 'vue';
import { Column, FilterValue, TableSize, HeaderCellClass, HeaderCellStyle } from '../../ele-data-table/types';
import { HeaderColumn, SortBy, CellFilterChangeParams, ColSize } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 当前列配置 */
    column: PropType<HeaderColumn>;
    /** 当前列索引 */
    columnIndex: NumberConstructor;
    /** 当前行索引 */
    headerIndex: NumberConstructor;
    /** 当前列宽 */
    colSize: PropType<ColSize>;
    /** 表格排序状态 */
    sortBy: PropType<SortBy>;
    /** 表格当前筛选值 */
    filterValue: PropType<FilterValue>;
    /** 表格是否是全选状态 */
    isCheckAll: BooleanConstructor;
    /** 表格是否是半选状态 */
    isIndeterminate: BooleanConstructor;
    /** 是否禁用表头选择框 */
    disabledCheckbox: BooleanConstructor;
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 单元格类名自定义 */
    headerCellClass: PropType<HeaderCellClass>;
    /** 单元格样式自定义 */
    headerCellStyle: PropType<HeaderCellStyle>;
    /** 表头单元格是否溢出省略 */
    headerEllipsis: BooleanConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    click: (_col: Column, _e: MouseEvent) => void;
    contextmenu: (_col: Column, _e: MouseEvent) => void;
    mouseenter: (_col: Column, _e: MouseEvent) => void;
    filterChange: (_params: CellFilterChangeParams) => void;
    checkedChange: (_checked: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 当前列配置 */
    column: PropType<HeaderColumn>;
    /** 当前列索引 */
    columnIndex: NumberConstructor;
    /** 当前行索引 */
    headerIndex: NumberConstructor;
    /** 当前列宽 */
    colSize: PropType<ColSize>;
    /** 表格排序状态 */
    sortBy: PropType<SortBy>;
    /** 表格当前筛选值 */
    filterValue: PropType<FilterValue>;
    /** 表格是否是全选状态 */
    isCheckAll: BooleanConstructor;
    /** 表格是否是半选状态 */
    isIndeterminate: BooleanConstructor;
    /** 是否禁用表头选择框 */
    disabledCheckbox: BooleanConstructor;
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 单元格类名自定义 */
    headerCellClass: PropType<HeaderCellClass>;
    /** 单元格样式自定义 */
    headerCellStyle: PropType<HeaderCellStyle>;
    /** 表头单元格是否溢出省略 */
    headerEllipsis: BooleanConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
}>> & Readonly<{
    onClick?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onContextmenu?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onMouseenter?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onFilterChange?: ((_params: CellFilterChangeParams) => any) | undefined;
    onCheckedChange?: ((_checked: boolean) => any) | undefined;
}>, {
    headerEllipsis: boolean;
    isCheckAll: boolean;
    isIndeterminate: boolean;
    disabledCheckbox: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
