/**
 * toTree 方法参数
 */
export interface ToTreeOption<T> {
    /** 数据 */
    data?: T[] | null;
    /** id 字段名称 */
    idField?: string | null;
    /** parentId 字段名称 */
    parentIdField?: string | null;
    /** 生成的 children 字段名称 */
    childrenField?: string | null;
    /** 最顶级的 parentId 值 */
    parentId?: number | string | (number | string)[] | null;
    /** 是否添加包含所有父级 id 的字段 */
    addParentIds?: boolean | null;
    /** 包含所有父级 id 字段的名称 */
    parentIdsField?: string | null;
    /** 所有父级的 id */
    parentIds?: (number | string)[] | null;
    /** 是否添加包含所有父级的字段 */
    addParents?: boolean | null;
    /** 包含所有父级字段的名称 */
    parentsField?: string | null;
    /** 所有父级 */
    parents?: T[] | null;
}
/**
 * parentId 形式数据转 children 形式
 * @param option ToTreeOption
 */
export declare function toTree<T>(option: ToTreeOption<T>): T[];
/**
 * 遍历 children 形式数据
 * @param data 数据
 * @param callback 回调
 * @param childrenField children 字段名
 * @param parent 当前的父级
 */
export declare function eachTree<T>(data?: T[], callback?: (item: T, index: number, parent?: T) => void | boolean, childrenField?: string, parent?: T): false | undefined;
/**
 * 处理 children 形式数据
 * @param data 数据
 * @param formatter 格式器
 * @param childrenField children 字段名
 * @param resultChildrenField 返回后的 children 字段名
 * @param afterFormatter 后置格式器
 * @param parent 当前的父级
 */
export declare function mapTree<T, K>(data: T[] | undefined | null, formatter: (item: T, index?: number, parent?: T | K) => K | void | undefined | 'flatChildren', childrenField?: string, resultChildrenField?: string, afterFormatter?: (item: K) => K | void | undefined, parent?: T | K): K[];
/**
 * 查找 children 形式数据
 * @param data 数据
 * @param predicate 查找条件
 * @param childrenField children 字段名
 */
export declare function findTree<T>(data: T[] | undefined, predicate: (value: T, index: number) => unknown, childrenField?: string): T | undefined;
/**
 * 检查是否全屏
 */
export declare function checkFullscreen(): boolean;
/**
 * 退出全屏
 */
export declare function exitFullscreen(): void;
/**
 * 全屏
 * @param el HTMLElement
 */
export declare function requestFullscreen(el?: HTMLElement): void;
/**
 * 经纬度坐标
 */
export interface Point {
    /** 经度 */
    lng: number;
    /** 纬度 */
    lat: number;
}
/**
 * 百度地图坐标转高德地图坐标
 * @param point 坐标
 */
export declare function bd09ToGcj02(point: Point): Point;
/**
 * 高德地图坐标转百度地图坐标
 * @param point 坐标
 */
export declare function gcj02ToBd09(point: Point): Point;
/**
 * 生成 m 到 n 的随机数
 * @param m 最小值(包含)
 * @param n 最大值(不包含)
 */
export declare function random(m: number, n: number): number;
/**
 * 生成随机字符串
 * @param length 长度
 * @param radix 基数
 */
export declare function uuid(length?: number, radix?: number): string;
/**
 * 数字千分位格式化参数
 */
export interface FormatNumberOption {
    /** 小数位数, 默认保留所有小数位 */
    decimals?: number;
    /** 小数分隔符, 默认 '.' */
    decimalSeparator?: string;
    /** 千分位分隔符, 默认 ',' */
    thousandSeparator?: string;
    /** 是否在数字为 0 时显示 '-' */
    zeroDisplay?: boolean;
}
/**
 * 数字千分位
 * @param num 数字
 * @param option 参数
 */
export declare function formatNumber(num?: number | string | null, option?: FormatNumberOption): string;
/**
 * 赋值不改变原字段
 * @param target 目标对象
 * @param source 源对象
 * @param excludes 排除的字段
 */
export declare function assignObject<T extends {}, K extends {}>(target: T, source: K, excludes?: string[]): T;
/**
 * 复制字符串
 * @param text 字符串
 */
export declare function copyText(text: string): Promise<undefined>;
/**
 * 查找直接子元素
 * @param parentEl 父元素
 * @param className 根据类名查找
 * @param attr 根据属性查找
 */
export declare function queryChild(parentEl?: Element, className?: string, attr?: string[]): Element | undefined;
/**
 * 判断是否是外链
 * @param url 地址
 */
export declare function isExternalLink(url?: string | null): boolean;
