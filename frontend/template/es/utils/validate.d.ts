/** 格式校验工具 */
/**
 * 手机号正则表达式
 */
export declare const phoneReg: RegExp;
/**
 * 手机号正则表达式(强校验)
 */
export declare const phoneStrongReg: RegExp;
/**
 * 固话正则表达式
 */
export declare const telReg: RegExp;
/**
 * 邮箱正则表达式
 */
export declare const emailReg: RegExp;
/**
 * 网址正则表达式
 */
export declare const urlReg: RegExp;
/**
 * 身份证正则表达式
 */
export declare const identityReg: RegExp;
/**
 * 日期正则表达式
 */
export declare const dateReg: RegExp;
/**
 * 数字正则表达式
 */
export declare const numberReg: RegExp;
/**
 * 整数正则表达式
 */
export declare const integerReg: RegExp;
/**
 * 正整数正则表达式
 */
export declare const positiveIntegerReg: RegExp;
/**
 * 负整数正则表达式
 */
export declare const negativeIntegerReg: RegExp;
/**
 * 非负整数(正整数或0)正则表达式
 */
export declare const nonNegativeIntegerReg: RegExp;
/**
 * 非正整数(负整数或0)正则表达式
 */
export declare const nonPositiveIntegerReg: RegExp;
/**
 * 中文正则表达式
 */
export declare const chineseReg: RegExp;
/**
 * 端口号正则表达式
 */
export declare const portReg: RegExp;
/**
 * IP 正则表达式
 */
export declare const ipReg: RegExp;
/**
 * 经度正则表达式, -180.0 ~ +180.0(整数部分为 0 ~ 180 , 必须输入 1 到 5 位小数)
 */
export declare const longitudeReg: RegExp;
/**
 * 纬度正则表达式, -90.0 ~ +90.0(整数部分为 0 ~ 90, 必须输入 1 到 5 位小数)
 */
export declare const latitudeReg: RegExp;
/**
 * 是否是手机号
 * @param value
 */
export declare function isPhone(value: string): boolean;
/**
 * 是否是手机号(强校验)
 * @param value
 */
export declare function isPhoneStrong(value: string): boolean;
/**
 * 是否为固话
 * @param value
 */
export declare function isTel(value: string): boolean;
/**
 * 是否是邮箱
 * @param value
 */
export declare function isEmail(value: string): boolean;
/**
 * 是否是网址
 * @param value
 */
export declare function isUrl(value: string): boolean;
/**
 * 是否是身份证
 * @param value
 */
export declare function isIdentity(value: string): boolean;
/**
 * 是否是日期
 * @param value
 */
export declare function isDate(value: string): boolean;
/**
 * 是否是数字
 * @param value
 */
export declare function isNumber(value: string): boolean;
/**
 * 是否是整数
 * @param value
 */
export declare function isInteger(value: string): boolean;
/**
 * 是否是正整数
 * @param value
 */
export declare function isPositiveInteger(value: string): boolean;
/**
 * 是否是负整数
 * @param value
 */
export declare function isNegativeInteger(value: string): boolean;
/**
 * 是否是非负整数(正整数或 0)
 * @param value
 */
export declare function isNonNegativeInteger(value: string): boolean;
/**
 * 是否是非正整数(负整数或 0)
 * @param value
 */
export declare function isNonPositiveInteger(value: string): boolean;
/**
 * 是否是中文
 * @param value
 */
export declare function isChinese(value: string): boolean;
/**
 * 是否是端口号
 * @param value
 */
export declare function isPort(value: string): boolean;
/**
 * 是否是 IP
 * @param value
 */
export declare function isIP(value: string): boolean;
/**
 * 是否是经度, -180.0 ~ +180.0(整数部分为 0 ~ 180 , 必须输入 1 到 5 位小数)
 * @param value
 */
export declare function isLongitude(value: string): boolean;
/**
 * 是否是纬度, -90.0 ~ +90.0(整数部分为 0 ~ 90 , 必须输入 1 到 5 位小数)
 * @param value
 */
export declare function isLatitude(value: string): boolean;
/**
 * 验证最小长度, 最大长度
 * @param value
 * @param minLength
 * @param maxLength
 */
export declare function maxMinLength(value: string, minLength?: number, maxLength?: number): boolean;
/**
 * 验证最小值, 最大值
 * @param value
 * @param min
 * @param max
 */
export declare function maxMin(value: number, min?: number, max?: number): boolean;
/**
 * 是否是身份证(强校验)
 * @param value
 */
export declare function isIdentityStrong(value: string): string | null | undefined;
