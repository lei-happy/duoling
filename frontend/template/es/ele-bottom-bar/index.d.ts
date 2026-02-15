declare function __VLS_template(): {
    default?(_: {}): any;
    extra?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    extraStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    teleported: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    extraStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    teleported: BooleanConstructor;
}>> & Readonly<{}>, {
    teleported: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
