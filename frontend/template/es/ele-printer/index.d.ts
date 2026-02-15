declare function __VLS_template(): {
    header?(_: {}): any;
    default?(_: {}): any;
    footer?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    footerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    title: StringConstructor;
    margin: (NumberConstructor | StringConstructor)[];
    direction: import('vue').PropType<import('./types').PrintDirection | null>;
    orientation: import('vue').PropType<import('./types').PrintOrientation | null>;
    target: import('vue').PropType<import('./types').PrintTarget | null>;
    static: BooleanConstructor;
    options: ObjectConstructor;
}>, {
    print: (options?: any) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value: boolean) => void;
    done: () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    footerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    title: StringConstructor;
    margin: (NumberConstructor | StringConstructor)[];
    direction: import('vue').PropType<import('./types').PrintDirection | null>;
    orientation: import('vue').PropType<import('./types').PrintOrientation | null>;
    target: import('vue').PropType<import('./types').PrintTarget | null>;
    static: BooleanConstructor;
    options: ObjectConstructor;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value: boolean) => any) | undefined;
    onDone?: (() => any) | undefined;
}>, {
    modelValue: boolean;
    static: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
