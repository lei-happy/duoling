import { PropType, ExtractPropTypes } from 'vue';
import { TableSize } from '../ele-pro-table/types';

/**
 * 属性
 */
export declare const tableProps: {
    /** 是否为斑马纹 */
    stripe: BooleanConstructor;
    /** 是否带有纵向边框 */
    border: BooleanConstructor;
    /** 尺寸 */
    size: PropType<TableSize>;
    /** 是否有表头 */
    hasHeader: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否有表尾 */
    hasFooter: BooleanConstructor;
    /** 是否使用打印皮肤 */
    printSkin: BooleanConstructor;
};
export type TableProps = ExtractPropTypes<typeof tableProps>;
