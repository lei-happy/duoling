import { ProFormItemProps } from '../ele-pro-form/types';
import { CrudField } from '../ele-crud/types';
import { HeaderRightToolName } from './types';

export declare const codeTips: string;
/**
 * 默认表头工具栏右侧按钮布局
 */
export declare const defaultHeaderRightTools: HeaderRightToolName[];
/**
 * 生成字段 id 并检查重复
 * @param fields 当前字段数据
 * @param keys 新生成还未添加的字段 id
 */
export declare function generateUniqueItemKey(fields?: CrudField[], keys?: string[]): string;
/**
 * 字段数据生成新的 id
 * @param fields 字段数据
 * @param curdFields 当前的全部字段数据
 * @param overwriteProp prop 是否也重新生成
 */
export declare function itemsGenerateNewKey(fields?: CrudField[] | CrudField, curdFields?: CrudField[], overwriteProp?: boolean): void;
/**
 * 页面设置的表单项配置
 */
export declare const defaultPageConfigFormItems: ProFormItemProps[];
/**
 * 字段编辑的表单项配置
 */
export declare const defaultFieldEditFormItems: ProFormItemProps[];
