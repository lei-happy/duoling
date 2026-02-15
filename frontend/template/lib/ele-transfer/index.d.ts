import { ElTransferInstance } from '../ele-app/el';
import { TransferDataItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    data: import('vue').PropType<TransferDataItem[] | import('./types').TransferDataFunction>;
    titles: {
        readonly type: import('vue').PropType<[string, string]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    buttonTexts: {
        readonly type: import('vue').PropType<[string, string]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    filterPlaceholder: StringConstructor;
    filterMethod: {
        readonly type: import('vue').PropType<(query: string, item: import('element-plus').TransferDataItem) => boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    leftDefaultChecked: {
        readonly type: import('vue').PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    rightDefaultChecked: {
        readonly type: import('vue').PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    renderContent: {
        readonly type: import('vue').PropType<import('element-plus').renderContent>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    modelValue: {
        readonly type: import('vue').PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    format: {
        readonly type: import('vue').PropType<import('element-plus').TransferFormat>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    filterable: BooleanConstructor;
    props: {
        readonly type: import('vue').PropType<import('element-plus').TransferPropsAlias>;
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
        readonly type: import('vue').PropType<"push" | "unshift" | "original">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "original";
    };
    validateEvent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
}>, {
    reloadOptions: (params?: any) => void;
    transferRef: import('vue').Ref<ElTransferInstance, ElTransferInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (value: import('element-plus').TransferKey[]) => void;
    change: (value: import('element-plus').TransferKey[], direction: import('element-plus').TransferDirection, movedKeys: import('element-plus').TransferKey[]) => void;
    "left-check-change": (value: import('element-plus').TransferKey[], movedKeys?: import('element-plus').TransferKey[] | undefined) => void;
    "right-check-change": (value: import('element-plus').TransferKey[], movedKeys?: import('element-plus').TransferKey[] | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    data: import('vue').PropType<TransferDataItem[] | import('./types').TransferDataFunction>;
    titles: {
        readonly type: import('vue').PropType<[string, string]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    buttonTexts: {
        readonly type: import('vue').PropType<[string, string]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    filterPlaceholder: StringConstructor;
    filterMethod: {
        readonly type: import('vue').PropType<(query: string, item: import('element-plus').TransferDataItem) => boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    leftDefaultChecked: {
        readonly type: import('vue').PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    rightDefaultChecked: {
        readonly type: import('vue').PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    renderContent: {
        readonly type: import('vue').PropType<import('element-plus').renderContent>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    modelValue: {
        readonly type: import('vue').PropType<import('element-plus').TransferKey[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => never[];
    };
    format: {
        readonly type: import('vue').PropType<import('element-plus').TransferFormat>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => {};
    };
    filterable: BooleanConstructor;
    props: {
        readonly type: import('vue').PropType<import('element-plus').TransferPropsAlias>;
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
        readonly type: import('vue').PropType<"push" | "unshift" | "original">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "original";
    };
    validateEvent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
}>> & Readonly<{
    "onUpdate:modelValue"?: ((value: import('element-plus').TransferKey[]) => any) | undefined;
    onChange?: ((value: import('element-plus').TransferKey[], direction: import('element-plus').TransferDirection, movedKeys: import('element-plus').TransferKey[]) => any) | undefined;
    "onLeft-check-change"?: ((value: import('element-plus').TransferKey[], movedKeys?: import('element-plus').TransferKey[] | undefined) => any) | undefined;
    "onRight-check-change"?: ((value: import('element-plus').TransferKey[], movedKeys?: import('element-plus').TransferKey[] | undefined) => any) | undefined;
}>, {
    modelValue: import('element-plus').TransferKey[];
    validateEvent: boolean;
    filterable: boolean;
    props: import('element-plus').TransferPropsAlias;
    format: import('element-plus').TransferFormat;
    titles: [string, string];
    buttonTexts: [string, string];
    leftDefaultChecked: import('element-plus').TransferKey[];
    rightDefaultChecked: import('element-plus').TransferKey[];
    targetOrder: "push" | "unshift" | "original";
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
