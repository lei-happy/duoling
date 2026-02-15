"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const props = require("../ele-cropper/props");
const cropperModalProps = {
  ...props.cropperProps,
  /** 弹窗是否显示 */
  modelValue: Boolean,
  /** 弹窗参数 */
  modalProps: Object
};
const cropperModalEmits = {
  /** 裁剪完成事件 */
  done: (_result) => true,
  /** 更新弹窗显示状态 */
  "update:modelValue": (_value) => true
};
exports.cropperModalEmits = cropperModalEmits;
exports.cropperModalProps = cropperModalProps;
