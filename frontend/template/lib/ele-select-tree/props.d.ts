import { PropType, ExtractPropTypes } from 'vue';
import { TreeComponentProps } from 'element-plus/es/components/tree/src/tree.type';
import { SelectTreeData, SelectTreeDataFunction } from './types';

export declare const elTreeProps: {
    data: {
        type: ArrayConstructor;
        default: () => never[];
    };
    emptyText: {
        type: StringConstructor;
    };
    renderAfterExpand: {
        type: BooleanConstructor;
        default: boolean;
    };
    nodeKey: StringConstructor;
    checkStrictly: BooleanConstructor;
    defaultExpandAll: BooleanConstructor;
    expandOnClickNode: {
        type: BooleanConstructor;
        default: boolean;
    };
    checkOnClickNode: BooleanConstructor;
    checkDescendants: {
        type: BooleanConstructor;
        default: boolean;
    };
    autoExpandParent: {
        type: BooleanConstructor;
        default: boolean;
    };
    defaultCheckedKeys: PropType<TreeComponentProps["defaultCheckedKeys"]>;
    defaultExpandedKeys: PropType<TreeComponentProps["defaultExpandedKeys"]>;
    currentNodeKey: PropType<string | number>;
    renderContent: FunctionConstructor;
    showCheckbox: {
        type: BooleanConstructor;
        default: boolean;
    };
    draggable: {
        type: BooleanConstructor;
        default: boolean;
    };
    allowDrag: FunctionConstructor;
    allowDrop: FunctionConstructor;
    props: {
        type: PropType<TreeComponentProps["props"]>;
        default: () => {
            children: string;
            label: string;
            disabled: string;
        };
    };
    lazy: {
        type: BooleanConstructor;
        default: boolean;
    };
    highlightCurrent: BooleanConstructor;
    load: PropType<TreeComponentProps["load"]>;
    filterNodeMethod: PropType<TreeComponentProps["filterNodeMethod"]>;
    accordion: BooleanConstructor;
    indent: {
        type: NumberConstructor;
        default: number;
    };
    icon: {
        type: (StringConstructor | FunctionConstructor | ObjectConstructor)[];
    };
};
/**
 * 属性
 */
export declare const selectTreeProps: {
    /** 数据 */
    data: PropType<SelectTreeData | SelectTreeDataFunction>;
    emptyText: {
        type: StringConstructor;
    };
    renderAfterExpand: {
        type: BooleanConstructor;
        default: boolean;
    };
    nodeKey: StringConstructor;
    checkStrictly: BooleanConstructor;
    defaultExpandAll: BooleanConstructor;
    expandOnClickNode: {
        type: BooleanConstructor;
        default: boolean;
    };
    checkOnClickNode: BooleanConstructor;
    checkDescendants: {
        type: BooleanConstructor;
        default: boolean;
    };
    autoExpandParent: {
        type: BooleanConstructor;
        default: boolean;
    };
    defaultCheckedKeys: PropType<TreeComponentProps["defaultCheckedKeys"]>;
    defaultExpandedKeys: PropType<TreeComponentProps["defaultExpandedKeys"]>;
    currentNodeKey: PropType<string | number>;
    renderContent: FunctionConstructor;
    showCheckbox: {
        type: BooleanConstructor;
        default: boolean;
    };
    draggable: {
        type: BooleanConstructor;
        default: boolean;
    };
    allowDrag: FunctionConstructor;
    allowDrop: FunctionConstructor;
    props: {
        type: PropType<TreeComponentProps["props"]>;
        default: () => {
            children: string;
            label: string;
            disabled: string;
        };
    };
    lazy: {
        type: BooleanConstructor;
        default: boolean;
    };
    highlightCurrent: BooleanConstructor;
    load: PropType<TreeComponentProps["load"]>;
    filterNodeMethod: PropType<TreeComponentProps["filterNodeMethod"]>;
    accordion: BooleanConstructor;
    indent: {
        type: NumberConstructor;
        default: number;
    };
    icon: {
        type: (StringConstructor | FunctionConstructor | ObjectConstructor)[];
    };
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
    options: {
        readonly type: import('vue').PropType<Record<string, any>[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
};
export type SelectTreeProps = ExtractPropTypes<typeof selectTreeProps>;
/**
 * 事件
 */
export declare const selectTreeEmits: {
    'update:modelValue': (_value: any) => boolean;
};
