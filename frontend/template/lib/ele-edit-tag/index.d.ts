import { ElTagInstance, ElInputInstance } from '../ele-app/el';

declare function __VLS_template(): {
    placeholder?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<string[]>;
    type: import('vue').PropType<import('../ele-app/el').ElTagProps["type"]>;
    hit: BooleanConstructor;
    color: StringConstructor;
    size: import('vue').PropType<import('../ele-app/el').ElTagProps["size"]>;
    effect: import('vue').PropType<import('../ele-app/el').ElTagProps["effect"]>;
    round: BooleanConstructor;
    placeholder: StringConstructor;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    inputTagStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    buttonStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    validator: import('vue').PropType<import('./types').Validator>;
    beforeRemove: import('vue').PropType<import('./types').BeforeRemove>;
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    readonly: BooleanConstructor;
    disabled: BooleanConstructor;
}>, {
    inputTagRef: import('vue').Ref<ElTagInstance, ElTagInstance>;
    inputRef: import('vue').Ref<ElInputInstance, ElInputInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_value?: string[] | undefined) => void;
    change: (_value?: string[] | undefined) => void;
    itemClick: (_index: number, _value: string) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<string[]>;
    type: import('vue').PropType<import('../ele-app/el').ElTagProps["type"]>;
    hit: BooleanConstructor;
    color: StringConstructor;
    size: import('vue').PropType<import('../ele-app/el').ElTagProps["size"]>;
    effect: import('vue').PropType<import('../ele-app/el').ElTagProps["effect"]>;
    round: BooleanConstructor;
    placeholder: StringConstructor;
    inputStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    inputTagStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    buttonStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    itemStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    validator: import('vue').PropType<import('./types').Validator>;
    beforeRemove: import('vue').PropType<import('./types').BeforeRemove>;
    tooltipProps: import('vue').PropType<import('../ele-app/plus').EleTooltipProps>;
    readonly: BooleanConstructor;
    disabled: BooleanConstructor;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_value?: string[] | undefined) => any) | undefined;
    onChange?: ((_value?: string[] | undefined) => any) | undefined;
    onItemClick?: ((_index: number, _value: string) => any) | undefined;
}>, {
    disabled: boolean;
    readonly: boolean;
    round: boolean;
    hit: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
