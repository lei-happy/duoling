"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CropperPreview" },
  __name: "cropper-preview",
  props: {
    /** 组件宽度 */
    previewWidth: {
      type: Number,
      required: true
    },
    /** 裁剪比例 */
    aspectRatio: Number
  },
  setup(__props, { expose: __expose }) {
    const rootRef = vue.ref(null);
    const getPreviews = () => {
      if (!rootRef.value) {
        return;
      }
      return rootRef.value.querySelectorAll(".ele-cropper-preview");
    };
    __expose({
      getPreviews
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "rootRef",
        ref: rootRef,
        class: "ele-cropper-previews",
        style: vue.normalizeStyle({ width: `${__props.previewWidth + 14}px` })
      }, [
        vue.createElementVNode("div", {
          class: "ele-cropper-preview",
          style: vue.normalizeStyle({
            width: `${__props.previewWidth}px`,
            height: `${__props.previewWidth / (__props.aspectRatio || 1)}px`,
            marginTop: "0px"
          })
        }, null, 4),
        __props.aspectRatio === 1 ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-cropper-preview is-circle",
          style: vue.normalizeStyle({
            width: `${__props.previewWidth}px`,
            height: `${__props.previewWidth / __props.aspectRatio}px`
          })
        }, null, 4)) : __props.aspectRatio ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
          vue.createElementVNode("div", {
            class: "ele-cropper-preview",
            style: vue.normalizeStyle({
              width: `${__props.previewWidth}px`,
              height: `${(__props.previewWidth / 3 * 2 - 10) / __props.aspectRatio}px`
            })
          }, null, 4),
          vue.createElementVNode("div", {
            class: "ele-cropper-preview",
            style: vue.normalizeStyle({
              width: `${__props.previewWidth}px`,
              height: `${__props.previewWidth / 3 / __props.aspectRatio}px`,
              marginLeft: "10px"
            })
          }, null, 4)
        ], 64)) : vue.createCommentVNode("", true)
      ], 4);
    };
  }
});
module.exports = _sfc_main;
