declare function __VLS_template(): {
    icon?(_: {}): any;
    title?(_: {}): any;
    default?(_: {}): any;
    action?(_: {}): any;
    closeIcon?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    title: StringConstructor;
    type: import('vue').PropType<import('../ele-app/el').ElAlertProps["type"]>;
    description: {
        type: (BooleanConstructor | StringConstructor)[];
        default: string;
    };
    closable: {
        type: BooleanConstructor;
        default: boolean;
    };
    center: BooleanConstructor;
    closeText: StringConstructor;
    showIcon: BooleanConstructor;
    effect: import('vue').PropType<import('../ele-app/el').ElAlertProps["effect"]>;
    iconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    closeIconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    closeIconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    descriptionStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    transitionName: {
        type: StringConstructor;
        default: string;
    };
}>, {
    handleClose: (e: MouseEvent) => void;
    open: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    close: (_e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    title: StringConstructor;
    type: import('vue').PropType<import('../ele-app/el').ElAlertProps["type"]>;
    description: {
        type: (BooleanConstructor | StringConstructor)[];
        default: string;
    };
    closable: {
        type: BooleanConstructor;
        default: boolean;
    };
    center: BooleanConstructor;
    closeText: StringConstructor;
    showIcon: BooleanConstructor;
    effect: import('vue').PropType<import('../ele-app/el').ElAlertProps["effect"]>;
    iconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    closeIconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    closeIconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    bodyStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    titleStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    descriptionStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    transitionName: {
        type: StringConstructor;
        default: string;
    };
}>> & Readonly<{
    onClose?: ((_e: MouseEvent) => any) | undefined;
}>, {
    description: string | boolean;
    closable: boolean;
    showIcon: boolean;
    center: boolean;
    transitionName: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
