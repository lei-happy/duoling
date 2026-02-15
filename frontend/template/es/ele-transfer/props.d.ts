import { PropType, ExtractPropTypes } from 'vue';
import { TransferDataItem, TransferDataFunction } from './types';

export { transferEmits } from 'element-plus';
/**
 * 属性
 */
export declare const transferProps: {
    /** 数据 */
    data: PropType<TransferDataItem[] | TransferDataFunction>;
    titles: {
        readonly type: PropType<[string, string]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    buttonTexts: {
        readonly type: PropType<[string, string]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    filterPlaceholder: StringConstructor;
    filterMethod: {
        readonly type: PropType<(query: string, item: import('element-plus').TransferDataItem) => boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    leftDefaultChecked: {
        readonly type: PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    rightDefaultChecked: {
        readonly type: PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    renderContent: {
        readonly type: PropType<import('element-plus').renderContent>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    modelValue: {
        readonly type: PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    format: {
        readonly type: PropType<import('element-plus').TransferFormat>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    filterable: BooleanConstructor;
    props: {
        readonly type: PropType<import('element-plus').TransferPropsAlias>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {
            label: "label";
            key: "key";
            disabled: "disabled";
        };
    };
    targetOrder: {
        readonly type: PropType<"push" | "unshift" | "original">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "original";
    };
    validateEvent: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
};
export type TransferProps = ExtractPropTypes<typeof transferProps>;
