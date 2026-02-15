"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const cropperProps = {
  /** 图片高度 */
  height: String,
  /** 图片地址 */
  src: String,
  /** 图片地址对应的图片类型,如'image/jpeg' */
  imageType: {
    type: String,
    default: "image/png"
  },
  /** 允许上传的图片类型 */
  accept: {
    type: String,
    default: "image/*"
  },
  /** 操作按钮布局 */
  tools: {
    type: String,
    default: "zoomIn,zoomOut | moveLeft,moveRight,moveUp,moveDown | rotateLeft,rotateRight | flipX,flipY | reset,upload | ok"
  },
  /** 是否需要预览组件 */
  preview: {
    type: Boolean,
    default: true
  },
  /** 预览组件宽度 */
  previewWidth: {
    type: Number,
    default: 98
  },
  /** 是否返回blob数据 */
  toBlob: Boolean,
  /** cropperjs的参数 */
  options: Object,
  /** cropperjs裁剪方法的参数 */
  croppedOptions: Object,
  /** 是否需要tooltip */
  tooltip: {
    type: Boolean,
    default: true
  },
  /** tooltip属性 */
  tooltipProps: Object,
  /** 上传按钮点击前的钩子 */
  beforeUploadClick: Function,
  /** 是否开启响应式 */
  responsive: {
    type: Boolean,
    default: null
  },
  /** 国际化 */
  locale: Object
};
const cropperEmits = {
  /** 裁剪完成事件 */
  done: (_result) => true
};
exports.cropperEmits = cropperEmits;
exports.cropperProps = cropperProps;
