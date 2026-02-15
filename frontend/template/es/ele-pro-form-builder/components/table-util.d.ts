import { ProFormItemKey, ProFormItemProps } from '../../ele-pro-form/types';
import { ComponentGroup, TableGridData, TableGridRow, UpdateItemsResult } from '../types';

/**
 * 获取单元格对应的表格表单项
 * @param tdFormItemId 单元格表单项 id
 * @param formItems 当前的全部表单项数据
 */
export declare function getTableFormItemByTd(tdFormItemId: string, formItems?: ProFormItemProps[]): {
    tableFormItem: ProFormItemProps | undefined;
    tdFormItem: ProFormItemProps | undefined;
    trItemIndex: number | undefined;
};
/**
 * 获取单元格的全部内容表单项
 * @param tdFormItemId 单元格表单项 id
 * @param formItems 当前的全部表单项数据
 */
export declare function getTableCellContents(tdFormItemId?: ProFormItemKey, formItems?: ProFormItemProps[]): ProFormItemProps[];
/**
 * 生成用于处理表格跨行跨列的数据
 * @param tableRowFormItems 表格所有行表单项
 */
export declare function generateTableGrid(tableRowFormItems?: ProFormItemProps[]): TableGridData;
/**
 * 表格数据拆分单元格合并
 * @param gridData 表格封装后的数据
 * @param tdFormItemId 单元格表单项 id
 */
export declare function splitTableGridCell(gridData: TableGridRow[], tdFormItemId: ProFormItemKey): void;
/**
 * 重新计算表格数据的跨行跨列
 * @param gridData 表格封装后的数据
 * @param precorrect 是否先纠正之前的跨行跨列
 */
export declare function computeTableGridSpan(gridData: TableGridRow[], precorrect?: boolean): void;
/**
 * 表格数据删除所有空行
 * @param gridData 表格封装后的数据
 */
export declare function deleteTableGridEmptyRow(gridData: TableGridRow[]): (string | number | symbol)[];
/**
 * 表格数据删除所有空列
 * @param gridData 表格封装后的数据
 */
export declare function deleteTableGridEmptyCol(gridData: TableGridRow[]): (string | number | symbol)[];
/**
 * 表格数据删除整行
 * @param gridData 表格封装后的数据
 * @param deleteRowIndex 要删除的行索引
 */
export declare function deleteTableGridRow(gridData: TableGridRow[], deleteRowIndex: number): (string | number | symbol)[];
/**
 * 表格数据删除整列
 * @param gridData 表格封装后的数据
 * @param deleteColIndex 要删除的列索引
 */
export declare function deleteTableGridCol(gridData: TableGridRow[], deleteColIndex: number): (string | number | symbol)[];
/**
 * 获取表格数据添加和删除以及拆分后导致跨行跨列变化的影响
 * @param gridData 表格封装后的数据
 * @param formItems 当前的全部表单项数据
 * @param componentData 组件库数据
 */
export declare function getTableGridEffects(gridData: TableGridRow[], formItems?: ProFormItemProps[], componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 添加表格行时获取插入的位置索引
 * @param gridData 表格封装后的数据
 * @param tdFormItem 指定位置对应的单元格表单项
 * @param position 指定位置的上方或下方添加, 默认下方
 */
export declare function getTableRowInsertIndex(gridData: TableGridRow[], tdFormItem?: ProFormItemProps, position?: -1): {
    insertIndex: number;
    trFormItemIndex?: undefined;
    tdFormItemIndex?: undefined;
} | {
    trFormItemIndex: number;
    insertIndex: number;
    tdFormItemIndex: number;
};
/**
 * 添加表格列时获取插入的位置索引
 * @param gridData 表格封装后的数据
 * @param tdFormItem 指定位置对应的单元格表单项
 * @param position 指定位置的左侧或右侧添加, 默认右侧
 */
export declare function getTableColInsertIndex(gridData: TableGridRow[], tdFormItem?: ProFormItemProps, position?: -1): {
    insertIndex: number;
    tdFormItemIndex?: undefined;
    trFormItemIndex?: undefined;
} | {
    tdFormItemIndex: number;
    insertIndex: number;
    trFormItemIndex: number;
};
/**
 * 表格添加行时生成需要的数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param tdFormItem 指定位置对应的单元格表单项
 * @param position 指定位置的上方或下方添加, 默认下方
 * @param componentData 组件库数据
 */
export declare function generateAddTableRowData(tableFormItem: ProFormItemProps, formItems?: ProFormItemProps[], tdFormItem?: ProFormItemProps, position?: -1, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 表格添加列时生成需要的数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param tdFormItem 指定位置对应的单元格表单项
 * @param position 指定位置的左侧或右侧添加, 默认右侧
 * @param componentData 组件库数据
 */
export declare function generateAddTableColData(tableFormItem: ProFormItemProps, formItems?: ProFormItemProps[], tdFormItem?: ProFormItemProps, position?: -1, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 获取表格拆分单元格的影响数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param tdFormItem 单元格表单项
 * @param componentData 组件库数据
 */
export declare function getTableSplitEffects(tableFormItem: ProFormItemProps, formItems: ProFormItemProps[] | undefined, tdFormItem: ProFormItemProps, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 获取表格删除整行的影响数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param deleteRowIndex 要删除的行索引
 * @param componentData 组件库数据
 */
export declare function getTableDeleteRowEffects(tableFormItem: ProFormItemProps, formItems: ProFormItemProps[] | undefined, deleteRowIndex: number, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 获取表格删除整列的影响数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param tdFormItem 要删除所在列的单元格表单项
 * @param componentData 组件库数据
 */
export declare function getTableDeleteColEffects(tableFormItem: ProFormItemProps, formItems: ProFormItemProps[] | undefined, tdFormItem: ProFormItemProps, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 获取表格合并右侧的影响数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param tdFormItem 单元格表单项
 * @param componentData 组件库数据
 */
export declare function getTableMergeRightEffects(tableFormItem: ProFormItemProps, formItems: ProFormItemProps[] | undefined, tdFormItem: ProFormItemProps, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 获取表格合并下方的影响数据
 * @param tableFormItem 表格表单项
 * @param formItems 当前的全部表单项数据
 * @param tdFormItem 单元格表单项
 * @param componentData 组件库数据
 */
export declare function getTableMergeBelowEffects(tableFormItem: ProFormItemProps, formItems: ProFormItemProps[] | undefined, tdFormItem: ProFormItemProps, componentData?: ComponentGroup[]): UpdateItemsResult;
