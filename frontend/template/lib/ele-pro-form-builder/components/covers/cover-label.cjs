"use strict";
const vue = require("vue");
const _hoisted_1 = {
  class: "ele-icon-color-primary",
  style: {
    display: "flex",
    alignItems: "baseline",
    justifyContent: "center",
    fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color emoji"
  }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-label",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("div", { style: { fontSize: "18px" } }, "Label", -1),
        vue.createElementVNode("div", { style: { fontSize: "14px", marginLeft: "3px" } }, "Label", -1),
        vue.createElementVNode("div", { style: { fontSize: "12px", marginLeft: "3px" } }, "Label", -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
