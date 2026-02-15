import { EleProFormProps } from '../ele-app/plusx';
import { ProFormItemProps } from '../ele-pro-form/types';
import { CrudField, SideConfig } from './types';

/**
 * 代码字符串前缀
 */
export declare const codeStringPrefix = "/*__PRO_CRUD__*/";
/**
 * 获取搜索表单默认属性
 */
export declare function getDefaultSearchFormProps(): EleProFormProps;
/**
 * 获取字段数据对应的搜索表单项数据
 * @param fields 字段数据
 */
export declare function getFieldsSearchFormItems(fields?: CrudField[]): ProFormItemProps[];
/**
 * 获取字段数据对应的添加表单项数据
 * @param fields 字段数据
 */
export declare function getFieldsAddFormItems(fields?: CrudField[]): ProFormItemProps[];
/**
 * 获取字段数据对应的修改表单项数据
 * @param fields 字段数据
 */
export declare function getFieldsEditFormItems(fields?: CrudField[]): ProFormItemProps[];
/**
 * 树组件默认的节点值字段名
 */
export declare const defaultTreeNodeKey = "value";
/**
 * 获取树组件数据值的字段名
 * @param sideConfig 侧栏配置
 */
export declare function getTreeValueField(sideConfig?: SideConfig): string;
/**
 * 获取树组件显示文本的字段名
 * @param sideConfig 侧栏配置
 */
export declare function getTreeLabelField(sideConfig?: SideConfig): string;
/**
 * 执行代码字符串
 * @param code 代码字符串
 * @param httpRequest 远程数据源请求工具
 */
export declare function getCodeResult(code: string, httpRequest?: any): any;
