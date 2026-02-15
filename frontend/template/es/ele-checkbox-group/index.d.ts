import { ElCheckboxGroupInstance } from '../ele-app/el';
import { CheckboxOption } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    type: import('vue').PropType<import('./types').CheckboxType>;
    options: import('vue').PropType<CheckboxOption[] | import('./types').CheckboxOptionFunction>;
    ariaLabel: StringConstructor;
    modelValue: {
        readonly type: import('vue').PropType<import('element-plus').CheckboxGroupValueType>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    disabled: BooleanConstructor;
    min: NumberConstructor;
    max: NumberConstructor;
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    fill: StringConstructor;
    textColor: StringConstructor;
    tag: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "div";
    };
    validateEvent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    props: {
        readonly type: import('vue').PropType<{
            value?: string;
            label?: string;
            disabled?: string;
        }>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => Required<{
            value?: string;
            label?: string;
            disabled?: string;
        }>;
    };
}>, {
    reloadOptions: (params?: any) => void;
    checkboxGroupRef: import('vue').Ref<ElCheckboxGroupInstance, ElCheckboxGroupInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (val: import('element-plus').CheckboxGroupValueType) => void;
    change: (val: import('element-plus').CheckboxValueType[]) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    type: import('vue').PropType<import('./types').CheckboxType>;
    options: import('vue').PropType<CheckboxOption[] | import('./types').CheckboxOptionFunction>;
    ariaLabel: StringConstructor;
    modelValue: {
        readonly type: import('vue').PropType<import('element-plus').CheckboxGroupValueType>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    disabled: BooleanConstructor;
    min: NumberConstructor;
    max: NumberConstructor;
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    fill: StringConstructor;
    textColor: StringConstructor;
    tag: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "div";
    };
    validateEvent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    props: {
        readonly type: import('vue').PropType<{
            value?: string;
            label?: string;
            disabled?: string;
        }>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => Required<{
            value?: string;
            label?: string;
            disabled?: string;
        }>;
    };
}>> & Readonly<{
    "onUpdate:modelValue"?: ((val: import('element-plus').CheckboxGroupValueType) => any) | undefined;
    onChange?: ((val: import('element-plus').CheckboxValueType[]) => any) | undefined;
}>, {
    modelValue: import('element-plus').CheckboxGroupValueType;
    disabled: boolean;
    validateEvent: boolean;
    tag: string;
    props: {
        value?: string;
        label?: string;
        disabled?: string;
    };
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
