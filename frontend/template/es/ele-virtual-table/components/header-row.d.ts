import { PropType } from 'vue';
import { Column, Filter, TableSize, HeaderCellClass, HeaderCellStyle } from '../../ele-data-table/types';
import { HeaderColumns, SortBy, CellFilterChangeParams, ColSize } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 表头行配置 */
    headerCols: PropType<HeaderColumns>;
    /** 表头所有行列宽 */
    headerColSizes: PropType<ColSize[]>;
    /** 当前行索引 */
    headerIndex: NumberConstructor;
    /** 表格排序状态 */
    sortBy: PropType<SortBy>;
    /** 表格筛选值 */
    filtered: PropType<Filter>;
    /** 表格是否是全选状态 */
    isCheckAll: BooleanConstructor;
    /** 表格是否是半选状态 */
    isIndeterminate: BooleanConstructor;
    /** 是否禁用表头选择框 */
    disabledCheckbox: BooleanConstructor;
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 表头单元格类名自定义 */
    headerCellClass: PropType<HeaderCellClass>;
    /** 表头单元样式自定义 */
    headerCellStyle: PropType<HeaderCellStyle>;
    /** 表头单元格是否溢出省略 */
    headerEllipsis: BooleanConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    cellClick: (_col: Column, _e: MouseEvent) => void;
    cellContextmenu: (_col: Column, _e: MouseEvent) => void;
    filterChange: (_params: CellFilterChangeParams) => void;
    checkedChange: (_checked: boolean) => void;
    cellMouseenter: (_col: Column, _e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 表头行配置 */
    headerCols: PropType<HeaderColumns>;
    /** 表头所有行列宽 */
    headerColSizes: PropType<ColSize[]>;
    /** 当前行索引 */
    headerIndex: NumberConstructor;
    /** 表格排序状态 */
    sortBy: PropType<SortBy>;
    /** 表格筛选值 */
    filtered: PropType<Filter>;
    /** 表格是否是全选状态 */
    isCheckAll: BooleanConstructor;
    /** 表格是否是半选状态 */
    isIndeterminate: BooleanConstructor;
    /** 是否禁用表头选择框 */
    disabledCheckbox: BooleanConstructor;
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 表头单元格类名自定义 */
    headerCellClass: PropType<HeaderCellClass>;
    /** 表头单元样式自定义 */
    headerCellStyle: PropType<HeaderCellStyle>;
    /** 表头单元格是否溢出省略 */
    headerEllipsis: BooleanConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
}>> & Readonly<{
    onCellClick?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onCellContextmenu?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onFilterChange?: ((_params: CellFilterChangeParams) => any) | undefined;
    onCheckedChange?: ((_checked: boolean) => any) | undefined;
    onCellMouseenter?: ((_col: Column, _e: MouseEvent) => any) | undefined;
}>, {
    headerEllipsis: boolean;
    isCheckAll: boolean;
    isIndeterminate: boolean;
    disabledCheckbox: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
