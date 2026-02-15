import type { PropType, ExtractPropTypes } from 'vue';
import { useTooltipProps, tooltipEmits as elTooltipEmits } from 'element-plus';
import type { StyleValue } from '../ele-app/types';
import { omit } from '../utils/common';
type TooltipExclude =
  | 'onUpdate:visible'
  | 'style'
  | 'onMouseenter'
  | 'onMouseleave'
  | 'onClick'
  | 'onKeydown'
  | 'onFocus'
  | 'onBlur'
  | 'onContextmenu'
  // 类型去掉几个复杂的避免实例化过深且可能无限
  | 'className'
  | 'popperClass'
  | 'popperStyle'
  | 'id'
  | 'role'
  | 'strategy'
  | 'open'
  | 'pure'
  | 'focusOnShow'
  | 'trapping'
  | 'referenceEl'
  | 'triggerTargetEl'
  | 'stopPopperMouseEvent'
  | 'boundariesPadding'
  | 'fallbackPlacements';
const normalizeProps = omit(useTooltipProps, [
  'onUpdate:visible',
  'style',
  'onMouseenter',
  'onMouseleave',
  'onClick',
  'onKeydown',
  'onFocus',
  'onBlur',
  'onContextmenu'
] as TooltipExclude[]);

/**
 * 属性
 */
export const tooltipProps = {
  className: String,
  popperClass: String,
  popperStyle: Object as PropType<StyleValue>,
  ...normalizeProps,
  /** 自定义内容样式 */
  bodyStyle: Object as PropType<StyleValue>,
  /** 自定义背景色 */
  bg: String,
  /** 自定义箭头颜色 */
  arrowBg: String,
  /** 宽度 */
  width: [String, Number],
  /** 是否是气泡卡片 */
  isPopover: Boolean
};

export type TooltipProps = ExtractPropTypes<typeof tooltipProps>;

/**
 * 事件
 */
export type TooltipEmits = {
  'update:visible': (visible: boolean) => boolean;
  'before-show': (e: Event) => boolean;
  'before-hide': (e: Event) => boolean;
  show: (e: Event) => boolean;
  hide: (e: Event) => boolean;
  open: (e: any) => boolean;
  close: (e: any) => boolean;
};

export const tooltipEmits = elTooltipEmits as unknown as TooltipEmits;

/**
 * 属性名
 */
export type TooltipPropKeys = Array<keyof typeof tooltipProps>;

export const tooltipPropKeys = Object.keys(tooltipProps) as TooltipPropKeys;
