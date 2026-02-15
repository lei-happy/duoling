"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleFileListTool" },
  __name: "index",
  emits: {
    click: (_e) => true
  },
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const handleClick = (e) => {
      emit("click", e);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-file-list-item-tool",
        onClick: vue.withModifiers(handleClick, ["stop"])
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ]);
    };
  }
});
module.exports = _sfc_main;
