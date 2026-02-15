import { PropType, ExtractPropTypes } from 'vue';
import { CheckboxType, CheckboxOption, CheckboxOptionFunction } from './types';

export { checkboxGroupEmits } from 'element-plus';
/**
 * 属性
 */
export declare const checkboxGroupProps: {
    /** 风格类型 */
    type: PropType<CheckboxType>;
    /** 选项数据 */
    options: PropType<CheckboxOption[] | CheckboxOptionFunction>;
    ariaLabel: StringConstructor;
    modelValue: {
        readonly type: PropType<import('element-plus').CheckboxGroupValueType>;
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
        readonly type: PropType<"" | "default" | "small" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    fill: StringConstructor;
    textColor: StringConstructor;
    tag: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "div";
    };
    validateEvent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    props: {
        readonly type: PropType<{
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
};
export type CheckboxGroupProps = ExtractPropTypes<typeof checkboxGroupProps>;
