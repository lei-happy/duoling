"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const props = require("../ele-text/props");
const ellipsisProps = {
  ...props.textProps,
  /** 最大行数 */
  maxLine: Number,
  /** 行高 */
  lineHeight: [Number, String],
  /** 文字提示属性 */
  tooltip: {
    type: [Boolean, Object],
    default: () => {
      return { original: true };
    }
  }
};
exports.ellipsisProps = ellipsisProps;
