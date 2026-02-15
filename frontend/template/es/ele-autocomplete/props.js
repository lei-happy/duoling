import { autocompleteProps as autocompleteProps$1 } from "element-plus";
import { autocompleteEmits } from "element-plus";
const autocompleteProps = {
  ...autocompleteProps$1,
  /** 建议数据 */
  fetchSuggestions: [Array, Function]
};
export {
  autocompleteEmits,
  autocompleteProps
};
