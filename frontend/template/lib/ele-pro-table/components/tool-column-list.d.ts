import { PropType } from 'vue';
import { ColItem } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 列配置数据 */
    data: PropType<ColItem[]>;
    /** 父级数据 */
    parent: PropType<ColItem>;
    /** 是否开启列拖拽排序 */
    sortable: BooleanConstructor;
    /** 是否开启开关固定列 */
    allowFixed: BooleanConstructor;
    /** 是否开启列宽设置 */
    allowWidth: BooleanConstructor;
    /** 列宽输入框提示文本 */
    columnWidthPlaceholder: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    sortChange: (_colItems: ColItem[], _parent?: ColItem | undefined) => void;
    checkedChange: (_item: ColItem, _checked: boolean) => void;
    fixedLeft: (_item: ColItem) => void;
    fixedRight: (_item: ColItem) => void;
    fixedLeftTooltip: (_el: HTMLElement) => void;
    fixedRightTooltip: (_el: HTMLElement) => void;
    colWidthChange: (_item: ColItem, _width?: string | number | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 列配置数据 */
    data: PropType<ColItem[]>;
    /** 父级数据 */
    parent: PropType<ColItem>;
    /** 是否开启列拖拽排序 */
    sortable: BooleanConstructor;
    /** 是否开启开关固定列 */
    allowFixed: BooleanConstructor;
    /** 是否开启列宽设置 */
    allowWidth: BooleanConstructor;
    /** 列宽输入框提示文本 */
    columnWidthPlaceholder: StringConstructor;
}>> & Readonly<{
    onSortChange?: ((_colItems: ColItem[], _parent?: ColItem | undefined) => any) | undefined;
    onCheckedChange?: ((_item: ColItem, _checked: boolean) => any) | undefined;
    onFixedLeft?: ((_item: ColItem) => any) | undefined;
    onFixedRight?: ((_item: ColItem) => any) | undefined;
    onFixedLeftTooltip?: ((_el: HTMLElement) => any) | undefined;
    onFixedRightTooltip?: ((_el: HTMLElement) => any) | undefined;
    onColWidthChange?: ((_item: ColItem, _width?: string | number | undefined) => any) | undefined;
}>, {
    sortable: boolean;
    allowFixed: boolean;
    allowWidth: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
