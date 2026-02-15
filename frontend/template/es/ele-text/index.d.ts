declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    tag: StringConstructor;
    type: import('vue').PropType<import('./types').TextType>;
    size: import('vue').PropType<import('./types').TextSize>;
    deleted: BooleanConstructor;
    underline: BooleanConstructor;
    strong: BooleanConstructor;
    italic: BooleanConstructor;
    icon: import('vue').PropType<import('./types').TextIcon>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    tag: StringConstructor;
    type: import('vue').PropType<import('./types').TextType>;
    size: import('vue').PropType<import('./types').TextSize>;
    deleted: BooleanConstructor;
    underline: BooleanConstructor;
    strong: BooleanConstructor;
    italic: BooleanConstructor;
    icon: import('vue').PropType<import('./types').TextIcon>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
}>> & Readonly<{}>, {
    underline: boolean;
    deleted: boolean;
    strong: boolean;
    italic: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
