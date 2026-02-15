"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const cascaderProps = {
  ...elementPlus.cascaderProps,
  /** 选项数据 */
  options: [Array, Function],
  /** 是否多选 */
  multiple: Boolean
};
Object.defineProperty(exports, "cascaderEmits", {
  enumerable: true,
  get: () => elementPlus.cascaderEmits
});
exports.cascaderProps = cascaderProps;
