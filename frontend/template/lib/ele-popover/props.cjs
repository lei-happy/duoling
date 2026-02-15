"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const common = require("../utils/common");
const props = require("../ele-tooltip/props");
const normalizeProps = common.omit(elementPlus.popoverProps, ["onUpdate:visible"]);
const popoverProps = {
  ...common.omit(props.tooltipProps, ["rawContent", "isPopover"]),
  popperStyle: [String, Array, Object],
  popperClass: String,
  ...normalizeProps,
  transition: {
    type: String,
    default: "el-fade-in-linear"
  },
  /** 自定义主体类名 */
  bodyClass: String,
  /** 自定义主体样式 */
  bodyStyle: Object,
  /** 自定义标题样式 */
  titleStyle: Object,
  /** 自定义内容样式 */
  contentStyle: Object
};
const popoverEmits = elementPlus.popoverEmits;
exports.popoverEmits = popoverEmits;
exports.popoverProps = popoverProps;
