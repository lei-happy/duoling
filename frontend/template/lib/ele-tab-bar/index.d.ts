import { TabBarItem } from './types';

declare function __VLS_template(): {
    label?(_: {
        label: string;
        item: TabBarItem;
    }): any;
    extra?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: (StringConstructor | NumberConstructor | BooleanConstructor | ObjectConstructor)[];
    items: import('vue').PropType<TabBarItem[]>;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    type: import('vue').PropType<import('./types').TabBarType>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value?: any) => void;
    change: (_active?: any) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: (StringConstructor | NumberConstructor | BooleanConstructor | ObjectConstructor)[];
    items: import('vue').PropType<TabBarItem[]>;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    type: import('vue').PropType<import('./types').TabBarType>;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value?: any) => any) | undefined;
    onChange?: ((_active?: any) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
