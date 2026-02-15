"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const select = require("element-plus/es/components/select/src/select");
const selectProps = {
  ...select.selectProps,
  /** 选项数据 */
  options: [Array, Function]
};
const selectEmits = {
  "update:modelValue": (_value) => true,
  change: (_value) => true,
  "remove-tag": (_value) => true,
  clear: () => true,
  "visible-change": (_visible) => true,
  focus: (_e) => true,
  blur: (_e) => true
};
exports.selectEmits = selectEmits;
exports.selectProps = selectProps;
