declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    default?(_: {}): any;
    footer?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    cron: StringConstructor;
    title: StringConstructor;
    modalProps: import('vue').PropType<import('../ele-app/plus').EleModalProps>;
    locale: import('vue').PropType<Partial<import('./types').CronBuilderLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    done: (_cron?: string | undefined) => void;
    "update:modelValue": (_value?: boolean | undefined) => void;
    "update:cron": (_cron?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: BooleanConstructor;
    cron: StringConstructor;
    title: StringConstructor;
    modalProps: import('vue').PropType<import('../ele-app/plus').EleModalProps>;
    locale: import('vue').PropType<Partial<import('./types').CronBuilderLocale>>;
}>> & Readonly<{
    onDone?: ((_cron?: string | undefined) => any) | undefined;
    "onUpdate:modelValue"?: ((_value?: boolean | undefined) => any) | undefined;
    "onUpdate:cron"?: ((_cron?: string | undefined) => any) | undefined;
}>, {
    modelValue: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
