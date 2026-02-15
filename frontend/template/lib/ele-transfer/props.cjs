"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const transferProps = {
  ...elementPlus.transferProps,
  /** 数据 */
  data: [Array, Function]
};
Object.defineProperty(exports, "transferEmits", {
  enumerable: true,
  get: () => elementPlus.transferEmits
});
exports.transferProps = transferProps;
