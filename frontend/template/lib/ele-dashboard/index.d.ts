declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    type: import('vue').PropType<import('./types').DashboardType>;
    color: StringConstructor;
    size: (StringConstructor | NumberConstructor)[];
    space: (StringConstructor | NumberConstructor)[];
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    type: import('vue').PropType<import('./types').DashboardType>;
    color: StringConstructor;
    size: (StringConstructor | NumberConstructor)[];
    space: (StringConstructor | NumberConstructor)[];
}>> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
