import { ProFormItemKey, ProFormItemProps } from '../../ele-pro-form/types';
import { ComponentGroup, UpdateItemsResult, AddChildrenItemAction } from '../types';

/**
 * 添加子级时生成需要的数据
 * @param triggerItem 触发添加的表单项
 * @param triggerParent 触发添加的表单项父级
 * @param triggerItemIndex 触发添加的表单项在父级中的位置
 * @param actionType 添加类型
 * @param formItems 当前的全部表单项数据
 * @param position 触发位置的上方(左侧)或下方(右侧)添加, 默认下方(左侧)
 * @param componentData 组件库数据
 */
export declare function generateAddChildData(triggerItem: ProFormItemProps, triggerParent: ProFormItemProps | undefined, triggerItemIndex: number | undefined, actionType: AddChildrenItemAction | undefined, formItems?: ProFormItemProps[], position?: -1, componentData?: ComponentGroup[]): UpdateItemsResult;
/**
 * 表单项数据生成新的 id
 * @param items 表单项数据
 * @param formItems 当前的全部表单项数据
 * @param overwriteProp prop 是否也重新生成
 */
export declare function itemsGenerateNewKey(items?: ProFormItemProps[] | ProFormItemProps, formItems?: ProFormItemProps[], overwriteProp?: boolean): void;
/**
 * 复制表单项时生成需要的数据
 * @param formItemId 表单项 id
 * @param formItems 当前的全部表单项数据
 */
export declare function generateCopyItemData(formItemId: ProFormItemKey, formItems?: ProFormItemProps[]): UpdateItemsResult;
