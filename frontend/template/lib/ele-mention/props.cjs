"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const mentionProps = {
  ...elementPlus.mentionProps,
  /** 数据 */
  options: [Array, Function]
};
Object.defineProperty(exports, "mentionEmits", {
  enumerable: true,
  get: () => elementPlus.mentionEmits
});
exports.mentionProps = mentionProps;
