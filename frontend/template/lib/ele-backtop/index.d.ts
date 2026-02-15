declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    target: import('vue').PropType<string | HTMLElement | null>;
    visibilityHeight: {
        type: NumberConstructor;
        default: number;
    };
    bottom: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    right: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    transitionName: {
        type: StringConstructor;
        default: string;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    click: (_e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    target: import('vue').PropType<string | HTMLElement | null>;
    visibilityHeight: {
        type: NumberConstructor;
        default: number;
    };
    bottom: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    right: {
        type: (NumberConstructor | StringConstructor)[];
        default: number;
    };
    transitionName: {
        type: StringConstructor;
        default: string;
    };
}>> & Readonly<{
    onClick?: ((_e: MouseEvent) => any) | undefined;
}>, {
    bottom: string | number;
    right: string | number;
    visibilityHeight: number;
    transitionName: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
