import type { PropType, ExtractPropTypes } from 'vue';
import { mentionProps as elMentionProps } from 'element-plus';
import type { MentionOption, MentionOptionsFunction } from './types';
export { mentionEmits } from 'element-plus';

/**
 * 属性
 */
export const mentionProps = {
  ...elMentionProps,
  /** 数据 */
  options: [Array, Function] as PropType<
    MentionOption[] | MentionOptionsFunction
  >
};

export type MentionProps = ExtractPropTypes<typeof mentionProps>;
