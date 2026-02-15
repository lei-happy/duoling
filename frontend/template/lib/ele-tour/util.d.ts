import { EleTooltipProps } from '../ele-app/plus';
import { Offset } from './types';

/**
 * 获取元素距浏览器窗口的距离
 * @param el 元素
 */
export declare function getOffset(el: HTMLElement): Offset;
/**
 * 获取气泡组件属性
 * @param visible 是否显示
 * @param model 是否是弹窗
 * @param props 自定义属性
 */
export declare function getPopperProps(visible?: boolean, modal?: boolean, props?: EleTooltipProps): EleTooltipProps;
/**
 * 让元素可见
 * @param el 元素
 */
export declare function scrollIntoView(el: HTMLElement): void;
