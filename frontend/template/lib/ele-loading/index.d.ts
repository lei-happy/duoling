declare function __VLS_template(): {
    spinner?(_: {}): any;
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    loading: BooleanConstructor;
    text: StringConstructor;
    blur: BooleanConstructor;
    size: import('vue').PropType<import('./types').LoadingSize>;
    spinnerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    textStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    plain: BooleanConstructor;
    type: {
        type: import('vue').PropType<import('./types').LoadingType>;
        default: string;
    };
    background: StringConstructor;
    spinner: StringConstructor;
    svgViewBox: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    loading: BooleanConstructor;
    text: StringConstructor;
    blur: BooleanConstructor;
    size: import('vue').PropType<import('./types').LoadingSize>;
    spinnerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    textStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    plain: BooleanConstructor;
    type: {
        type: import('vue').PropType<import('./types').LoadingType>;
        default: string;
    };
    background: StringConstructor;
    spinner: StringConstructor;
    svgViewBox: StringConstructor;
}>> & Readonly<{}>, {
    type: import('./types').LoadingType;
    loading: boolean;
    blur: boolean;
    plain: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
