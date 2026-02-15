import { EleProFormProps } from '../../ele-app/plusx';
import { ProFormItemProps, ProFormItemTypeData } from '../../ele-pro-form/types';
import { ComponentGroup } from '../types';

/**
 * 判断选项数据是否是数组类型
 * @param item 表单项
 * @param options 选项数据
 */
export declare function isArrayOptions(item?: ProFormItemProps, options?: any): boolean;
/**
 * 生成 ElForm 底栏代码
 * @param config 表单配置数据
 * @param showFooterExpand 是否需要展开收起按钮
 */
export declare function generateFooterCode(config: EleProFormProps, showFooterExpand?: boolean): string;
/**
 * 生成 ElFormItem 所有属性代码
 * @param item 表单项
 * @param indentSize 属性换行的缩进空格数量
 * @param indentChar 上层代码缩进
 */
export declare function generateFormItemProps(item: ProFormItemProps, indentSize?: number, indentChar?: string): string;
/**
 * 生成 ElCol 所有属性代码
 * @param item 表单项
 * @param grid 父级的 grid 属性
 * @param indentSize 属性换行的缩进空格数量
 * @param indentChar 上层代码缩进
 */
export declare function generateColProps(item?: ProFormItemProps, grid?: Record<string, any> | boolean, indentSize?: number, indentChar?: string): string;
/**
 * 生成容器组件和非单标签组件的所有属性代码
 * @param item 表单项
 * @param indentSize 属性换行的缩进空格数量
 * @param indentChar 上层代码缩进
 * @param omitKeys 排除的属性名
 */
export declare function generateComponentProps(item: ProFormItemProps, indentSize?: number, indentChar?: string, omitKeys?: string[]): string;
/**
 * 生成 ElForm 代码时获取组件使用的组件名称
 * @param item 表单项
 * @param componentData 组件库数据
 */
export declare function getItemComponentTag(item: ProFormItemProps, componentData?: ComponentGroup[]): string;
/**
 * 生成展示型组件和单标签组件的完整代码
 * @param item 表单项
 * @param indentSize 属性换行的缩进空格数量
 * @param indentChar 上层代码缩进
 * @param content 展示型组件的文本内容
 * @param componentData 组件库数据
 */
export declare function generateItemComponentCode(item: ProFormItemProps, indentSize: number | undefined, indentChar: string | undefined, content: string | undefined, componentData?: ComponentGroup[]): string;
/**
 * 生成 ElForm 代码时获取 div 容器使用的组件名称
 * @param item 表单项
 */
export declare function getDivTag(item: ProFormItemProps): any;
/**
 * 生成 ElForm 内容代码
 * @param config 表单配置数据
 * @param showFooterExpand 是否需要展开收起按钮
 * @param componentData 组件库数据
 * @param itemTypeData 高级表单组件类型数据
 */
export declare function generateContentCode(config: EleProFormProps, showFooterExpand: boolean | undefined, componentData?: ComponentGroup[], itemTypeData?: ProFormItemTypeData[]): string;
/**
 * 获取上传组件表单验证方法代码
 * @param item 表单项
 */
export declare function getUploadValidatorCode(item: ProFormItemProps): string;
/**
 * 生成 ElForm 验证规则代码
 * @param items 表单项数据
 * @param componentData 组件库数据
 * @param itemTypeData 高级表单组件类型数据
 * @param requiredLang 默认的必填提示文本
 */
export declare function generateRuleCode(items: ProFormItemProps[], componentData?: ComponentGroup[], itemTypeData?: ProFormItemTypeData[], requiredLang?: string): any;
/**
 * 获取生成 ElForm 代码时组件的属性
 * @param item 表单项
 * @param componentData 组件库数据
 * @param itemTypeData 高级表单组件类型数据
 */
export declare function getComponentProps(item: ProFormItemProps, componentData?: ComponentGroup[], itemTypeData?: ProFormItemTypeData[]): {
    [x: string]: any;
};
/**
 * 获取导入代码和变量声明代码
 * @param config 表单配置
 * @param componentData 组件库数据
 */
export declare function getImportAndVarCode(config: EleProFormProps, componentData?: ComponentGroup[]): {
    imports: string[];
    codes: string[];
    proImports: string[];
    proCodes: string[];
};
/**
 * 取消表单项数据的多余属性
 * @param formItems 表单项数据
 * @param componentData 组件库数据
 * @param itemTypeData 高级表单组件类型数据
 */
export declare function getElNormalizeItems(formItems?: ProFormItemProps[], componentData?: ComponentGroup[], itemTypeData?: ProFormItemTypeData[]): ProFormItemProps[];
/**
 * 生成 ElForm 代码
 * @param data 表单配置数据
 * @param componentData 组件库数据
 * @param itemTypeData 高级表单组件类型数据
 * @param requiredLang 默认的必填提示文本
 */
export declare function generateElFormCode(data?: EleProFormProps, componentData?: ComponentGroup[], itemTypeData?: ProFormItemTypeData[], requiredLang?: string): string;
/**
 * 生成 ProForm 代码
 * @param data 表单配置数据
 * @param componentData 组件库数据
 */
export declare function generateProFormCode(data?: EleProFormProps, componentData?: ComponentGroup[]): string;
