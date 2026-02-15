import { StyleValue, SlotObject } from '../ele-app/types';

export * from './core';
/**
 * 防抖函数
 * @param func 函数
 * @param wait 等待时间
 */
export declare function debounce<T extends (...args: any) => any>(func: T, wait: number): (this: any) => void;
/**
 * 节流函数
 * @param func 函数
 * @param wait 等待时间
 * @param trailing 是否在节流结束后调用
 */
export declare function throttle<T extends (...args: any) => any>(func: T, wait: number, trailing?: boolean): (this: any) => void;
/**
 * 忽略对象属性
 * @param obj 来源对象
 * @param fields 忽略的属性
 */
export declare function omit<T extends {}, K extends keyof T>(obj: T | null | undefined, fields: K[]): Omit<T, K>;
/**
 * 摘选对象属性
 * @param obj 来源对象
 * @param fields 摘选的属性
 */
export declare function pick<T extends object, K extends keyof T>(obj: T, fields: K[]): Pick<T, K>;
/**
 * 根据字段路径获取值
 * @param data 数据
 * @param path 字段路径
 * @param defaultValue 默认值
 */
export declare function getValue<T, K>(data?: K | null, path?: string | string[] | ((d: K) => T), defaultValue?: T): T | undefined;
/**
 * 样式对象转字符串
 * @param style 样式对象
 */
export declare function joinStyle(style?: StyleValue | string): string;
/**
 * 处理字符串数组
 * @param content 字符串内容
 * @param comment 默认内容
 * @param reduce 处理方法
 */
export declare function normalizeStringArray(content: string | string[] | undefined, comment: Array<any>, reduce: (item: string) => string): string[];
/**
 * 获取映射后的组件插槽数据
 * @param slots 原始的插槽数据
 * @param compSlotsMap 组件插槽名称映射
 * @param excludeMapNames 排除的组件插槽名称
 * @param excludeCompSlots 排除插槽传递的名称
 * @param reserveSlots 是否保留原始的插槽数据名称
 */
export declare function getMappedSlots(slots: SlotObject, compSlotsMap?: Record<string, string>, excludeMapNames?: string[], excludeSlots?: string[], reserveSlots?: boolean): SlotObject;
/**
 * 获取映射后的组件插槽名称数据
 * @param slots 原始的插槽数据
 * @param compSlotsMap 组件插槽名称映射
 * @param excludeMapNames 排除的组件插槽名称
 * @param excludeCompSlots 排除插槽传递的名称
 * @param reserveSlots 是否保留原始的插槽数据名称
 */
export declare function getSlotsMap(slots: SlotObject, compSlotsMap?: Record<string, string>, excludeMapNames?: string[], excludeSlots?: string[], reserveSlots?: boolean): Record<string, string>;
/**
 * 日期格式处理
 */
export declare function localize(start?: any, end?: any, max?: any): string | number | undefined;
/**
 * 首字母大写
 * @param str 字符串
 */
export declare function capitalize(str: string): string;
/**
 * 获取像素密度
 */
export declare function getPixelRatio(): number;
/**
 * 判断元素内容是否溢出省略
 * @param el 元素节点
 * @param direction 只判断单个方向是否溢出
 */
export declare function contentIsEllipsis(el: HTMLElement, direction?: 'horizontal' | 'vertical'): boolean;
/**
 * 获取节点样式
 * @param el 节点
 */
export declare function getCurrentStyle(el: Element): CSSStyleDeclaration;
/**
 * 下载文件
 * @param url 文件地址
 * @param name 文件名
 */
export declare function downloadUrl(url: string, name: string): void;
/**
 * 下载文件
 * @param data 二进制数据
 * @param name 文件名
 * @param type 文件类型
 */
export declare function download(data: Blob | ArrayBuffer | string, name: string, type?: string): void;
