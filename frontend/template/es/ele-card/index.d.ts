declare function __VLS_template(): {
    header?(_: {}): any;
    extra?(_: {}): any;
    collapseIcon?(_: {
        collapse: boolean;
    }): any;
    default?(_: {}): any;
    footer?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    header: StringConstructor;
    headerClass: StringConstructor;
    footer: StringConstructor;
    footerClass: StringConstructor;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyClass: StringConstructor;
    shadow: import('vue').PropType<import('../ele-app/el').ElCardProps["shadow"]>;
    bordered: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    footerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    collapsable: import('vue').PropType<boolean | "header">;
    collapse: BooleanConstructor;
    collapseIconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    searchForm: BooleanConstructor;
    flexTable: import('vue').PropType<boolean | "auto">;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    collapseChange: (_collapse: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    header: StringConstructor;
    headerClass: StringConstructor;
    footer: StringConstructor;
    footerClass: StringConstructor;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    bodyClass: StringConstructor;
    shadow: import('vue').PropType<import('../ele-app/el').ElCardProps["shadow"]>;
    bordered: BooleanConstructor;
    headerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    footerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    collapsable: import('vue').PropType<boolean | "header">;
    collapse: BooleanConstructor;
    collapseIconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    searchForm: BooleanConstructor;
    flexTable: import('vue').PropType<boolean | "auto">;
}>> & Readonly<{
    onCollapseChange?: ((_collapse: boolean) => any) | undefined;
}>, {
    collapse: boolean;
    bordered: boolean;
    searchForm: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
