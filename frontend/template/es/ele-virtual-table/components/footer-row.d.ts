import { PropType } from 'vue';
import { SummaryMethod } from '../../ele-data-table/types';
import { BodyColumns, ColSize, VirtualRow } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 表格主体列配置 */
    bodyCols: {
        type: PropType<BodyColumns>;
        required: true;
    };
    /** 表格数据 */
    tableData: {
        type: PropType<VirtualRow[]>;
        required: true;
    };
    /** 表格主体列宽 */
    colSizes: {
        type: PropType<ColSize[]>;
        required: true;
    };
    /** 表格主体所有列合计宽度 */
    sumWidth: NumberConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
    /** 合计行文本 */
    sumText: StringConstructor;
    /** 合计行自定义方法 */
    summaryMethod: PropType<SummaryMethod>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    mouseenter: (_e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 表格主体列配置 */
    bodyCols: {
        type: PropType<BodyColumns>;
        required: true;
    };
    /** 表格数据 */
    tableData: {
        type: PropType<VirtualRow[]>;
        required: true;
    };
    /** 表格主体列宽 */
    colSizes: {
        type: PropType<ColSize[]>;
        required: true;
    };
    /** 表格主体所有列合计宽度 */
    sumWidth: NumberConstructor;
    /** 表格行高 */
    rowHeight: NumberConstructor;
    /** 合计行文本 */
    sumText: StringConstructor;
    /** 合计行自定义方法 */
    summaryMethod: PropType<SummaryMethod>;
}>> & Readonly<{
    onMouseenter?: ((_e: MouseEvent) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
