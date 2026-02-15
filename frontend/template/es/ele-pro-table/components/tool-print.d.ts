import { PropType } from 'vue';
import { StyleValue } from '../../ele-app/types';
import { EleModalProps, ElePrinterProps, EleTableProps } from '../../ele-app/plus';
import { Columns, DataItem, SpanMethod, SummaryMethod, CellStyle, CellClass, HeaderCellStyle, HeaderCellClass, TreeProps } from '../../ele-data-table/types';
import { TableLocale, ExportDataType, BeforeExport, ExportPlugin, Datasource, FetchFunction, TableExportParams, GetDatasourceResultFunction } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: {
    row: DataItem | undefined;
    column: import('../types').Column;
    $index: number;
}) => any>> & Partial<Record<string, (_: any) => any>> & {
    printTop?(_: {
        data: DataItem[];
    }): any;
    printBottom?(_: {
        data: DataItem[];
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 表格国际化 */
    locale: {
        type: PropType<TableLocale>;
        required: true;
    };
    /** 缓存本地的名称 */
    cacheKey: StringConstructor;
    /** 弹窗参数 */
    modalProps: PropType<EleModalProps>;
    /** 打印组件参数 */
    printerProps: PropType<ElePrinterProps>;
    /** 打印表格参数 */
    tableProps: PropType<EleTableProps>;
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
    /** 自定义表格样式 */
    tableStyle: PropType<StyleValue>;
    /** 单元格样式 */
    cellStyle: PropType<CellStyle>;
    /** 单元格类名自定义 */
    cellClassName: PropType<CellClass>;
    /** 单元格样式 */
    headerCellStyle: PropType<HeaderCellStyle>;
    /** 单元格类名自定义 */
    headerCellClassName: PropType<HeaderCellClass>;
    /** 序号列起始索引 */
    pageIndex: NumberConstructor;
    /** 树表字段名 */
    treeProps: PropType<TreeProps>;
    /** 表格请求数据方法 */
    fetch: PropType<FetchFunction>;
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
    /** 打印前的钩子函数 */
    beforePrint: PropType<BeforeExport>;
    /** 打印插件 */
    printPlugin: PropType<ExportPlugin>;
    /** 获取数据源返回结果方法 */
    getDatasourceResult: {
        type: PropType<GetDatasourceResultFunction>;
        required: true;
    };
}>, {
    openModal: () => void;
    closeModal: () => void;
    printData: (params?: TableExportParams) => void;
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
    /** 打印组件参数 */
    printerProps: PropType<ElePrinterProps>;
    /** 打印表格参数 */
    tableProps: PropType<EleTableProps>;
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
    /** 自定义表格样式 */
    tableStyle: PropType<StyleValue>;
    /** 单元格样式 */
    cellStyle: PropType<CellStyle>;
    /** 单元格类名自定义 */
    cellClassName: PropType<CellClass>;
    /** 单元格样式 */
    headerCellStyle: PropType<HeaderCellStyle>;
    /** 单元格类名自定义 */
    headerCellClassName: PropType<HeaderCellClass>;
    /** 序号列起始索引 */
    pageIndex: NumberConstructor;
    /** 树表字段名 */
    treeProps: PropType<TreeProps>;
    /** 表格请求数据方法 */
    fetch: PropType<FetchFunction>;
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
    /** 打印前的钩子函数 */
    beforePrint: PropType<BeforeExport>;
    /** 打印插件 */
    printPlugin: PropType<ExportPlugin>;
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
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
