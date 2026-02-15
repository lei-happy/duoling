/**
 * 标识 js 变量名
 */
export declare class JsVar {
    /** 生成代码时显示的变量名称 */
    name?: string;
    /** 生成 ElForm 代码时添加的声明代码 */
    code?: string;
    /** 生成 ProForm 代码时添加的声明代码 */
    proCode?: string;
    /** 生成 ElForm 代码时添加的导入代码 */
    imports?: string[];
    /** 生成 ProForm 代码时添加的导入代码 */
    proImports?: string[];
    /** 原始数据类型 */
    dataType?: string;
    /** 转 JSON 时标识是 JsVar 对象 */
    __isJsVar: boolean;
    constructor(props: Omit<JsVar, '__isJsVar'>);
}
/**
 * 移除字符串前缀
 * @param content 字符串
 * @param prefix 一个或多个前缀
 */
export declare function removePrefixStr(content: string, prefix: string | string[]): string;
/**
 * JSON 数据值转换 JsVar 对象
 * @param jv JSON 解析后的值
 */
export declare function transformJsVar(jv: any): JsVar | undefined;
