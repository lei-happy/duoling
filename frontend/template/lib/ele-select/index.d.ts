import { ElSelectInstance } from '../ele-app/el';
import { SelectOption } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    options: import('vue').PropType<SelectOption[] | import('./types').SelectOptionFunction>;
    ariaLabel: StringConstructor;
    emptyValues: ArrayConstructor;
    valueOnClear: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => string | number | boolean | Function) | (() => string | number | boolean | Function | null) | ((new (...args: any[]) => string | number | boolean | Function) | (() => string | number | boolean | Function | null))[], unknown, unknown, undefined, boolean>;
    name: StringConstructor;
    id: StringConstructor;
    modelValue: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => string | number | boolean | Record<string, any> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[]) | (() => import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[] | null) | ((new (...args: any[]) => string | number | boolean | Record<string, any> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[]) | (() => import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[] | null))[], unknown, unknown, undefined, boolean>;
    autocomplete: import('element-plus/es/utils/index').EpPropFinalized<StringConstructor, unknown, unknown, string, boolean>;
    automaticDropdown: BooleanConstructor;
    size: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "" | "small" | "default" | "large", never>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    effect: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => string) | (() => import('element-plus/es/components/popper/index').PopperEffect) | ((new (...args: any[]) => string) | (() => import('element-plus/es/components/popper/index').PopperEffect))[], unknown, unknown, string, boolean>;
    disabled: BooleanConstructor;
    clearable: BooleanConstructor;
    filterable: BooleanConstructor;
    allowCreate: BooleanConstructor;
    loading: BooleanConstructor;
    popperClass: import('element-plus/es/utils/index').EpPropFinalized<StringConstructor, unknown, unknown, string, boolean>;
    popperStyle: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | import('vue').CSSProperties) | (() => string | import('vue').CSSProperties) | ((new (...args: any[]) => string | import('vue').CSSProperties) | (() => string | import('vue').CSSProperties))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperOptions: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => Partial<import('element-plus').Options>) | (() => Partial<import('element-plus').Options>) | ((new (...args: any[]) => Partial<import('element-plus').Options>) | (() => Partial<import('element-plus').Options>))[], unknown, unknown, () => Partial<import('element-plus').Options>, boolean>;
    remote: BooleanConstructor;
    loadingText: StringConstructor;
    noMatchText: StringConstructor;
    noDataText: StringConstructor;
    remoteMethod: {
        readonly type: import('vue').PropType<(query: string) => void>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    filterMethod: {
        readonly type: import('vue').PropType<(query: string) => void>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    multiple: BooleanConstructor;
    multipleLimit: import('element-plus/es/utils/index').EpPropFinalized<NumberConstructor, unknown, unknown, number, boolean>;
    placeholder: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    defaultFirstOption: BooleanConstructor;
    reserveKeyword: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    valueKey: import('element-plus/es/utils/index').EpPropFinalized<StringConstructor, unknown, unknown, string, boolean>;
    collapseTags: BooleanConstructor;
    collapseTagsTooltip: BooleanConstructor;
    maxCollapseTags: import('element-plus/es/utils/index').EpPropFinalized<NumberConstructor, unknown, unknown, number, boolean>;
    teleported: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, true, boolean>;
    persistent: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    clearIcon: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component) | ((new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    fitInputWidth: BooleanConstructor;
    suffixIcon: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component) | ((new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    tagType: {
        default: string;
        type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "primary" | "success" | "warning" | "info" | "danger", unknown>>;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    tagEffect: {
        default: string;
        type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "dark" | "light" | "plain", unknown>>;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    validateEvent: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    remoteShowSuffix: BooleanConstructor;
    showArrow: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    offset: import('element-plus/es/utils/index').EpPropFinalized<NumberConstructor, unknown, unknown, number, boolean>;
    placement: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => "left" | "right" | "top" | "bottom" | "auto" | "auto-start" | "auto-end" | "top-start" | "top-end" | "bottom-start" | "bottom-end" | "right-start" | "right-end" | "left-start" | "left-end") | (() => import('element-plus').Placement) | ((new (...args: any[]) => "left" | "right" | "top" | "bottom" | "auto" | "auto-start" | "auto-end" | "top-start" | "top-end" | "bottom-start" | "bottom-end" | "right-start" | "right-end" | "left-start" | "left-end") | (() => import('element-plus').Placement))[], import('element-plus').Placement, unknown, string, boolean>;
    fallbackPlacements: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => import('element-plus').Placement[]) | (() => import('element-plus').Placement[]) | ((new (...args: any[]) => import('element-plus').Placement[]) | (() => import('element-plus').Placement[]))[], unknown, unknown, string[], boolean>;
    tabindex: import('element-plus/es/utils/index').EpPropFinalized<(NumberConstructor | StringConstructor)[], unknown, unknown, number, boolean>;
    appendTo: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | HTMLElement) | (() => import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement) | ((new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement))[], unknown, unknown>) | ((new (...args: any[]) => string | HTMLElement) | (() => import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement) | ((new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement))[], unknown, unknown>))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    props: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => import('element-plus/es/components/select-v2/src/useProps').Props) | (() => import('element-plus/es/components/select-v2/src/useProps').Props) | ((new (...args: any[]) => import('element-plus/es/components/select-v2/src/useProps').Props) | (() => import('element-plus/es/components/select-v2/src/useProps').Props))[], unknown, unknown, () => Required<import('element-plus/es/components/select-v2/src/useProps').Props>, boolean>;
}>, {
    reloadOptions: (params?: any) => void;
    selectRef: import('vue').Ref<ElSelectInstance, ElSelectInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    clear: () => void;
    focus: (_e: FocusEvent) => void;
    blur: (_e: FocusEvent) => void;
    "visible-change": (_visible: boolean) => void;
    "update:modelValue": (_value: any) => void;
    change: (_value: any) => void;
    "remove-tag": (_value: any) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    options: import('vue').PropType<SelectOption[] | import('./types').SelectOptionFunction>;
    ariaLabel: StringConstructor;
    emptyValues: ArrayConstructor;
    valueOnClear: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => string | number | boolean | Function) | (() => string | number | boolean | Function | null) | ((new (...args: any[]) => string | number | boolean | Function) | (() => string | number | boolean | Function | null))[], unknown, unknown, undefined, boolean>;
    name: StringConstructor;
    id: StringConstructor;
    modelValue: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => string | number | boolean | Record<string, any> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[]) | (() => import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[] | null) | ((new (...args: any[]) => string | number | boolean | Record<string, any> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[]) | (() => import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[] | null))[], unknown, unknown, undefined, boolean>;
    autocomplete: import('element-plus/es/utils/index').EpPropFinalized<StringConstructor, unknown, unknown, string, boolean>;
    automaticDropdown: BooleanConstructor;
    size: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "" | "small" | "default" | "large", never>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    effect: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => string) | (() => import('element-plus/es/components/popper/index').PopperEffect) | ((new (...args: any[]) => string) | (() => import('element-plus/es/components/popper/index').PopperEffect))[], unknown, unknown, string, boolean>;
    disabled: BooleanConstructor;
    clearable: BooleanConstructor;
    filterable: BooleanConstructor;
    allowCreate: BooleanConstructor;
    loading: BooleanConstructor;
    popperClass: import('element-plus/es/utils/index').EpPropFinalized<StringConstructor, unknown, unknown, string, boolean>;
    popperStyle: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | import('vue').CSSProperties) | (() => string | import('vue').CSSProperties) | ((new (...args: any[]) => string | import('vue').CSSProperties) | (() => string | import('vue').CSSProperties))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperOptions: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => Partial<import('element-plus').Options>) | (() => Partial<import('element-plus').Options>) | ((new (...args: any[]) => Partial<import('element-plus').Options>) | (() => Partial<import('element-plus').Options>))[], unknown, unknown, () => Partial<import('element-plus').Options>, boolean>;
    remote: BooleanConstructor;
    loadingText: StringConstructor;
    noMatchText: StringConstructor;
    noDataText: StringConstructor;
    remoteMethod: {
        readonly type: import('vue').PropType<(query: string) => void>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    filterMethod: {
        readonly type: import('vue').PropType<(query: string) => void>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    multiple: BooleanConstructor;
    multipleLimit: import('element-plus/es/utils/index').EpPropFinalized<NumberConstructor, unknown, unknown, number, boolean>;
    placeholder: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    defaultFirstOption: BooleanConstructor;
    reserveKeyword: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    valueKey: import('element-plus/es/utils/index').EpPropFinalized<StringConstructor, unknown, unknown, string, boolean>;
    collapseTags: BooleanConstructor;
    collapseTagsTooltip: BooleanConstructor;
    maxCollapseTags: import('element-plus/es/utils/index').EpPropFinalized<NumberConstructor, unknown, unknown, number, boolean>;
    teleported: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, true, boolean>;
    persistent: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    clearIcon: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component) | ((new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    fitInputWidth: BooleanConstructor;
    suffixIcon: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component) | ((new (...args: any[]) => (string | import('vue').Component) & {}) | (() => string | import('vue').Component))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    tagType: {
        default: string;
        type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "primary" | "success" | "warning" | "info" | "danger", unknown>>;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    tagEffect: {
        default: string;
        type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "dark" | "light" | "plain", unknown>>;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    validateEvent: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    remoteShowSuffix: BooleanConstructor;
    showArrow: import('element-plus/es/utils/index').EpPropFinalized<BooleanConstructor, unknown, unknown, boolean, boolean>;
    offset: import('element-plus/es/utils/index').EpPropFinalized<NumberConstructor, unknown, unknown, number, boolean>;
    placement: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => "left" | "right" | "top" | "bottom" | "auto" | "auto-start" | "auto-end" | "top-start" | "top-end" | "bottom-start" | "bottom-end" | "right-start" | "right-end" | "left-start" | "left-end") | (() => import('element-plus').Placement) | ((new (...args: any[]) => "left" | "right" | "top" | "bottom" | "auto" | "auto-start" | "auto-end" | "top-start" | "top-end" | "bottom-start" | "bottom-end" | "right-start" | "right-end" | "left-start" | "left-end") | (() => import('element-plus').Placement))[], import('element-plus').Placement, unknown, string, boolean>;
    fallbackPlacements: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => import('element-plus').Placement[]) | (() => import('element-plus').Placement[]) | ((new (...args: any[]) => import('element-plus').Placement[]) | (() => import('element-plus').Placement[]))[], unknown, unknown, string[], boolean>;
    tabindex: import('element-plus/es/utils/index').EpPropFinalized<(NumberConstructor | StringConstructor)[], unknown, unknown, number, boolean>;
    appendTo: {
        readonly type: import('vue').PropType<import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | HTMLElement) | (() => import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement) | ((new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement))[], unknown, unknown>) | ((new (...args: any[]) => string | HTMLElement) | (() => import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement) | ((new (...args: any[]) => string | HTMLElement) | (() => string | HTMLElement))[], unknown, unknown>))[], unknown, unknown>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    props: import('element-plus/es/utils/index').EpPropFinalized<(new (...args: any[]) => import('element-plus/es/components/select-v2/src/useProps').Props) | (() => import('element-plus/es/components/select-v2/src/useProps').Props) | ((new (...args: any[]) => import('element-plus/es/components/select-v2/src/useProps').Props) | (() => import('element-plus/es/components/select-v2/src/useProps').Props))[], unknown, unknown, () => Required<import('element-plus/es/components/select-v2/src/useProps').Props>, boolean>;
}>> & Readonly<{
    onClear?: (() => any) | undefined;
    onFocus?: ((_e: FocusEvent) => any) | undefined;
    onBlur?: ((_e: FocusEvent) => any) | undefined;
    "onVisible-change"?: ((_visible: boolean) => any) | undefined;
    "onUpdate:modelValue"?: ((_value: any) => any) | undefined;
    onChange?: ((_value: any) => any) | undefined;
    "onRemove-tag"?: ((_value: any) => any) | undefined;
}>, {
    effect: import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string) | (() => import('element-plus/es/components/popper/index').PopperEffect) | ((new (...args: any[]) => string) | (() => import('element-plus/es/components/popper/index').PopperEffect))[], unknown, unknown>;
    valueKey: string;
    modelValue: import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | number | boolean | Record<string, any> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[]) | (() => import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[] | null) | ((new (...args: any[]) => string | number | boolean | Record<string, any> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[]) | (() => import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown> | import('element-plus/es/utils/index').EpPropMergeType<(ObjectConstructor | BooleanConstructor | NumberConstructor | StringConstructor)[], unknown, unknown>[] | null))[], unknown, unknown>;
    placement: import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => "left" | "right" | "top" | "bottom" | "auto" | "auto-start" | "auto-end" | "top-start" | "top-end" | "bottom-start" | "bottom-end" | "right-start" | "right-end" | "left-start" | "left-end") | (() => import('element-plus').Placement) | ((new (...args: any[]) => "left" | "right" | "top" | "bottom" | "auto" | "auto-start" | "auto-end" | "top-start" | "top-end" | "bottom-start" | "bottom-end" | "right-start" | "right-end" | "left-start" | "left-end") | (() => import('element-plus').Placement))[], import('element-plus').Placement, unknown>;
    popperClass: string;
    teleported: import('element-plus/es/utils/index').EpPropMergeType<BooleanConstructor, unknown, unknown>;
    fitInputWidth: boolean;
    disabled: boolean;
    autocomplete: string;
    clearable: boolean;
    tabindex: import('element-plus/es/utils/index').EpPropMergeType<(NumberConstructor | StringConstructor)[], unknown, unknown>;
    validateEvent: import('element-plus/es/utils/index').EpPropMergeType<BooleanConstructor, unknown, unknown>;
    loading: boolean;
    offset: number;
    valueOnClear: import('element-plus/es/utils/index').EpPropMergeType<(new (...args: any[]) => string | number | boolean | Function) | (() => string | number | boolean | Function | null) | ((new (...args: any[]) => string | number | boolean | Function) | (() => string | number | boolean | Function | null))[], unknown, unknown>;
    filterable: boolean;
    collapseTags: boolean;
    maxCollapseTags: number;
    collapseTagsTooltip: boolean;
    fallbackPlacements: import('element-plus').Placement[];
    tagType: import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "primary" | "success" | "warning" | "info" | "danger", unknown>;
    tagEffect: import('element-plus/es/utils/index').EpPropMergeType<StringConstructor, "dark" | "light" | "plain", unknown>;
    persistent: import('element-plus/es/utils/index').EpPropMergeType<BooleanConstructor, unknown, unknown>;
    props: import('element-plus/es/components/select-v2/src/useProps').Props;
    popperOptions: Partial<import('element-plus').Options>;
    showArrow: import('element-plus/es/utils/index').EpPropMergeType<BooleanConstructor, unknown, unknown>;
    automaticDropdown: boolean;
    allowCreate: boolean;
    remote: boolean;
    multiple: boolean;
    multipleLimit: number;
    defaultFirstOption: boolean;
    reserveKeyword: import('element-plus/es/utils/index').EpPropMergeType<BooleanConstructor, unknown, unknown>;
    remoteShowSuffix: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
