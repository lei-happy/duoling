import { StyleValue } from '../ele-app/types';
import { EleTextInstance } from '../ele-app/plus';
import { EllipsisTooltip } from './types';

declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    maxLine: NumberConstructor;
    lineHeight: (NumberConstructor | StringConstructor)[];
    tooltip: {
        type: import('vue').PropType<boolean | EllipsisTooltip>;
        default: () => {
            original: boolean;
        };
    };
    tag: StringConstructor;
    type: import('vue').PropType<import('../ele-text/types').TextType>;
    size: import('vue').PropType<import('../ele-text/types').TextSize>;
    deleted: BooleanConstructor;
    underline: BooleanConstructor;
    strong: BooleanConstructor;
    italic: BooleanConstructor;
    icon: import('vue').PropType<import('../ele-text/types').TextIcon>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: import('vue').PropType<StyleValue>;
}>, {
    textRef: import('vue').Ref<EleTextInstance, EleTextInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    maxLine: NumberConstructor;
    lineHeight: (NumberConstructor | StringConstructor)[];
    tooltip: {
        type: import('vue').PropType<boolean | EllipsisTooltip>;
        default: () => {
            original: boolean;
        };
    };
    tag: StringConstructor;
    type: import('vue').PropType<import('../ele-text/types').TextType>;
    size: import('vue').PropType<import('../ele-text/types').TextSize>;
    deleted: BooleanConstructor;
    underline: BooleanConstructor;
    strong: BooleanConstructor;
    italic: BooleanConstructor;
    icon: import('vue').PropType<import('../ele-text/types').TextIcon>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: import('vue').PropType<StyleValue>;
}>> & Readonly<{}>, {
    strong: boolean;
    tooltip: boolean | EllipsisTooltip;
    underline: boolean;
    italic: boolean;
    deleted: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
