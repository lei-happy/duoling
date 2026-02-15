import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { TreeTableDataItem, TreeTableColumn } from './types';

/**
 * 属性
 */
export declare const treeTableProps: {
    /** 数据 */
    data: PropType<TreeTableDataItem[]>;
    /** 列配置 */
    columns: PropType<TreeTableColumn[]>;
    /** 表格高度 */
    height: StringConstructor;
    /** 表格样式 */
    tableStyle: PropType<StyleValue>;
    /** 表头样式 */
    headerStyle: PropType<StyleValue>;
    /** 序号列宽度 */
    indexColWidth: {
        type: NumberConstructor;
        default: number;
    };
};
export type TreeTableProps = ExtractPropTypes<typeof treeTableProps>;
