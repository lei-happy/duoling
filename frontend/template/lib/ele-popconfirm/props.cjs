"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const props = require("../ele-popover/props");
const popconfirmProps = {
  ...props.popoverProps,
  trigger: {
    type: String,
    default: "click"
  },
  /** 确认按钮文字 */
  confirmButtonText: String,
  /** 取消按钮文字 */
  cancelButtonText: String,
  /** 确认按钮类型 */
  confirmButtonType: {
    type: String,
    default: "primary"
  },
  /** 取消按钮类型 */
  cancelButtonType: {
    type: String,
    default: "text"
  },
  /** 自定义图标 */
  icon: [String, Object, Function],
  /** 图标颜色 */
  iconColor: {
    type: String,
    default: "#f90"
  },
  /** 是否隐藏图标 */
  hideIcon: Boolean,
  /** 是否隐藏确认按钮 */
  hideConfirmButton: Boolean,
  /** 是否隐藏取消按钮 */
  hideCancelButton: Boolean,
  /** 图标样式 */
  iconStyle: Object,
  /** 图标组件属性 */
  iconProps: Object,
  /** 确认按钮组件属性 */
  confirmButtonProps: Object,
  /** 取消按钮组件属性 */
  cancelButtonProps: Object,
  /** 底栏样式 */
  footerStyle: Object
};
const popconfirmEmits = {
  ...props.popoverEmits,
  confirm: (_e) => true,
  cancel: (_e) => true
};
exports.popconfirmEmits = popconfirmEmits;
exports.popconfirmProps = popconfirmProps;
