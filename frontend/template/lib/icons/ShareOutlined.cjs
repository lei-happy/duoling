"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": "4",
  "stroke-linejoin": "round",
  "stroke-linecap": "round"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ShareOutlined" },
  __name: "ShareOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M42 30V42H6V6L18 6" }, null, -1),
        vue.createElementVNode("path", { d: "M30 6H42V18M20 28L42 6" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
