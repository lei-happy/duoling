"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const stepsProps = {
  ...elementPlus.stepsProps,
  /** 步骤条数据 */
  items: Array,
  /** 类型 */
  type: String
};
exports.stepsProps = stepsProps;
