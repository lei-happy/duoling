import { SetupContext, VNode } from 'vue';
import { TableV2SortOrder } from 'element-plus';
import { DataKey, DataItem, Column, Columns, Sorter, Filter, FilterValue, OrderValue, TableSize, RowKey, RowSelectable, TreeProps, ShowOverflowTooltip, SpanMethod, ColumnIndex, SummaryMethod } from '../ele-data-table/types';
import { VirtualColumn, VirtualColumns, BodyColumns, HeaderColumn, HeaderRows, ColSize, CustomRenderProps, SortBy, TreeTableProps, CellSpan, CellParams, VirtualRow } from './types';

/**
 * 获取行高
 * @param size 表格尺寸
 * @param rowHeight 自定义行高
 */
export declare function getRowHeight(size?: TableSize, rowHeight?: number): number;
/**
 * 获取列的唯一值
 * @param column 列配置
 */
export declare function getColKey(column?: Column): string;
/**
 * 获取数字类型的尺寸
 * @param size 字符或数字类型的尺寸
 * @param defaultValue 默认值
 */
export declare function getNumberSize<T extends number | undefined>(size?: string | number, defaultValue?: T): number | T;
/**
 * 获取表格高度
 * @param height 自定义高度
 * @param maxHeight 最大高度
 * @param minHeight 最小高度
 * @param wrapHeight 容器高度
 */
export declare function getTableHeight(height: string | number | undefined, maxHeight: string | number | undefined, minHeight: number, wrapHeight: number): number;
/**
 * 计算固定列需要显示阴影的位置
 * @param cols 列配置
 */
export declare function computeFixedCols(cols: VirtualColumns): void;
/**
 * 生成表头和主体列配置
 * @param columns 列配置
 * @param cols 用于存放主体列
 * @param rows 用于存放表头列
 * @param level 多级表头时当前级别
 * @param parentRowCol 多级表头时父表头列
 */
export declare function generateRowCols(columns: Columns, cols: BodyColumns, rows: HeaderRows, level: number, parentRowCol?: HeaderColumn): void;
/**
 * 分析列配置
 * @param columns 列配置
 */
export declare function analyseColumns(columns: Columns | undefined): {
    cols: BodyColumns;
    rows: HeaderRows;
};
/**
 * 分配列宽
 * @param col 列属性
 * @param tableWidth 表格宽度
 * @param colsWidth 已知的列总计宽度
 * @param colsMinWidth 剩余列总计最小宽度
 */
export declare function getColWidth(col: VirtualColumn, tableWidth: number, colsWidth: number, colsMinWidth: number): number;
/**
 * 计算左右固定列浮动位置
 * @param cols 列配置
 * @param colSizes 全部列宽
 */
export declare function computeFixedPositions(cols: VirtualColumns, colSizes: ColSize[]): void;
/**
 * 计算列宽和固定列浮动位置
 * @param cols 主体列
 * @param rows 表头行
 * @param wrapWidth 容器宽度
 */
export declare function computeColSizes(cols: VirtualColumns, rows: HeaderRows, wrapWidth: number): {
    width: number;
    colSizes: ColSize[];
    rowSizes: ColSize[][];
    sumWidth: number;
};
/**
 * 判断表格列尺寸是否改变
 * @param colSizes 当前所有列尺寸
 * @param newSizes 新的所有列尺寸
 */
export declare function colSizesIsChanged(colSizes: ColSize[], newSizes: ColSize[]): boolean;
/**
 * 生成 ElTableV2 格式的列配置
 * @param bodyCols 主体列配置
 * @param colSizes 列尺寸数据
 */
export declare function getTableColumns(bodyCols: BodyColumns, colSizes: ColSize[]): Partial<import('element-plus/es/components/table-v2/index').Column<DataItem>>[];
/**
 * 处理表格数据
 * @param data 数据
 * @param hasExpandCol 是否有展开列
 * @param childrenName 树表格子级数据字段名
 * @param hasChildrenName 树表格是否有子级字段名
 * @param rowKey 数据唯一值字段名
 * @param selectable 控制行是否可选中的方法
 */
export declare function transformTableData(data: DataItem[] | undefined, hasExpandCol: boolean, childrenName: string, hasChildrenName: string, rowKey: RowKey, selectable?: RowSelectable | null): VirtualRow[];
/**
 * 获取值对应的数据
 * @param key 值
 * @param data 表格数据
 * @param rowKey 数据值字段名
 * @param childrenField 子级字段名
 */
export declare function getRowByKey<T extends DataItem | VirtualRow>(key: DataKey, data: T[], rowKey?: RowKey, childrenField?: string): T | undefined;
/**
 * 获取平铺后的数据值和数据
 * @param data 表格数据
 * @param rowKey 数据值字段名
 * @param childrenField 子级字段名
 */
export declare function getKeysAndList<T extends DataItem | VirtualRow>(data?: T[], rowKey?: RowKey, childrenField?: string): [DataKey[], T[]];
/**
 * 判断是否自适应行高
 * @param hasExpandCol 是否有展开行
 * @param bodyCols 主体列配置
 * @param showOverflowTooltip 全局溢出提示属性
 */
export declare function isAutoRowHeight(hasExpandCol: boolean, bodyCols: BodyColumns, showOverflowTooltip: ShowOverflowTooltip): boolean;
/**
 * 单元格渲染组件(用于同时支持插槽和返回 VNode 的自定义渲染函数)
 * @param props 属性
 * @param ctx SetupContext
 */
export declare function CellRender(props: CustomRenderProps, ctx: SetupContext): VNode[] | undefined;
/**
 * 获取表头点击后的排序值
 * @param current 当前排序值
 * @param col 点击的列
 */
export declare function getSortBy(current?: SortBy, col?: Column): SortBy | undefined;
/**
 * 获取排序值对应的枚举
 * @param order 排序值
 */
export declare function getSortOrder(order?: OrderValue): TableV2SortOrder | undefined;
/**
 * 获取排序枚举对应的值
 * @param sort 排序枚举
 */
export declare function getOrderValue(sort?: TableV2SortOrder): OrderValue | undefined;
/**
 * 获取默认排序
 * @param defaultSort 默认排序值
 */
export declare function getDefaultSort(defaultSort?: Sorter): SortBy | undefined;
/**
 * 获取默认排序状态
 * @param defaultSort 默认排序值
 * @param columns 列配置
 */
export declare function getDefaultSorter(defaultSort?: Sorter, columns?: Columns): Sorter | undefined;
/**
 * 获取默认筛选
 * @param columns 列配置
 */
export declare function getDefaultFiltered(columns?: Columns): Filter;
/**
 * 获取列筛选值
 * @param col 列配置
 * @param filtered 当前筛选值
 */
export declare function getColFiltered(col?: Column, filtered?: Filter): FilterValue;
/**
 * 获取判断多选是否可选择的方法
 * @param cols 列配置
 */
export declare function getSelectableFunction(cols: BodyColumns): ((row: any, index: number) => boolean) | null | undefined;
/**
 * 获取嵌套数据配置项
 * @param treeProps 嵌套数据配置项
 */
export declare function getTreeProps(treeProps?: TreeProps): TreeTableProps;
/**
 * 获取序号列值
 * @param rowIndex 行索引
 * @param index 自定义起始索引
 * @param pageIndex 表格分页起始索引
 */
export declare function getIndexValue(rowIndex: number, index?: ColumnIndex, pageIndex?: number): number;
/**
 * 获取单元格的跨行和跨列
 * @param column 列配置
 * @param columnIndex 列索引
 * @param row 行数据
 * @param rowIndex 行索引
 * @param spanMethod 跨行跨列方法
 */
export declare function getCellSpan(params: CellParams, spanMethod?: SpanMethod): CellSpan;
/**
 * 获取自定义的合计列
 * @param summaryMethod 自定义方法
 * @param bodyCols 表格主体列配置
 * @param data 表格数据
 */
export declare function getUserSums(summaryMethod?: SummaryMethod, bodyCols?: BodyColumns, data?: DataItem[]): (string | VNode)[] | undefined;
/**
 * 计算列合计值
 * @param data 表格数据
 * @param prop 列字段名称
 * @param index 列索引
 * @param sumText 第一列文本
 */
export declare function getSumValue(data?: DataItem[], prop?: string, index?: number, sumText?: string): string;
/**
 * 获取原始列配置
 * @param columns 列配置
 * @param key 列的 key
 * @param dataKey 列的 dataKey
 */
export declare function getColumnByKey(columns?: Columns, key?: string, dataKey?: string): Column | undefined;
/**
 * 尺寸取整
 * @param size 尺寸
 */
export declare function floorSize(size: number): number;
/**
 * 判断单元格是否溢出
 * @param cell 单元格节点
 */
export declare function cellIsOverflow(cell: HTMLElement): boolean;
/**
 * 获取排序对比值
 * @param sortMethod 自定义的排序方法
 * @param a 排序数据
 * @param b 排序比较数据
 * @param prop 排序字段名
 */
export declare function getSortCompareValue(sortMethod: Column['sortMethod'], a: DataItem, b: DataItem, prop?: string): number;
