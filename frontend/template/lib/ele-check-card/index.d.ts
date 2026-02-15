import { CheckCardItem, CheckedValue } from './types';

declare function __VLS_template(): {
    item?(_: {
        item: CheckCardItem | undefined;
        checked: boolean;
        disabled: boolean;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: {
        type: import('vue').PropType<CheckedValue>;
        default: () => null;
    };
    items: import('vue').PropType<CheckCardItem[] | import('./types').CheckCardItemsFunction>;
    multiple: BooleanConstructor;
    disabled: BooleanConstructor;
    bordered: {
        type: BooleanConstructor;
        default: boolean;
    };
    arrow: {
        type: BooleanConstructor;
        default: boolean;
    };
    arrowStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    itemClass: StringConstructor;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    row: import('vue').PropType<boolean | import('../ele-app/el').ElRowProps>;
    allowUncheck: BooleanConstructor;
}>, {
    reloadOptions: (params?: any) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value: CheckedValue) => void;
    change: (_value: CheckedValue) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: {
        type: import('vue').PropType<CheckedValue>;
        default: () => null;
    };
    items: import('vue').PropType<CheckCardItem[] | import('./types').CheckCardItemsFunction>;
    multiple: BooleanConstructor;
    disabled: BooleanConstructor;
    bordered: {
        type: BooleanConstructor;
        default: boolean;
    };
    arrow: {
        type: BooleanConstructor;
        default: boolean;
    };
    arrowStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    itemClass: StringConstructor;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    row: import('vue').PropType<boolean | import('../ele-app/el').ElRowProps>;
    allowUncheck: BooleanConstructor;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value: CheckedValue) => any) | undefined;
    onChange?: ((_value: CheckedValue) => any) | undefined;
}>, {
    modelValue: CheckedValue;
    disabled: boolean;
    multiple: boolean;
    bordered: boolean;
    arrow: boolean;
    allowUncheck: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
