import { ProFormItemProps, ProFormItemTypeData } from '../../ele-pro-form/types';
import { ComponentGroup } from '../types';

/**
 * 有固定子级的组件类型
 */
export declare const fixedChildTypes: {
    type: string;
    childType: string;
}[];
/**
 * 生成表单项 id
 */
export declare function generateItemKey(): string;
/**
 * 生成表单项 id 并检查重复
 * @param items 当前表单项数据
 * @param keys 新生成还未添加的表单项 id
 */
export declare function generateUniqueItemKey(items?: ProFormItemProps[], keys?: string[]): string;
/**
 * 根据组件类型名称获取对应组件定义
 * @param type 组件类型名称
 * @param componentData 组件库数据
 */
export declare function getComponentItemByType(type: string | undefined, componentData?: ComponentGroup[]): import('../types').ComponentItem | undefined;
/**
 * 深度克隆对象
 * @param data 对象
 * @param excludeUndefined 排除未定义值
 */
export declare function deepCloneObject<T extends Record<string, any>>(data?: T, excludeUndefined?: boolean): T;
/**
 * 生成子级表单项数据
 * @param parentType 父组件类型
 * @param childNo 子组件编号
 * @param childKey 子组件 id
 * @param componentData 组件库数据
 */
export declare function generateChildFormItem(parentType?: string, childNo?: string, childKey?: string, componentData?: ComponentGroup[]): ProFormItemProps;
/**
 * 生成表单项数据
 * @param type 组件类型或组件数据
 * @param formItems 当前的全部表单项数据
 * @param componentData 组件库数据
 * @param itemTypeData 高级表单组件类型数据
 */
export declare function generateBuildFormItem(type: string | undefined, formItems: ProFormItemProps[] | undefined, componentData?: ComponentGroup[], itemTypeData?: ProFormItemTypeData[]): ProFormItemProps | undefined;
/**
 * 获取表单项的属性值和对应的属性配置表单项数据
 * @param item 表单项
 * @param componentData 组件库数据
 */
export declare function getFormDataAndItems(item: ProFormItemProps | undefined, componentData?: ComponentGroup[]): {
    data: Record<string, any>;
    items: ProFormItemProps[];
};
/**
 * 获取数据所有属性的路径数组
 * @param data 数据
 * @param excludeKeys 排除的属性名
 * @param prefix 前缀
 */
export declare function getPropertyPath(data: any, excludeKeys?: string[], prefix?: string): string[];
