"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { width: "62px", margin: "0 auto" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-check-card",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(index.IconCard), {
          size: "sm",
          checked: true
        }),
        vue.createVNode(vue.unref(index.IconCard), {
          size: "sm",
          style: { marginTop: "4px" }
        }),
        vue.createVNode(vue.unref(index.IconCard), {
          size: "sm",
          style: { marginTop: "4px" }
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
