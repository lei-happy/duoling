import { defineComponent, ref, createElementBlock, openBlock, normalizeStyle, createElementVNode, createCommentVNode, Fragment } from "vue";
const _sfc_main = /* @__PURE__ */ defineComponent({
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
    const rootRef = ref(null);
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
      return openBlock(), createElementBlock("div", {
        ref_key: "rootRef",
        ref: rootRef,
        class: "ele-cropper-previews",
        style: normalizeStyle({ width: `${__props.previewWidth + 14}px` })
      }, [
        createElementVNode("div", {
          class: "ele-cropper-preview",
          style: normalizeStyle({
            width: `${__props.previewWidth}px`,
            height: `${__props.previewWidth / (__props.aspectRatio || 1)}px`,
            marginTop: "0px"
          })
        }, null, 4),
        __props.aspectRatio === 1 ? (openBlock(), createElementBlock("div", {
          key: 0,
          class: "ele-cropper-preview is-circle",
          style: normalizeStyle({
            width: `${__props.previewWidth}px`,
            height: `${__props.previewWidth / __props.aspectRatio}px`
          })
        }, null, 4)) : __props.aspectRatio ? (openBlock(), createElementBlock(Fragment, { key: 1 }, [
          createElementVNode("div", {
            class: "ele-cropper-preview",
            style: normalizeStyle({
              width: `${__props.previewWidth}px`,
              height: `${(__props.previewWidth / 3 * 2 - 10) / __props.aspectRatio}px`
            })
          }, null, 4),
          createElementVNode("div", {
            class: "ele-cropper-preview",
            style: normalizeStyle({
              width: `${__props.previewWidth}px`,
              height: `${__props.previewWidth / 3 / __props.aspectRatio}px`,
              marginLeft: "10px"
            })
          }, null, 4)
        ], 64)) : createCommentVNode("", true)
      ], 4);
    };
  }
});
export {
  _sfc_main as default
};
