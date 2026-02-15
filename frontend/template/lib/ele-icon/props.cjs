"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const iconProps = {
  ...elementPlus.iconProps,
  /** 图标名称 */
  name: [String, Object, Function],
  /** 图标类型 */
  iconType: String
};
exports.iconProps = iconProps;
