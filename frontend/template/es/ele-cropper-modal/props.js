import { cropperProps } from "../ele-cropper/props";
const cropperModalProps = {
  ...cropperProps,
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
export {
  cropperModalEmits,
  cropperModalProps
};
