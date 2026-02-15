"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const common = require("../utils/common");
const normalizeProps = common.omit(elementPlus.useTooltipProps, [
  "onUpdate:visible",
  "style",
  "onMouseenter",
  "onMouseleave",
  "onClick",
  "onKeydown",
  "onFocus",
  "onBlur",
  "onContextmenu"
]);
const tooltipProps = {
  className: String,
  popperClass: String,
  popperStyle: Object,
  ...normalizeProps,
  /** 自定义内容样式 */
  bodyStyle: Object,
  /** 自定义背景色 */
  bg: String,
  /** 自定义箭头颜色 */
  arrowBg: String,
  /** 宽度 */
  width: [String, Number],
  /** 是否是气泡卡片 */
  isPopover: Boolean
};
const tooltipEmits = elementPlus.tooltipEmits;
const tooltipPropKeys = Object.keys(tooltipProps);
exports.tooltipEmits = tooltipEmits;
exports.tooltipPropKeys = tooltipPropKeys;
exports.tooltipProps = tooltipProps;
