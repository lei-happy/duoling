import { PropType } from 'vue';
import { EleModalProps } from '../../ele-app/plus';
import { Columns, DataItem, SpanMethod, SummaryMethod, TreeProps } from '../../ele-data-table/types';
import { TableLocale, ExportDataType, BeforeExport, ExportPlugin, Datasource, FetchFunction, TableExportParams, GetDatasourceResultFunction } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 表格国际化 */
    locale: {
        type: PropType<TableLocale>;
        required: true;
    };
    /** 缓存本地的名称 */
    cacheKey: StringConstructor;
    /** 弹窗参数 */
    modalProps: PropType<EleModalProps>;
    /** 列数据 */
    columns: PropType<Columns>;
    /** 表格选中数据 */
    selections: PropType<DataItem[]>;
    /** 表格当前页数据 */
    pageData: PropType<DataItem[]>;
    /** 表格全部数据 */
    datasource: PropType<Datasource>;
    /** 单元格合并行列方法 */
    spanMethod: PropType<SpanMethod>;
    /** 表格是否有表头 */
    tableHeader: BooleanConstructor;
    /** 是否显示合计行 */
    showSummary: BooleanConstructor;
    /** 合计行文本 */
    sumText: StringConstructor;
    /** 合计行自定义方法 */
    summaryMethod: PropType<SummaryMethod>;
    /** 序号列起始索引 */
    pageIndex: NumberConstructor;
    /** 树表字段名 */
    treeProps: PropType<TreeProps>;
    /** 表格请求数据方法 */
    fetch: PropType<FetchFunction>;
    /** 默认文件名 */
    defaultFileName: {
        type: StringConstructor;
        default: string;
    };
    /** 默认数据类型 */
    defaultDataType: {
        type: PropType<ExportDataType>;
        default: string;
    };
    /** 默认是否勾选表尾 */
    defaultShowFooter: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 默认是否勾选层级序号 */
    defaultShowTreeIndex: BooleanConstructor;
    /** 导出前的钩子函数 */
    beforeExport: PropType<BeforeExport>;
    /** 导出插件 */
    exportPlugin: PropType<ExportPlugin>;
    /** 获取数据源返回结果方法 */
    getDatasourceResult: {
        type: PropType<GetDatasourceResultFunction>;
        required: true;
    };
}>, {
    openModal: () => void;
    closeModal: () => void;
    exportData: (params?: TableExportParams) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 表格国际化 */
    locale: {
        type: PropType<TableLocale>;
        required: true;
    };
    /** 缓存本地的名称 */
    cacheKey: StringConstructor;
    /** 弹窗参数 */
    modalProps: PropType<EleModalProps>;
    /** 列数据 */
    columns: PropType<Columns>;
    /** 表格选中数据 */
    selections: PropType<DataItem[]>;
    /** 表格当前页数据 */
    pageData: PropType<DataItem[]>;
    /** 表格全部数据 */
    datasource: PropType<Datasource>;
    /** 单元格合并行列方法 */
    spanMethod: PropType<SpanMethod>;
    /** 表格是否有表头 */
    tableHeader: BooleanConstructor;
    /** 是否显示合计行 */
    showSummary: BooleanConstructor;
    /** 合计行文本 */
    sumText: StringConstructor;
    /** 合计行自定义方法 */
    summaryMethod: PropType<SummaryMethod>;
    /** 序号列起始索引 */
    pageIndex: NumberConstructor;
    /** 树表字段名 */
    treeProps: PropType<TreeProps>;
    /** 表格请求数据方法 */
    fetch: PropType<FetchFunction>;
    /** 默认文件名 */
    defaultFileName: {
        type: StringConstructor;
        default: string;
    };
    /** 默认数据类型 */
    defaultDataType: {
        type: PropType<ExportDataType>;
        default: string;
    };
    /** 默认是否勾选表尾 */
    defaultShowFooter: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 默认是否勾选层级序号 */
    defaultShowTreeIndex: BooleanConstructor;
    /** 导出前的钩子函数 */
    beforeExport: PropType<BeforeExport>;
    /** 导出插件 */
    exportPlugin: PropType<ExportPlugin>;
    /** 获取数据源返回结果方法 */
    getDatasourceResult: {
        type: PropType<GetDatasourceResultFunction>;
        required: true;
    };
}>> & Readonly<{}>, {
    showSummary: boolean;
    tableHeader: boolean;
    defaultDataType: ExportDataType;
    defaultShowFooter: boolean;
    defaultShowTreeIndex: boolean;
    defaultFileName: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
