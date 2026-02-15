import { PropType } from 'vue';
import { Column, FilterValue } from '../../ele-data-table/types';
import { EleTooltipProps, EleTooltipInstance } from '../../ele-app/plus';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 选中项 */
    filtered: PropType<FilterValue>;
    /** 是否多选 */
    filterMultiple: BooleanConstructor;
    /** 数据项 */
    filters: PropType<Column["filters"]>;
    /** 弹出框定位 */
    filterPlacement: {
        type: PropType<EleTooltipProps["placement"]>;
        default: string;
    };
}>, {
    popperRef: import('vue').Ref<EleTooltipInstance, EleTooltipInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    change: (_filtered: FilterValue) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 选中项 */
    filtered: PropType<FilterValue>;
    /** 是否多选 */
    filterMultiple: BooleanConstructor;
    /** 数据项 */
    filters: PropType<Column["filters"]>;
    /** 弹出框定位 */
    filterPlacement: {
        type: PropType<EleTooltipProps["placement"]>;
        default: string;
    };
}>> & Readonly<{
    onChange?: ((_filtered: FilterValue) => any) | undefined;
}>, {
    filterPlacement: import('element-plus').Placement | undefined;
    filterMultiple: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
