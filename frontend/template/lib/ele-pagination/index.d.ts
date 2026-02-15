import { ElPaginationInstance } from '../ele-app/el';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    total: import('vue').PropType<import('./types').PaginationTotal>;
    hasNext: {
        type: BooleanConstructor;
        default: boolean;
    };
    type: {
        type: import('vue').PropType<import('./types').PaginationType>;
        default: string;
    };
    isFixedPopper: {
        type: BooleanConstructor;
        default: boolean;
    };
    pageSize: NumberConstructor;
    defaultPageSize: NumberConstructor;
    pageCount: NumberConstructor;
    pagerCount: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 7;
    };
    currentPage: NumberConstructor;
    defaultCurrentPage: NumberConstructor;
    layout: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    pageSizes: {
        readonly type: import('vue').PropType<number[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [10, 20, 30, 40, 50, 100];
    };
    popperClass: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    prevText: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    prevIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    nextText: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    nextIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    small: BooleanConstructor;
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    background: BooleanConstructor;
    disabled: BooleanConstructor;
    hideOnSinglePage: BooleanConstructor;
    appendSizeTo: StringConstructor;
}>, {
    paginationRef: import('vue').Ref<ElPaginationInstance, ElPaginationInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentPage": (_currentPage: number) => void;
    "update:pageSize": (_pageSize: number) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    total: import('vue').PropType<import('./types').PaginationTotal>;
    hasNext: {
        type: BooleanConstructor;
        default: boolean;
    };
    type: {
        type: import('vue').PropType<import('./types').PaginationType>;
        default: string;
    };
    isFixedPopper: {
        type: BooleanConstructor;
        default: boolean;
    };
    pageSize: NumberConstructor;
    defaultPageSize: NumberConstructor;
    pageCount: NumberConstructor;
    pagerCount: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 7;
    };
    currentPage: NumberConstructor;
    defaultCurrentPage: NumberConstructor;
    layout: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    pageSizes: {
        readonly type: import('vue').PropType<number[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [10, 20, 30, 40, 50, 100];
    };
    popperClass: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    prevText: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    prevIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    nextText: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    nextIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    teleported: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    small: BooleanConstructor;
    size: {
        readonly type: import('vue').PropType<"" | "small" | "default" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    background: BooleanConstructor;
    disabled: BooleanConstructor;
    hideOnSinglePage: BooleanConstructor;
    appendSizeTo: StringConstructor;
}>> & Readonly<{
    "onUpdate:currentPage"?: ((_currentPage: number) => any) | undefined;
    "onUpdate:pageSize"?: ((_pageSize: number) => any) | undefined;
}>, {
    small: boolean;
    type: import('./types').PaginationType;
    popperClass: string;
    teleported: boolean;
    disabled: boolean;
    pagerCount: number;
    layout: string;
    pageSizes: number[];
    prevText: string;
    prevIcon: string | import('vue').Component;
    nextText: string;
    nextIcon: string | import('vue').Component;
    background: boolean;
    hideOnSinglePage: boolean;
    hasNext: boolean;
    isFixedPopper: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
