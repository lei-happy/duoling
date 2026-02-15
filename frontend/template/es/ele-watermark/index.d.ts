import { StyleValue } from '../ele-app/types';
import { WatermarkFont } from './types';

declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    width: NumberConstructor;
    height: NumberConstructor;
    rotate: NumberConstructor;
    zIndex: NumberConstructor;
    image: StringConstructor;
    content: import('vue').PropType<string | string[]>;
    font: import('vue').PropType<WatermarkFont>;
    gap: import('vue').PropType<import('./types').WatermarkGap>;
    offset: import('vue').PropType<import('./types').WatermarkOffset>;
    lineGap: NumberConstructor;
    customStyle: import('vue').PropType<Exclude<StyleValue, string>>;
    svgRender: BooleanConstructor;
    disabled: BooleanConstructor;
    fixed: BooleanConstructor;
    wrapPosition: {
        type: BooleanConstructor;
        default: boolean;
    };
    wrapHeight: (NumberConstructor | StringConstructor)[];
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    width: NumberConstructor;
    height: NumberConstructor;
    rotate: NumberConstructor;
    zIndex: NumberConstructor;
    image: StringConstructor;
    content: import('vue').PropType<string | string[]>;
    font: import('vue').PropType<WatermarkFont>;
    gap: import('vue').PropType<import('./types').WatermarkGap>;
    offset: import('vue').PropType<import('./types').WatermarkOffset>;
    lineGap: NumberConstructor;
    customStyle: import('vue').PropType<Exclude<StyleValue, string>>;
    svgRender: BooleanConstructor;
    disabled: BooleanConstructor;
    fixed: BooleanConstructor;
    wrapPosition: {
        type: BooleanConstructor;
        default: boolean;
    };
    wrapHeight: (NumberConstructor | StringConstructor)[];
}>> & Readonly<{}>, {
    fixed: boolean;
    disabled: boolean;
    svgRender: boolean;
    wrapPosition: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
