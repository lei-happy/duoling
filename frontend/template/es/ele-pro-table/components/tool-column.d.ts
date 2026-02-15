import { PropType } from 'vue';
import { EleTooltipProps } from '../../ele-app/plus';
import { Columns } from '../../ele-data-table/types';
import { TableLocale } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 提示位置 */
    placement: PropType<EleTooltipProps["placement"]>;
    /** 表格国际化 */
    locale: {
        type: PropType<TableLocale>;
        required: true;
    };
    /** 列数据 */
    columns: PropType<Columns>;
    /** 是否开启列拖拽排序 */
    sortable: BooleanConstructor;
    /** 是否开启开关固定列 */
    allowFixed: BooleanConstructor;
    /** 列配置缓存本地的名称 */
    cacheKey: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:columns": (_columns: Columns, _tableColumns: Columns, _isReset: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 提示位置 */
    placement: PropType<EleTooltipProps["placement"]>;
    /** 表格国际化 */
    locale: {
        type: PropType<TableLocale>;
        required: true;
    };
    /** 列数据 */
    columns: PropType<Columns>;
    /** 是否开启列拖拽排序 */
    sortable: BooleanConstructor;
    /** 是否开启开关固定列 */
    allowFixed: BooleanConstructor;
    /** 列配置缓存本地的名称 */
    cacheKey: StringConstructor;
}>> & Readonly<{
    "onUpdate:columns"?: ((_columns: Columns, _tableColumns: Columns, _isReset: boolean) => any) | undefined;
}>, {
    sortable: boolean;
    allowFixed: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
