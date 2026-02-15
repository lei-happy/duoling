"use strict";
const vue = require("vue");
const _hoisted_1 = { class: "ele-admin-tool" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "LayoutTool" },
  __name: "layout-tool",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.renderSlot(_ctx.$slots, "default")
      ]);
    };
  }
});
module.exports = _sfc_main;
