import type { PropType, ExtractPropTypes } from 'vue';
import {
  popoverProps as elPopoverProps,
  popoverEmits as elPopoverEmits
} from 'element-plus';
import type { StyleValue } from '../ele-app/types';
import { omit } from '../utils/common';
import { tooltipProps } from '../ele-tooltip/props';
type Excludes = 'onUpdate:visible' | 'popperClass' | 'popperStyle';
const normalizeProps = omit(elPopoverProps, ['onUpdate:visible'] as Excludes[]);

/**
 * 属性
 */
export const popoverProps = {
  ...omit(tooltipProps, ['rawContent', 'isPopover']),
  popperStyle: [String, Array, Object] as PropType<StyleValue>,
  popperClass: String,
  ...normalizeProps,
  transition: {
    type: String,
    default: 'el-fade-in-linear'
  },
  /** 自定义主体类名 */
  bodyClass: String,
  /** 自定义主体样式 */
  bodyStyle: Object as PropType<StyleValue>,
  /** 自定义标题样式 */
  titleStyle: Object as PropType<StyleValue>,
  /** 自定义内容样式 */
  contentStyle: Object as PropType<StyleValue>
};

export type PopoverProps = ExtractPropTypes<typeof popoverProps>;

/**
 * 事件
 */
export const popoverEmits = elPopoverEmits;
