import { PropType } from 'vue';
import { DataItem, Column, TableSize, CellClass, CellStyle, SpanMethod, ShowOverflowTooltip } from '../../ele-data-table/types';
import { BodyColumn, ColSize } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 列配置 */
    column: {
        type: PropType<BodyColumn>;
        required: true;
    };
    /** 列索引 */
    columnIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 行索引 */
    rowIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 行数据 */
    rowData: {
        type: PropType<DataItem>;
        required: true;
    };
    /** 所有列的列宽 */
    colSizes: {
        type: PropType<ColSize[]>;
        required: true;
    };
    /** 单元格类名自定义 */
    bodyCellClass: PropType<CellClass>;
    /** 单元格样式自定义 */
    bodyCellStyle: PropType<CellStyle>;
    /** 单元格合并行列方法 */
    spanMethod: PropType<SpanMethod>;
    /** 溢出提示组件全局属性 */
    tableTooltipProps: PropType<ShowOverflowTooltip>;
    /** 序号列起始编号 */
    pageIndex: NumberConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
    /** 多选当前行是否选中 */
    isChecked: BooleanConstructor;
    /** 多选当前行是否禁用 */
    isDisabled: BooleanConstructor;
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 树表格展开图标的列 */
    expandColumnKey: StringConstructor;
    /** 树表格当前行是否有子级 */
    hasChildren: BooleanConstructor;
    /** 树表格当前行缩进 */
    rowIndent: StringConstructor;
    /** 树表格当前行是否折叠 */
    isCollapse: BooleanConstructor;
    /** 树表格子级加载状态 */
    loading: BooleanConstructor;
    /** 是否需要固定单元格高度 */
    fixedCellHeight: BooleanConstructor;
    /** 表格是否是自适应行高 */
    autoRowHeight: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    click: (_col: Column, _e: MouseEvent) => void;
    contextmenu: (_col: Column, _e: MouseEvent) => void;
    dblclick: (_col: Column, _e: MouseEvent) => void;
    mouseenter: (_col: Column, _e: MouseEvent) => void;
    mouseleave: (_col: Column, _e: MouseEvent) => void;
    expandChange: (_expanded: boolean) => void;
    checkedChange: (_checked: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 列配置 */
    column: {
        type: PropType<BodyColumn>;
        required: true;
    };
    /** 列索引 */
    columnIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 行索引 */
    rowIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 行数据 */
    rowData: {
        type: PropType<DataItem>;
        required: true;
    };
    /** 所有列的列宽 */
    colSizes: {
        type: PropType<ColSize[]>;
        required: true;
    };
    /** 单元格类名自定义 */
    bodyCellClass: PropType<CellClass>;
    /** 单元格样式自定义 */
    bodyCellStyle: PropType<CellStyle>;
    /** 单元格合并行列方法 */
    spanMethod: PropType<SpanMethod>;
    /** 溢出提示组件全局属性 */
    tableTooltipProps: PropType<ShowOverflowTooltip>;
    /** 序号列起始编号 */
    pageIndex: NumberConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
    /** 多选当前行是否选中 */
    isChecked: BooleanConstructor;
    /** 多选当前行是否禁用 */
    isDisabled: BooleanConstructor;
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 树表格展开图标的列 */
    expandColumnKey: StringConstructor;
    /** 树表格当前行是否有子级 */
    hasChildren: BooleanConstructor;
    /** 树表格当前行缩进 */
    rowIndent: StringConstructor;
    /** 树表格当前行是否折叠 */
    isCollapse: BooleanConstructor;
    /** 树表格子级加载状态 */
    loading: BooleanConstructor;
    /** 是否需要固定单元格高度 */
    fixedCellHeight: BooleanConstructor;
    /** 表格是否是自适应行高 */
    autoRowHeight: BooleanConstructor;
}>> & Readonly<{
    onClick?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onContextmenu?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onDblclick?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onMouseenter?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onMouseleave?: ((_col: Column, _e: MouseEvent) => any) | undefined;
    onExpandChange?: ((_expanded: boolean) => any) | undefined;
    onCheckedChange?: ((_checked: boolean) => any) | undefined;
}>, {
    loading: boolean;
    isCollapse: boolean;
    isDisabled: boolean;
    hasChildren: boolean;
    fixedCellHeight: boolean;
    autoRowHeight: boolean;
    isChecked: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
