import { PropType } from 'vue';
import { StyleValue } from '../../ele-app/types';
import { CheckCardItem } from '../types';

declare function __VLS_template(): {
    default?(_: {
        item: CheckCardItem | undefined;
        checked: boolean;
        disabled: boolean;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 数据 */
    item: PropType<CheckCardItem>;
    /** 是否选中 */
    checked: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否显示边框 */
    bordered: BooleanConstructor;
    /** 是否需要选中箭头 */
    arrow: BooleanConstructor;
    /** 选中箭头样式 */
    arrowStyle: PropType<StyleValue>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 数据 */
    item: PropType<CheckCardItem>;
    /** 是否选中 */
    checked: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否显示边框 */
    bordered: BooleanConstructor;
    /** 是否需要选中箭头 */
    arrow: BooleanConstructor;
    /** 选中箭头样式 */
    arrowStyle: PropType<StyleValue>;
}>> & Readonly<{}>, {
    disabled: boolean;
    checked: boolean;
    bordered: boolean;
    arrow: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
