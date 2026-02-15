import { ElCascaderInstance } from '../ele-app/el';
import { CascaderOption } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    options: import('vue').PropType<CascaderOption[] | import('./types').CascaderOptionFunction>;
    multiple: BooleanConstructor;
    emptyValues: ArrayConstructor;
    valueOnClear: {
        readonly type: import('vue').PropType<string | number | boolean | Function | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    placeholder: StringConstructor;
    disabled: BooleanConstructor;
    clearable: BooleanConstructor;
    clearIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    filterable: BooleanConstructor;
    filterMethod: {
        readonly type: import('vue').PropType<(node: import('element-plus').CascaderNode, keyword: string) => boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: (node: import('element-plus').CascaderNode, keyword: string) => boolean;
    };
    separator: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    showAllLevels: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    collapseTags: BooleanConstructor;
    maxCollapseTags: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: number;
    };
    collapseTagsTooltip: BooleanConstructor;
    maxCollapseTagsTooltipHeight: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    debounce: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: number;
    };
    beforeFilter: {
        readonly type: import('vue').PropType<(value: string) => boolean | Promise<any>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => true;
    };
    placement: {
        readonly type: import('vue').PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    fallbackPlacements: {
        readonly type: import('vue').PropType<import('element-plus').Placement[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string[];
    };
    popperClass: {
        readonly type: import('vue').PropType<string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | any[] | {
            [x: string]: boolean;
        })[])[])[])[])[])[])[])[])[])[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperStyle: {
        readonly type: import('vue').PropType<import('vue').StyleValue>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    effect: {
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    tagType: {
        default: string;
        type: import('vue').PropType<"primary" | "success" | "warning" | "info" | "danger">;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    tagEffect: {
        default: string;
        type: import('vue').PropType<"dark" | "light" | "plain">;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    validateEvent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    persistent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    showCheckedStrategy: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    checkOnClickNode: BooleanConstructor;
    showPrefix: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    modelValue: {
        readonly type: import('vue').PropType<import('element-plus').CascaderValue | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    props: {
        readonly type: import('vue').PropType<import('element-plus').CascaderProps>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => import('element-plus').CascaderProps;
    };
}>, {
    reloadOptions: (params?: any) => void;
    cascaderRef: import('vue').Ref<ElCascaderInstance, ElCascaderInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    clear: () => void;
    focus: (evt: FocusEvent) => void;
    blur: (evt: FocusEvent) => void;
    "update:modelValue": (value: import('element-plus').CascaderValue | null | undefined) => void;
    change: (value: import('element-plus').CascaderValue | null | undefined) => void;
    visibleChange: (val: boolean) => void;
    expandChange: (val: import('element-plus').CascaderValue) => void;
    removeTag: (val: import('element-plus').CascaderNodePathValue | import('element-plus').CascaderNodeValue) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    options: import('vue').PropType<CascaderOption[] | import('./types').CascaderOptionFunction>;
    multiple: BooleanConstructor;
    emptyValues: ArrayConstructor;
    valueOnClear: {
        readonly type: import('vue').PropType<string | number | boolean | Function | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: undefined;
    };
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    placeholder: StringConstructor;
    disabled: BooleanConstructor;
    clearable: BooleanConstructor;
    clearIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    filterable: BooleanConstructor;
    filterMethod: {
        readonly type: import('vue').PropType<(node: import('element-plus').CascaderNode, keyword: string) => boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: (node: import('element-plus').CascaderNode, keyword: string) => boolean;
    };
    separator: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    showAllLevels: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    collapseTags: BooleanConstructor;
    maxCollapseTags: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: number;
    };
    collapseTagsTooltip: BooleanConstructor;
    maxCollapseTagsTooltipHeight: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    debounce: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: number;
    };
    beforeFilter: {
        readonly type: import('vue').PropType<(value: string) => boolean | Promise<any>>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => true;
    };
    placement: {
        readonly type: import('vue').PropType<import('element-plus').Placement>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    fallbackPlacements: {
        readonly type: import('vue').PropType<import('element-plus').Placement[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string[];
    };
    popperClass: {
        readonly type: import('vue').PropType<string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | {
            [x: string]: boolean;
        } | (string | any[] | {
            [x: string]: boolean;
        })[])[])[])[])[])[])[])[])[])[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    popperStyle: {
        readonly type: import('vue').PropType<import('vue').StyleValue>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    effect: {
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    tagType: {
        default: string;
        type: import('vue').PropType<"primary" | "success" | "warning" | "info" | "danger">;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    tagEffect: {
        default: string;
        type: import('vue').PropType<"dark" | "light" | "plain">;
        required: false;
        validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    validateEvent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    persistent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    showCheckedStrategy: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    checkOnClickNode: BooleanConstructor;
    showPrefix: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: boolean;
    };
    modelValue: {
        readonly type: import('vue').PropType<import('element-plus').CascaderValue | null>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    props: {
        readonly type: import('vue').PropType<import('element-plus').CascaderProps>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => import('element-plus').CascaderProps;
    };
}>> & Readonly<{
    onClear?: (() => any) | undefined;
    onFocus?: ((evt: FocusEvent) => any) | undefined;
    onBlur?: ((evt: FocusEvent) => any) | undefined;
    "onUpdate:modelValue"?: ((value: import('element-plus').CascaderValue | null | undefined) => any) | undefined;
    onChange?: ((value: import('element-plus').CascaderValue | null | undefined) => any) | undefined;
    onVisibleChange?: ((val: boolean) => any) | undefined;
    onExpandChange?: ((val: import('element-plus').CascaderValue) => any) | undefined;
    onRemoveTag?: ((val: import('element-plus').CascaderNodePathValue | import('element-plus').CascaderNodeValue) => any) | undefined;
}>, {
    effect: import('element-plus').PopperEffect;
    debounce: number;
    placement: import('element-plus').Placement;
    teleported: boolean;
    disabled: boolean;
    clearable: boolean;
    validateEvent: boolean;
    separator: string;
    valueOnClear: string | number | boolean | Function | null;
    filterable: boolean;
    filterMethod: (node: import('element-plus').CascaderNode, keyword: string) => boolean;
    showAllLevels: boolean;
    collapseTags: boolean;
    maxCollapseTags: number;
    collapseTagsTooltip: boolean;
    beforeFilter: (value: string) => boolean | Promise<any>;
    fallbackPlacements: import('element-plus').Placement[];
    tagType: "primary" | "success" | "warning" | "info" | "danger";
    tagEffect: "dark" | "light" | "plain";
    persistent: boolean;
    showCheckedStrategy: string;
    checkOnClickNode: boolean;
    showPrefix: boolean;
    props: import('element-plus').CascaderProps;
    multiple: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
