import { ElFormInstance } from '../ele-app/el';
import { ChildrenRenderInstance } from './components/render-util';
import { ProFormItemProps, ProFormItemKey } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    topExtra?(_: {}): any;
    bottomExtra?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    labelWidth: {
        type: (NumberConstructor | StringConstructor)[];
        default: string;
    };
    items: import('vue').PropType<ProFormItemProps[]>;
    grid: import('vue').PropType<boolean | import('../ele-app/el').ElColProps>;
    rowProps: import('vue').PropType<import('../ele-app/el').ElRowProps>;
    footer: BooleanConstructor;
    footerProps: import('vue').PropType<import('../ele-app/el').ElFormItemProps>;
    footerSlots: ObjectConstructor;
    footerColProps: import('vue').PropType<import('../ele-app/el').ElColProps>;
    autoFooterCol: BooleanConstructor;
    footerStyle: import('vue').PropType<import('vue').CSSProperties>;
    submitText: StringConstructor;
    resetText: StringConstructor;
    submitButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    resetButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    showSearchExpand: BooleanConstructor;
    searchExpandButtonProps: import('vue').PropType<import('../ele-app/el').ElLinkProps>;
    searchExpandText: StringConstructor;
    searchShrinkText: StringConstructor;
    searchExpand: BooleanConstructor;
    preventFormSubmit: {
        type: BooleanConstructor;
        default: boolean;
    };
    editable: BooleanConstructor;
    screenSize: import('vue').PropType<import('./types').ScreenSize>;
    activeItemKey: import('vue').PropType<ProFormItemKey>;
    itemTypeData: import('vue').PropType<import('./types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    locale: import('vue').PropType<Partial<import('./types').ProFormLocale>>;
    model: ObjectConstructor;
    rules: {
        readonly type: import('vue').PropType<Partial<Record<string, import('element-plus').FormItemRule | import('element-plus').FormItemRule[]>>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    labelPosition: {
        readonly type: import('vue').PropType<"top" | "left" | "right">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "right";
    };
    requireAsteriskPosition: {
        readonly type: import('vue').PropType<"left" | "right">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "left";
    };
    labelSuffix: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    inline: BooleanConstructor;
    inlineMessage: BooleanConstructor;
    statusIcon: BooleanConstructor;
    showMessage: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    validateOnRuleChange: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    hideRequiredAsterisk: BooleanConstructor;
    scrollToError: BooleanConstructor;
    scrollIntoViewOptions: {
        readonly type: import('vue').PropType<boolean | ScrollIntoViewOptions>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    disabled: BooleanConstructor;
}>, {
    formRef: import('vue').Ref<ElFormInstance, ElFormInstance>;
    childrenRef: import('vue').Ref<ChildrenRenderInstance, ChildrenRenderInstance>;
    getProFormRefs: () => Record<string, any>;
    clearCodeCache: () => void;
    validate: (callback?: import('element-plus').FormValidateCallback) => import('element-plus').FormValidationResult;
    validateField: (props?: import('element-plus').FormItemProp | import('element-plus').FormItemProp[], callback?: import('element-plus').FormValidateCallback) => import('element-plus').FormValidationResult;
    resetFields: (props?: import('element-plus').FormItemProp | import('element-plus').FormItemProp[]) => void;
    clearValidate: (props?: import('element-plus').FormItemProp | import('element-plus').FormItemProp[]) => void;
    scrollToField: (prop: import('element-plus').FormItemProp) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    reset: () => void;
    submit: (_model: Record<string, any>) => void;
    validate: (prop: import('element-plus').FormItemProp, isValid: boolean, message: string) => void;
    "update:activeItemKey": (_activeKey: string | number | symbol) => void;
    updateValue: (_prop: string, _value: unknown) => void;
    "update:searchExpand": (_expand: boolean) => void;
    "update:items": (_items: ProFormItemProps[]) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    labelWidth: {
        type: (NumberConstructor | StringConstructor)[];
        default: string;
    };
    items: import('vue').PropType<ProFormItemProps[]>;
    grid: import('vue').PropType<boolean | import('../ele-app/el').ElColProps>;
    rowProps: import('vue').PropType<import('../ele-app/el').ElRowProps>;
    footer: BooleanConstructor;
    footerProps: import('vue').PropType<import('../ele-app/el').ElFormItemProps>;
    footerSlots: ObjectConstructor;
    footerColProps: import('vue').PropType<import('../ele-app/el').ElColProps>;
    autoFooterCol: BooleanConstructor;
    footerStyle: import('vue').PropType<import('vue').CSSProperties>;
    submitText: StringConstructor;
    resetText: StringConstructor;
    submitButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    resetButtonProps: import('vue').PropType<import('../ele-app/el').ElButtonProps>;
    showSearchExpand: BooleanConstructor;
    searchExpandButtonProps: import('vue').PropType<import('../ele-app/el').ElLinkProps>;
    searchExpandText: StringConstructor;
    searchShrinkText: StringConstructor;
    searchExpand: BooleanConstructor;
    preventFormSubmit: {
        type: BooleanConstructor;
        default: boolean;
    };
    editable: BooleanConstructor;
    screenSize: import('vue').PropType<import('./types').ScreenSize>;
    activeItemKey: import('vue').PropType<ProFormItemKey>;
    itemTypeData: import('vue').PropType<import('./types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    locale: import('vue').PropType<Partial<import('./types').ProFormLocale>>;
    model: ObjectConstructor;
    rules: {
        readonly type: import('vue').PropType<Partial<Record<string, import('element-plus').FormItemRule | import('element-plus').FormItemRule[]>>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    labelPosition: {
        readonly type: import('vue').PropType<"top" | "left" | "right">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "right";
    };
    requireAsteriskPosition: {
        readonly type: import('vue').PropType<"left" | "right">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "left";
    };
    labelSuffix: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    inline: BooleanConstructor;
    inlineMessage: BooleanConstructor;
    statusIcon: BooleanConstructor;
    showMessage: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    validateOnRuleChange: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    hideRequiredAsterisk: BooleanConstructor;
    scrollToError: BooleanConstructor;
    scrollIntoViewOptions: {
        readonly type: import('vue').PropType<boolean | ScrollIntoViewOptions>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    disabled: BooleanConstructor;
}>> & Readonly<{
    onReset?: (() => any) | undefined;
    onSubmit?: ((_model: Record<string, any>) => any) | undefined;
    onValidate?: ((prop: import('element-plus').FormItemProp, isValid: boolean, message: string) => any) | undefined;
    "onUpdate:activeItemKey"?: ((_activeKey: string | number | symbol) => any) | undefined;
    onUpdateValue?: ((_prop: string, _value: unknown) => any) | undefined;
    "onUpdate:searchExpand"?: ((_expand: boolean) => any) | undefined;
    "onUpdate:items"?: ((_items: ProFormItemProps[]) => any) | undefined;
}>, {
    disabled: boolean;
    footer: boolean;
    labelPosition: "top" | "left" | "right";
    requireAsteriskPosition: "left" | "right";
    labelWidth: string | number;
    labelSuffix: string;
    inline: boolean;
    inlineMessage: boolean;
    statusIcon: boolean;
    showMessage: boolean;
    validateOnRuleChange: boolean;
    hideRequiredAsterisk: boolean;
    scrollToError: boolean;
    scrollIntoViewOptions: boolean | ScrollIntoViewOptions;
    editable: boolean;
    searchExpand: boolean;
    autoFooterCol: boolean;
    showSearchExpand: boolean;
    preventFormSubmit: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
