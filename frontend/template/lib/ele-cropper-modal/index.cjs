"use strict";
const vue = require("vue");
const receiver = require("../ele-config-provider/receiver");
const EleModal = require("../ele-modal/index");
const EleCropper = require("../ele-cropper/index");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCropperModal" },
  __name: "index",
  props: props.cropperModalProps,
  emits: props.cropperModalEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("cropper", props2);
    const updateModelValue = (value) => {
      emit("update:modelValue", value);
    };
    const handleDone = (result) => {
      emit("done", result);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, vue.mergeProps({
        width: "620px",
        title: vue.unref(lang).title
      }, _ctx.modalProps || {}, {
        modelValue: _ctx.modelValue,
        "onUpdate:modelValue": updateModelValue
      }), vue.createSlots({
        default: vue.withCtx(() => [
          vue.createVNode(EleCropper, {
            height: _ctx.height,
            src: _ctx.src,
            imageType: _ctx.imageType,
            accept: _ctx.accept,
            tools: _ctx.tools,
            preview: _ctx.preview,
            previewWidth: _ctx.previewWidth,
            toBlob: _ctx.toBlob,
            options: _ctx.options,
            croppedOptions: _ctx.croppedOptions,
            tooltip: _ctx.tooltip,
            tooltipProps: _ctx.tooltipProps,
            beforeUploadClick: _ctx.beforeUploadClick,
            responsive: _ctx.responsive,
            locale: _ctx.locale,
            onDone: handleDone
          }, null, 8, ["height", "src", "imageType", "accept", "tools", "preview", "previewWidth", "toBlob", "options", "croppedOptions", "tooltip", "tooltipProps", "beforeUploadClick", "responsive", "locale"])
        ]),
        _: 2
      }, [
        _ctx.$slots.header ? {
          name: "header",
          fn: vue.withCtx((slotProps) => [
            vue.renderSlot(_ctx.$slots, "header", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
          ]),
          key: "0"
        } : void 0,
        _ctx.$slots.footer ? {
          name: "footer",
          fn: vue.withCtx((slotProps) => [
            vue.renderSlot(_ctx.$slots, "footer", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
          ]),
          key: "1"
        } : void 0,
        _ctx.$slots.maxIcon ? {
          name: "maxIcon",
          fn: vue.withCtx((slotProps) => [
            vue.renderSlot(_ctx.$slots, "maxIcon", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
          ]),
          key: "2"
        } : void 0,
        _ctx.$slots.closeIcon ? {
          name: "closeIcon",
          fn: vue.withCtx((slotProps) => [
            vue.renderSlot(_ctx.$slots, "closeIcon", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
          ]),
          key: "3"
        } : void 0
      ]), 1040, ["title", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
