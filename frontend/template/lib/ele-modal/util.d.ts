import { MoveOut, MoveOutValue, Position } from './types';

export declare const containerClass = "ele-modal-container";
export declare const wrapperClass = "ele-modal";
export declare const closedClass = "ele-modal-closed";
/**
 * 是否可拉出指定方向
 * @param moveOut 拉出值
 * @param direction 方向
 */
export declare function canMoveOut(moveOut?: MoveOut, direction?: MoveOutValue): boolean;
/**
 * 获取弹窗容器
 * @param inner 是否限制在主体内部
 * @param multiple 是否支持同时打开多个
 * @param appendTo 自定义插入的容器
 * @param modalsEl 限制在主体内部时的容器
 */
export declare function getModalContainer(inner?: boolean, multiple?: boolean, appendTo?: string | HTMLElement, modalsEl?: HTMLElement | null): HTMLElement | string;
/**
 * 获取位置对应的外间距值
 * @param position 位置
 */
export declare function getPositionMargin(position?: Position): string | undefined;
/**
 * 获取弹窗最大层级
 * @param modalEl 弹窗节点
 * @param defaultZIndex 默认层级
 */
export declare function getMaxZIndex(modalEl?: HTMLElement, defaultZIndex?: number): number | undefined;
