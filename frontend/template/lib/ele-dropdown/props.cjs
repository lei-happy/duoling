"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const common = require("../utils/common");
const props = require("../ele-popover/props");
const normalizePopoverProps = common.omit(props.popoverProps, [
  "title",
  "effect",
  "content",
  "width",
  "placement",
  "disabled",
  "popperOptions",
  "popperClass",
  "showAfter",
  "hideAfter",
  "autoClose",
  "tabindex",
  "teleported",
  "bodyClass",
  "bodyStyle",
  "titleStyle",
  "contentStyle"
]);
const normalizeDropdownProps = common.omit(elementPlus.dropdownProps, [
  "onCommand",
  "onClick",
  "onVisibleChange",
  "onVisible-change"
]);
const dropdownProps = {
  ...normalizePopoverProps,
  size: String,
  ...normalizeDropdownProps,
  /** 下拉框渐变动画 */
  transition: {
    type: String,
    default: "el-zoom-in-top"
  },
  /** 下拉菜单数据 */
  items: Array,
  /** 选中的菜单 */
  modelValue: [String, Number, Object],
  /** 自定义下拉菜单样式 */
  menuStyle: Object,
  /** 自定义图标属性 */
  iconProps: Object,
  /** 图标尺寸 */
  iconSize: String,
  /** 下拉菜单使用的组件类型 */
  componentType: String,
  /** 是否阻止下拉菜单的右键事件 */
  preventContextmenu: Boolean,
  /** 内容按钮属性 */
  splitButtonProps: Object,
  /** 箭头按钮属性 */
  caretButtonProps: Object,
  /** 是否触发表单验证 */
  validateEvent: {
    type: Boolean,
    default: true
  }
};
const dropdownEmits = {
  ...props.popoverEmits,
  /** 内容按钮点击事件 */
  click: (_e) => true,
  /** 菜单项点击事件 */
  command: (_command) => true,
  /** 下拉框显示状态改变事件 */
  visibleChange: (_visible) => true,
  /** 更新选中值 */
  "update:modelValue": (_value) => true,
  /** 选中改变的事件 */
  change: (_active) => true
};
const elDropdownPropKeys = Object.keys(
  normalizeDropdownProps
);
exports.dropdownEmits = dropdownEmits;
exports.dropdownProps = dropdownProps;
exports.elDropdownPropKeys = elDropdownPropKeys;
