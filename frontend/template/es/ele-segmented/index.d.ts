import { ElTabsInstance } from '../ele-app/el';

declare function __VLS_template(): {
    label?(_: {
        item: import('./types').SegmentedItem;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: (NumberConstructor | StringConstructor)[];
    block: BooleanConstructor;
    disabled: BooleanConstructor;
    items: {
        type: import('vue').PropType<import('./types').SegmentedItem[]>;
        required: boolean;
    };
    size: import('vue').PropType<import('./types').SegmentedSize>;
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
}>, {
    tabRef: import('vue').Ref<ElTabsInstance, ElTabsInstance>;
    updateActiveBar: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value: string | number) => void;
    change: (_active: string | number) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: (NumberConstructor | StringConstructor)[];
    block: BooleanConstructor;
    disabled: BooleanConstructor;
    items: {
        type: import('vue').PropType<import('./types').SegmentedItem[]>;
        required: boolean;
    };
    size: import('vue').PropType<import('./types').SegmentedSize>;
    validateEvent: {
        type: BooleanConstructor;
        default: boolean;
    };
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value: string | number) => any) | undefined;
    onChange?: ((_active: string | number) => any) | undefined;
}>, {
    disabled: boolean;
    validateEvent: boolean;
    block: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
