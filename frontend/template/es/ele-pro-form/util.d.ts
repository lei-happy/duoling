import { ProFormItemProps, ProFormItemTypeData } from './types';
import { getValue, setValue, mergeValue, cloneDeep, ChildrenRender } from './components/render-util';

export { sortableGroupName } from './components/render-core';
export { setValue, getValue, mergeValue, cloneDeep, ChildrenRender };
/**
 * 判断表单项是否是容器类型
 * @param item 表单项
 * @param itemTypeData 高级表单组件类型数据
 */
export declare function isContainerType(item: ProFormItemProps, itemTypeData?: ProFormItemTypeData[]): boolean;
/**
 * 获取表单数据初始值
 * @param items 表单项数据
 * @param itemTypeData 高级表单组件类型数据
 * @param excludeUndefined 排除空值
 */
export declare function getFormInitValue(items?: ProFormItemProps[], itemTypeData?: ProFormItemTypeData[], excludeUndefined?: boolean): Record<string, any>;
