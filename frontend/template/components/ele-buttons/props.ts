import type { PropType, ExtractPropTypes } from 'vue';
import type { ElDividerProps } from '../ele-app/el';
import type { ButtonItem, ButtonItemType, ButtonsLocale } from './types';

/**
 * 属性
 */
export const buttonsProps = {
  /** 按钮数据 */
  items: Array as PropType<ButtonItem[]>,
  /** 是否显示分割线 */
  divider: [Boolean, Object] as PropType<boolean | ElDividerProps>,
  /** 组件类型 */
  type: String as PropType<ButtonItemType>,
  /** 间距 */
  gap: {
    type: [Boolean, Number],
    default: null
  },
  /** 是否自动换行 */
  wrap: {
    type: Boolean,
    default: null
  },
  /** 是否是弹窗底栏 */
  modalFooter: Boolean,
  /** 国际化 */
  locale: Object as PropType<Partial<ButtonsLocale>>
};

export type ButtonsProps = ExtractPropTypes<typeof buttonsProps>;

/**
 * 事件
 */
export const buttonsEmits = {
  itemClick: (_command: any, _e?: MouseEvent) => true
};
