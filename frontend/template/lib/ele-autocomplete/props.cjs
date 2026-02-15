"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const autocompleteProps = {
  ...elementPlus.autocompleteProps,
  /** 建议数据 */
  fetchSuggestions: [Array, Function]
};
Object.defineProperty(exports, "autocompleteEmits", {
  enumerable: true,
  get: () => elementPlus.autocompleteEmits
});
exports.autocompleteProps = autocompleteProps;
