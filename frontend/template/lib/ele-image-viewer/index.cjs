"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const MainContent = require("../ele-loading/components/main-content");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleImageViewer", inheritAttrs: false },
  __name: "index",
  props: props.imageViewerProps,
  emits: props.imageViewerEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const emit = __emit;
    const imageViewerRef = vue.ref(null);
    const handleClose = () => {
      emit("update:modelValue", false);
      emit("close");
    };
    const handleSwitch = (index) => {
      emit("switch", index);
    };
    const handleRotate = (deg) => {
      emit("rotate", deg);
    };
    const setActiveItem = (index) => {
      imageViewerRef.value && imageViewerRef.value.setActiveItem(index);
    };
    vue.onDeactivated(() => {
      handleClose();
    });
    __expose({
      imageViewerRef,
      setActiveItem
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Teleport, {
        to: "body",
        disabled: !_ctx.teleported
      }, [
        vue.createVNode(vue.Transition, {
          name: _ctx.transitionName,
          appear: true
        }, {
          default: vue.withCtx(() => [
            _ctx.modelValue ? (vue.openBlock(), vue.createBlock(MainContent, {
              key: 0,
              class: vue.normalizeClass(["ele-image-viewer", _ctx.customClass]),
              style: vue.normalizeStyle(_ctx.customStyle)
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(elementPlus.ElImageViewer), vue.mergeProps({
                  ..._ctx.$attrs,
                  ...vue.unref(common.omit)(_ctx.$props, [
                    "modelValue",
                    "customClass",
                    "customStyle",
                    "transitionName",
                    "keepAlive"
                  ])
                }, {
                  ref_key: "imageViewerRef",
                  ref: imageViewerRef,
                  teleported: false,
                  onClose: handleClose,
                  onSwitch: handleSwitch,
                  onRotate: handleRotate
                }), vue.createSlots({ _: 2 }, [
                  vue.renderList(Object.keys(_ctx.$slots), (name) => {
                    return {
                      name,
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ])
                    };
                  })
                ]), 1040)
              ]),
              _: 3
            }, 8, ["class", "style"])) : vue.createCommentVNode("", true)
          ]),
          _: 3
        }, 8, ["name"])
      ], 8, ["disabled"]);
    };
  }
});
module.exports = _sfc_main;
