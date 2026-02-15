import { ElePaginationProps } from '../ele-app/plus';
import { DataItem, Column, Columns, Sorter, Filter, TableSize, TreeProps, RowKey, SpanMethod, SummaryMethod } from '../ele-data-table/types';
import { Pages, Orders, Filters, OrderItem, RequestOption, ResponseOption, TablePagination, DatasourceResult, ResponseResult, ReloadDataResult, ColItem, ProProps, ExportBodyNode, ExportDataItem, ExportDataResult, CacheKey, TableLocale } from './types';

/**
 * 合并复合属性
 * @param props 属性
 * @param globalProps 全局属性
 */
export declare function mergeProps<T extends Record<keyof any, any>>(props?: ProProps<T> | null, globalProps?: ProProps<T> | null): ProProps<T>;
/**
 * 获取分页组件属性
 * @param size 表格尺寸
 * @param pagination 分页组件属性
 * @param globalPagination 全局配置分页组件属性
 * @param pageProps 分页相关的属性
 */
export declare function getPaginationProps(size: TableSize, pagination: boolean | TablePagination | undefined, globalPagination: boolean | TablePagination | undefined, pageProps?: Pick<ElePaginationProps, 'total' | 'pageSize' | 'currentPage' | 'hasNext'>): ElePaginationProps | null;
/**
 * 获取默认页码
 * @param pagination 分页组件属性
 * @param globalPagination 全局配置分页组件属性
 */
export declare function getTablePage(pagination: boolean | TablePagination | undefined, globalPagination: boolean | TablePagination | undefined): number;
/**
 * 获取默认每页数量
 * @param pagination 分页组件属性
 * @param globalPagination 全局配置分页组件属性
 */
export declare function getTableLimit(pagination: boolean | TablePagination | undefined, globalPagination: boolean | TablePagination | undefined): number;
/**
 * 判断是否开启自动修正页码
 * @param pagination 分页组件属性
 * @param globalPagination 全局配置分页组件属性
 */
export declare function isAutoAmend(pagination: boolean | TablePagination | undefined, globalPagination: boolean | TablePagination | undefined): boolean;
/**
 * 获取表格默认尺寸
 * @param cacheKey 本地缓存的键名
 * @param size 表格尺寸
 * @param globalSize 全局配置尺寸
 */
export declare function getTableSize(cacheKey?: string, size?: TableSize, globalSize?: TableSize): TableSize;
/**
 * 获取默认筛选条件
 * @param columns 表格的列
 */
export declare function getDefaultFilter(columns?: Columns): Filter;
/**
 * 获取请求参数名称
 * @param globalRequest 全局配置
 * @param request 当前配置
 */
export declare function getRequestName(globalRequest?: RequestOption, request?: RequestOption): RequestOption;
/**
 * 获取响应参数名称
 * @param globalResponse 全局响应参数配置
 * @param response 响应参数配置
 */
export declare function getResponseName(globalResponse?: ResponseOption, response?: ResponseOption): ResponseOption;
/**
 * 获取排序方式封装
 * @param sorter 排序方式
 */
export declare function getOrderItems(sorter?: Sorter): OrderItem[];
/**
 * 生成请求的排序参数
 * @param sorter 排序方式
 * @param request 请求参数配置
 * @param globalRequest 全局请求参数配置
 */
export declare function getRequestOrders(sorter?: Sorter, request?: RequestOption, globalRequest?: RequestOption): Orders;
/**
 * 生成请求的筛选参数
 * @param filter 筛选条件
 */
export declare function getRequestFilters(filter?: Filter): Filters;
/**
 * 生成请求的分页参数
 * @param page 页码
 * @param limit 每页数量
 * @param request 请求参数配置
 * @param globalRequest 全局请求参数配置
 */
export declare function getRequestPages(page: number, limit: number, request?: RequestOption, globalRequest?: RequestOption): Pages;
/**
 * 获取数据源请求结果
 * @param result 数据源请求的原始数据
 * @param response 响应参数配置
 * @param globalResponse 全局响应参数配置
 * @param lazy 表格是否开启懒加载
 * @param treeOpt 树形表格字段名配置
 */
export declare function getResponseResult(result: DatasourceResult, response?: ResponseOption, globalResponse?: ResponseOption, lazy?: boolean, treeOpt?: TreeProps): ResponseResult;
/**
 * 树形懒加载时数据增加可展开的字段标识
 * @param data 请求数据
 * @param lazy 表格是否开启懒加载
 * @param treeProps 树形表格字段名配置
 */
export declare function getResponseData(data?: DataItem[] | null, lazy?: boolean, treeProps?: TreeProps): DataItem[] | undefined;
/**
 * 排序数据
 * @param datasource 数据源
 * @param sorter 排序方式
 */
export declare function sortData(datasource?: DataItem[], sorter?: Sorter): DataItem[];
/**
 * 前端分页排序
 * @param datasource 数据源
 * @param sorter 排序方式
 * @param page 页码
 * @param limit 每页数量
 */
export declare function reloadData(datasource?: DataItem[], sorter?: Sorter, page?: number, limit?: number): ReloadDataResult;
/**
 * 获取列配置标识
 * @param column 列数据
 */
export declare function getColId(column: Column): string | undefined;
/**
 * 获取初始显示的列数据
 * @param columns 列数据
 * @param cacheColsWidth 缓存的列宽
 */
export declare function getInitColumns(columns: Columns, cacheColsWidth?: ColItem[]): Columns;
/**
 * 获取初始显示的列数据
 * @param columns 列数据
 * @param cacheKey 缓存名称
 * @param sortable 是否可排序
 */
export declare function getInitCacheColumns(columns: Columns, cacheKey?: string, sortable?: boolean): Columns;
/**
 * 获取显示的列配置
 * @param columns 原始列数据
 * @param cols 列配置数据
 * @param sortable 是否进行排序
 * @param isHideInCol 用于排序时计算不显示在配置中的列
 * @param filter 强制过滤的列
 * @param reserveUnchecked 是否保留未选中的列
 * @param cacheColsWidth 缓存的列宽
 */
export declare function getCheckedColumns(columns: Columns | undefined, cols: ColItem[], sortable: boolean | undefined, isHideInCol?: (item: Column) => boolean | undefined, filter?: (item: Column) => boolean, reserveUnchecked?: boolean, cacheColsWidth?: ColItem[]): Columns;
/**
 * 获取列展示列表数据
 * @param columns 列配置
 * @param locale 国际化
 * @param filter 过滤列的方法
 * @param cacheCols 缓存的列展示列表数据
 * @param sortFixed 是否对固定列排序
 * @param cancelFixed 是否取消固定列
 * @param cacheColsWidth 缓存的列宽
 */
export declare function getColItems(columns: Columns | undefined, locale: TableLocale, filter?: (item: Column) => boolean, cacheCols?: ColItem[], sortFixed?: boolean, cancelFixed?: boolean, cacheColsWidth?: ColItem[]): {
    cols: ColItem[];
    checkAll: boolean;
    indeterminate: boolean;
};
/**
 * 获取表格密度缓存的名称
 * @param cacheKey 缓存的名称
 */
export declare function getSizeCacheKey(cacheKey: string): string;
/**
 * 获取列配置缓存的名称
 * @param cacheKey 缓存的名称
 */
export declare function getColsCacheKey<T extends CacheKey>(cacheKey: T): T;
/**
 * 获取表格列宽缓存的名称
 * @param cacheKey 缓存的名称
 */
export declare function getColsWidthCacheKey(cacheKey: string): string;
/**
 * 获取导出的列配置缓存的名称
 * @param cacheKey 缓存的名称
 */
/**
 * 获取导出的列宽缓存的名称
 * @param cacheKey 缓存的名称
 */
/**
 * 获取打印的列配置缓存的名称
 * @param cacheKey 缓存的名称
 */
/**
 * 获取打印的列宽缓存的名称
 * @param cacheKey 缓存的名称
 */
/**
 * 获取缓存的列配置下拉列表数据
 * @param cacheKey 缓存的名称
 */
export declare function getCacheCols(cacheKey?: string): ColItem[] | undefined;
/**
 * 获取缓存的表格密度
 * @param cacheKey 缓存的名称
 */
export declare function getCacheSize(cacheKey?: string): TableSize;
/**
 * 获取缓存的列宽
 * @param cacheKey 缓存的名称
 */
export declare function getCacheColsWidth(cacheKey?: string): ColItem[] | undefined;
/**
 * 获取列对应的缓存的列宽
 * @param cacheColsWidth 缓存的列宽
 * @param column 列配置
 */
export declare function getCacheColWidth(cacheColsWidth?: ColItem[], column?: Column): number | string | undefined;
/**
 * 缓存列宽
 * @param width 列宽
 * @param column 列配置
 * @param cacheKey 缓存的名称
 */
export declare function cacheColWidth(width: number, column?: Column, cacheKey?: string): void;
/**
 * 获取 rowKey
 * @param rowKey 自定义 rowKey
 */
export declare function getRowKey(rowKey?: RowKey): string | ((row: DataItem) => string);
/**
 * 导出获取单元格文本
 * @param column 列配置
 * @param row 行数据
 * @param index 行索引
 * @param pageIndex 序号列起始索引
 */
export declare function getCellText(column: Column | undefined, row: DataItem, index: number, pageIndex?: number): string | number | boolean | Record<string, any> | Array<any>;
/**
 * 导出获取表头单元格文本
 * @param column 列配置
 * @param index 行索引
 */
export declare function getHeaderCellText(column: Column | undefined, index: number): string;
/**
 * 获取主体数据封装节点
 * @param data 数据
 * @param childrenField 子级字段名
 * @param level 树形所处深度
 * @param parents 父级节点
 */
export declare function getExportBodyNode(data: DataItem[], childrenField?: string, level?: number, parents?: ExportBodyNode[]): {
    depth: number;
    nodes: ExportBodyNode[];
};
/**
 * 获取导出的数据
 * @param data 元数据
 * @param columns 列配置
 * @param spanMethod 单元格合并方法
 * @param pageIndex 序号列起始索引
 * @param showSummary 是否显示合计行
 * @param sumText 合计行文本
 * @param summaryMethod 合计行自定义方法
 * @param childrenField 子级字段名
 * @param showTreeIndex 是否显示层级序号
 * @param showHeader 是否显示表头
 */
export declare function getExportData(data: DataItem[], columns: Columns, spanMethod?: SpanMethod, pageIndex?: number, showSummary?: boolean, sumText?: string, summaryMethod?: SummaryMethod, childrenField?: string, showTreeIndex?: boolean, showHeader?: boolean): ExportDataResult;
/**
 * 导出 csv 文件
 * @param fileName 文件名
 * @param headerData 表头数据
 * @param bodyData 主体数据
 * @param footerData 表尾数据
 */
export declare function exportCSV(fileName: string, headerData: ExportDataItem[][], bodyData: ExportDataItem[][], footerData: ExportDataItem[][]): void;
/**
 * 导出判断列是否显示
 * @param item 列配置
 */
export declare function columnsExportFilter(item: Column): boolean;
/**
 * 打印判断列是否显示
 * @param item 列配置
 */
export declare function columnsPrintFilter(item: Column): boolean;
/**
 * 列配置判断列是否显示
 * @param item 列配置
 */
export declare function columnsSettingFilter(item: Column): boolean;
