import { PropType } from 'vue';
import { CellStyle, CellClass } from '../../ele-data-table/types';
import { ExportDataItem } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 列数据 */
    col: {
        type: PropType<ExportDataItem>;
        required: true;
    };
    /** 列索引 */
    columnIndex: NumberConstructor;
    /** 单元格样式 */
    bodyCellStyle: PropType<CellStyle>;
    /** 单元格类名自定义 */
    bodyCellClass: PropType<CellClass>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 列数据 */
    col: {
        type: PropType<ExportDataItem>;
        required: true;
    };
    /** 列索引 */
    columnIndex: NumberConstructor;
    /** 单元格样式 */
    bodyCellStyle: PropType<CellStyle>;
    /** 单元格类名自定义 */
    bodyCellClass: PropType<CellClass>;
}>> & Readonly<{}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
