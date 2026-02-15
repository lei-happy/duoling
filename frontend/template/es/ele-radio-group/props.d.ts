import { PropType, ExtractPropTypes } from 'vue';
import { RadioType, RadioOption, RadioOptionFunction } from './types';

export { radioGroupEmits } from 'element-plus';
/**
 * 属性
 */
export declare const radioGroupProps: {
    /** 风格类型 */
    type: PropType<RadioType>;
    /** 选项数据 */
    options: PropType<RadioOption[] | RadioOptionFunction>;
    ariaLabel: StringConstructor;
    id: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    size: {
        readonly type: PropType<"" | "default" | "small" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    disabled: BooleanConstructor;
    modelValue: {
        readonly type: PropType<string | number | boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    fill: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    textColor: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    name: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
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
        readonly type: PropType<import('element-plus').radioOptionProp>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => Required<import('element-plus').radioOptionProp>;
    };
};
export type RadioGroupProps = ExtractPropTypes<typeof radioGroupProps>;
