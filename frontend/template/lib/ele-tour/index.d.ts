import { Ref } from 'vue';
import { EleTooltipInstance } from '../ele-app/plus';
import { TourStep } from './types';

declare function __VLS_template(): {
    title?(_: {
        step: TourStep;
        current: number | undefined;
    }): any;
    text?(_: {
        step: TourStep;
        current: number | undefined;
    }): any;
    footer?(_: {
        step: TourStep;
        current: number | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: NumberConstructor;
    steps: {
        type: import('vue').PropType<TourStep[]>;
        required: boolean;
    };
    mask: {
        type: BooleanConstructor;
        default: boolean;
    };
    padding: {
        type: NumberConstructor;
        default: number;
    };
    zIndex: NumberConstructor;
    locale: import('vue').PropType<Partial<import('./types').TourLocale>>;
}>, {
    tooltipRef: Ref<EleTooltipInstance, EleTooltipInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value?: number | null | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: NumberConstructor;
    steps: {
        type: import('vue').PropType<TourStep[]>;
        required: boolean;
    };
    mask: {
        type: BooleanConstructor;
        default: boolean;
    };
    padding: {
        type: NumberConstructor;
        default: number;
    };
    zIndex: NumberConstructor;
    locale: import('vue').PropType<Partial<import('./types').TourLocale>>;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value?: number | null | undefined) => any) | undefined;
}>, {
    mask: boolean;
    padding: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
