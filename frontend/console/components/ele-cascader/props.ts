import type { PropType, ExtractPropTypes } from 'vue';
import { cascaderProps as elCascaderProps } from 'element-plus';
import type { CascaderOption, CascaderOptionFunction } from './types';
export { cascaderEmits } from 'element-plus';

/**
 * 属性
 */
export const cascaderProps = {
  ...elCascaderProps,
  /** 选项数据 */
  options: [Array, Function] as PropType<
    CascaderOption[] | CascaderOptionFunction
  >,
  /** 是否多选 */
  multiple: Boolean
};

export type CascaderProps = ExtractPropTypes<typeof cascaderProps>;
