declare function __VLS_template(): {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    text: StringConstructor;
    innerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    customStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    icon: import('vue').PropType<import('./types').CopyableIcon>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    copiedIcon: import('vue').PropType<import('./types').CopyableIcon>;
    copiedIconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    copiedIconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    tooltip: {
        type: import('vue').PropType<boolean | import('../ele-app/plus').EleTooltipProps>;
        default: boolean;
    };
    resetAfter: {
        type: NumberConstructor;
        default: number;
    };
    locale: import('vue').PropType<Partial<import('./types').CopyableLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    copy: (_error?: any) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    text: StringConstructor;
    innerStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    customStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    icon: import('vue').PropType<import('./types').CopyableIcon>;
    iconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    iconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    copiedIcon: import('vue').PropType<import('./types').CopyableIcon>;
    copiedIconProps: import('vue').PropType<import('../ele-app/el').ElIconProps>;
    copiedIconStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    tooltip: {
        type: import('vue').PropType<boolean | import('../ele-app/plus').EleTooltipProps>;
        default: boolean;
    };
    resetAfter: {
        type: NumberConstructor;
        default: number;
    };
    locale: import('vue').PropType<Partial<import('./types').CopyableLocale>>;
}>> & Readonly<{
    onCopy?: ((_error?: any) => any) | undefined;
}>, {
    tooltip: boolean | Partial<import('../ele-tooltip/props').TooltipProps>;
    resetAfter: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
