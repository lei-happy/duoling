import { PropType } from 'vue';
import { StyleValue } from '../../ele-app/types';
import { ElEmptyProps } from '../../ele-app/el';
import { EleTooltipProps } from '../../ele-app/plus';
import { PopperType } from '../../ele-basic-select/types';
import { ItemTooltip } from '../types';

declare function __VLS_template(): {
    icon?(_: {
        icon: string;
        prefix: boolean;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 选中的图标 */
    icon: StringConstructor;
    /** 图标数据 */
    data: {
        type: PropType<string[]>;
        required: true;
    };
    /** 空组件属性 */
    emptyProps: PropType<ElEmptyProps>;
    /** 是否显示提示 */
    tooltip: PropType<ItemTooltip>;
    /** 提示属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 气泡是否展开 */
    popperVisible: BooleanConstructor;
    /** 网格样式 */
    gridStyle: PropType<StyleValue>;
    /** 图标样式 */
    itemStyle: PropType<StyleValue>;
    /** 下拉组件类型 */
    popperType: PropType<PopperType>;
}>, {
    hideTooltip: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    select: (_icon: string) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 选中的图标 */
    icon: StringConstructor;
    /** 图标数据 */
    data: {
        type: PropType<string[]>;
        required: true;
    };
    /** 空组件属性 */
    emptyProps: PropType<ElEmptyProps>;
    /** 是否显示提示 */
    tooltip: PropType<ItemTooltip>;
    /** 提示属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 气泡是否展开 */
    popperVisible: BooleanConstructor;
    /** 网格样式 */
    gridStyle: PropType<StyleValue>;
    /** 图标样式 */
    itemStyle: PropType<StyleValue>;
    /** 下拉组件类型 */
    popperType: PropType<PopperType>;
}>> & Readonly<{
    onSelect?: ((_icon: string) => any) | undefined;
}>, {
    popperVisible: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
