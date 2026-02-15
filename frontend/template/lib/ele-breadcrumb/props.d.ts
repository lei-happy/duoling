import { PropType, ExtractPropTypes } from 'vue';
import { BreadcrumbSeparator, BreadcrumbItem } from './types';

/**
 * 属性
 */
export declare const breadcrumbProps: {
    separator: {
        type: PropType<BreadcrumbSeparator>;
        default: string;
    };
    /** 面包屑数据 */
    items: {
        type: PropType<BreadcrumbItem[]>;
        required: boolean;
    };
    separatorIcon: {
        readonly type: PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
};
export type BreadcrumbProps = ExtractPropTypes<typeof breadcrumbProps>;
