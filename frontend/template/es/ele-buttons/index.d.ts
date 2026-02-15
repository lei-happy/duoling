declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    items: import('vue').PropType<import('./types').ButtonItem[]>;
    divider: import('vue').PropType<boolean | import('../ele-app/el').ElDividerProps>;
    type: import('vue').PropType<import('./types').ButtonItemType>;
    gap: {
        type: (NumberConstructor | BooleanConstructor)[];
        default: null;
    };
    wrap: {
        type: BooleanConstructor;
        default: null;
    };
    modalFooter: BooleanConstructor;
    locale: import('vue').PropType<Partial<import('./types').ButtonsLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_command: any, _e?: MouseEvent | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    items: import('vue').PropType<import('./types').ButtonItem[]>;
    divider: import('vue').PropType<boolean | import('../ele-app/el').ElDividerProps>;
    type: import('vue').PropType<import('./types').ButtonItemType>;
    gap: {
        type: (NumberConstructor | BooleanConstructor)[];
        default: null;
    };
    wrap: {
        type: BooleanConstructor;
        default: null;
    };
    modalFooter: BooleanConstructor;
    locale: import('vue').PropType<Partial<import('./types').ButtonsLocale>>;
}>> & Readonly<{
    onItemClick?: ((_command: any, _e?: MouseEvent | undefined) => any) | undefined;
}>, {
    gap: number | boolean;
    wrap: boolean;
    modalFooter: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
