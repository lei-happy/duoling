"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const checkboxGroupProps = {
  ...elementPlus.checkboxGroupProps,
  /** 风格类型 */
  type: String,
  /** 选项数据 */
  options: [Array, Function]
};
Object.defineProperty(exports, "checkboxGroupEmits", {
  enumerable: true,
  get: () => elementPlus.checkboxGroupEmits
});
exports.checkboxGroupProps = checkboxGroupProps;
