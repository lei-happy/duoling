"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const radioGroupProps = {
  ...elementPlus.radioGroupProps,
  /** 风格类型 */
  type: String,
  /** 选项数据 */
  options: [Array, Function]
};
Object.defineProperty(exports, "radioGroupEmits", {
  enumerable: true,
  get: () => elementPlus.radioGroupEmits
});
exports.radioGroupProps = radioGroupProps;
