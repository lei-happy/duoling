import { PropType } from 'vue';
import { DataKey, DataItem, Column, TableSize, CellClass, CellStyle, SpanMethod, ShowOverflowTooltip, TableLoad } from '../../ele-data-table/types';
import { BodyColumns, ColSize, VirtualRow } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 主体列配置 */
    bodyCols: {
        type: PropType<BodyColumns>;
        required: true;
    };
    /** 表格主体列宽 */
    colSizes: {
        type: PropType<ColSize[]>;
        required: true;
    };
    /** 当前行索引 */
    rowIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 当前行对象 */
    rowItem: {
        type: PropType<VirtualRow>;
        required: true;
    };
    /** 当前行数据唯一值 */
    rowId: PropType<DataKey>;
    /** 表格多选选中的值 */
    checkedRowKeys: PropType<Set<DataKey>>;
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
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 树表格展开图标的列 */
    expandColumnKey: StringConstructor;
    /** 表格展开行的值 */
    expandedRowKeys: PropType<DataKey[]>;
    /** 树表格是否懒加载子级 */
    lazy: BooleanConstructor;
    /** 树表格懒加载方法 */
    load: PropType<TableLoad>;
    /** 树表格行数据缩进级别 */
    level: NumberConstructor;
    /** 树表格每一级行缩进大小 */
    indent: NumberConstructor;
    /** 是否需要固定单元格高度 */
    fixedCellHeight: BooleanConstructor;
    /** 表格是否是自适应行高 */
    autoRowHeight: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    cellClick: (_row: VirtualRow, _col: Column, _e: MouseEvent) => void;
    cellDblclick: (_row: VirtualRow, _col: Column, _e: MouseEvent) => void;
    cellContextmenu: (_row: VirtualRow, _col: Column, _e: MouseEvent) => void;
    cellMouseenter: (_row: VirtualRow, _col: Column, _e: MouseEvent) => void;
    cellCheckedChange: (_row: VirtualRow, _checked: boolean) => void;
    cellExpandChange: (_row: VirtualRow, _expanded: boolean, _children?: DataItem[] | undefined) => void;
    cellMouseleave: (_row: VirtualRow, _col: Column, _e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 主体列配置 */
    bodyCols: {
        type: PropType<BodyColumns>;
        required: true;
    };
    /** 表格主体列宽 */
    colSizes: {
        type: PropType<ColSize[]>;
        required: true;
    };
    /** 当前行索引 */
    rowIndex: {
        type: NumberConstructor;
        required: true;
    };
    /** 当前行对象 */
    rowItem: {
        type: PropType<VirtualRow>;
        required: true;
    };
    /** 当前行数据唯一值 */
    rowId: PropType<DataKey>;
    /** 表格多选选中的值 */
    checkedRowKeys: PropType<Set<DataKey>>;
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
    /** 表格尺寸 */
    tableSize: PropType<TableSize>;
    /** 树表格展开图标的列 */
    expandColumnKey: StringConstructor;
    /** 表格展开行的值 */
    expandedRowKeys: PropType<DataKey[]>;
    /** 树表格是否懒加载子级 */
    lazy: BooleanConstructor;
    /** 树表格懒加载方法 */
    load: PropType<TableLoad>;
    /** 树表格行数据缩进级别 */
    level: NumberConstructor;
    /** 树表格每一级行缩进大小 */
    indent: NumberConstructor;
    /** 是否需要固定单元格高度 */
    fixedCellHeight: BooleanConstructor;
    /** 表格是否是自适应行高 */
    autoRowHeight: BooleanConstructor;
}>> & Readonly<{
    onCellClick?: ((_row: VirtualRow, _col: Column, _e: MouseEvent) => any) | undefined;
    onCellDblclick?: ((_row: VirtualRow, _col: Column, _e: MouseEvent) => any) | undefined;
    onCellContextmenu?: ((_row: VirtualRow, _col: Column, _e: MouseEvent) => any) | undefined;
    onCellMouseenter?: ((_row: VirtualRow, _col: Column, _e: MouseEvent) => any) | undefined;
    onCellCheckedChange?: ((_row: VirtualRow, _checked: boolean) => any) | undefined;
    onCellExpandChange?: ((_row: VirtualRow, _expanded: boolean, _children?: DataItem[] | undefined) => any) | undefined;
    onCellMouseleave?: ((_row: VirtualRow, _col: Column, _e: MouseEvent) => any) | undefined;
}>, {
    lazy: boolean;
    fixedCellHeight: boolean;
    autoRowHeight: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
