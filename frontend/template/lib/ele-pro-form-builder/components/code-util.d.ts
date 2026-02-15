import { JsVar } from './code-js-var';

/**
 * 模板引擎
 * @param template 模板
 * @param data 数据
 */
export declare function templateEngine(template: string, data?: {}): string;
/**
 * 转义字符串
 * @param str 字符串
 */
export declare function escapeStr(str: string): string;
/**
 * 判断是否是合法的属性名
 * @param name 属性名
 */
export declare function isValidKey(name: string): boolean;
/**
 * 驼峰转中划线
 * @param name 驼峰风格名称
 */
export declare function kebabCase(name: string): string;
/**
 * 代码增加缩进
 * @param code 代码
 * @param indentChar 缩进字符
 */
export declare function addIndentChar(code?: string, indentChar?: string): string;
/**
 * 对象转 js 字符串
 * @param obj 对象
 * @param singleLine 是否单行显示
 * @param indentSize 多行时缩进空格数量
 * @param transformJsVarFunc 转换 JsVar 对象的方法
 */
export declare function obj2Str(obj: any, singleLine?: boolean, indentSize?: number, transformJsVarFunc?: (jv: any) => JsVar | undefined): any;
/**
 * 生成组件属性的代码
 * @param props 属性
 * @param singleLine 是否单行显示
 * @param indentSize 多行时缩进空格数量
 * @param isAllProps 是否是全部属性, 会考虑标签结束符的换行和缩进
 * @param transformJsVarFunc 转换 JsVar 对象的方法
 */
export declare function generatePropsCode(props?: Record<string, any>, singleLine?: boolean | null, indentSize?: number, isAllProps?: boolean, transformJsVarFunc?: (jv: any) => JsVar | undefined): string;
