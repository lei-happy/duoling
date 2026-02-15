import { PropType, ExtractPropTypes } from 'vue';
import { PaginationType, PaginationTotal } from './types';

/**
 * 属性
 */
export declare const paginationProps: {
    /** 总条目数 */
    total: PropType<PaginationTotal>;
    /** 是否还有下一页 */
    hasNext: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 风格 */
    type: {
        type: PropType<PaginationType>;
        default: string;
    };
    /** 每页数量选择下拉是否使用固定定位 */
    isFixedPopper: {
        type: BooleanConstructor;
        default: boolean;
    };
    pageSize: NumberConstructor;
    defaultPageSize: NumberConstructor;
    pageCount: NumberConstructor;
    pagerCount: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 7;
    };
    currentPage: NumberConstructor;
    defaultCurrentPage: NumberConstructor;
    layout: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: string;
    };
    pageSizes: {
        readonly type: PropType<number[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [10, 20, 30, 40, 50, 100];
    };
    popperClass: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    prevText: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    prevIcon: {
        readonly type: PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    nextText: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    nextIcon: {
        readonly type: PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    teleported: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    small: BooleanConstructor;
    size: {
        readonly type: PropType<"" | "default" | "small" | "large">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    background: BooleanConstructor;
    disabled: BooleanConstructor;
    hideOnSinglePage: BooleanConstructor;
    appendSizeTo: StringConstructor;
};
export type PaginationProps = ExtractPropTypes<typeof paginationProps>;
/**
 * 事件
 */
export declare const paginationEmits: {
    /** 更新页码 */
    'update:currentPage': (_currentPage: number) => boolean;
    /** 更新每页数量 */
    'update:pageSize': (_pageSize: number) => boolean;
};
