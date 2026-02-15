import type { PropType, ExtractPropTypes } from 'vue';
import { autocompleteProps as elAutocompleteProps } from 'element-plus';
import type { AutocompleteDataItem, AutocompleteDataFunction } from './types';
export { autocompleteEmits } from 'element-plus';

/**
 * 属性
 */
export const autocompleteProps = {
  ...elAutocompleteProps,
  /** 建议数据 */
  fetchSuggestions: [Array, Function] as PropType<
    AutocompleteDataItem[] | AutocompleteDataFunction
  >
};

export type AutocompleteProps = ExtractPropTypes<typeof autocompleteProps>;
