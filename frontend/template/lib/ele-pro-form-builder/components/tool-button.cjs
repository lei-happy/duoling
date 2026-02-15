"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ToolButton" },
  __name: "tool-button",
  props: {
    buttonProps: {},
    tooltip: {}
  },
  emits: ["click"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const handleClick = (e) => {
      emit("click", e);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), vue.mergeProps(__props.buttonProps || {}, {
        title: __props.tooltip,
        class: "ele-pro-form-builder-tool-button",
        onClick: handleClick
      }), vue.createSlots({ _: 2 }, [
        _ctx.$slots.default ? {
          name: "default",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "default")
          ]),
          key: "0"
        } : void 0
      ]), 1040, ["title"]);
    };
  }
});
module.exports = _sfc_main;
