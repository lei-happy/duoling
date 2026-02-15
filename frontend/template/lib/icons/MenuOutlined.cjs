"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": "4"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MenuOutlined" },
  __name: "MenuOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M3 7H45" }, null, -1),
        vue.createElementVNode("path", { d: "M3 24H44" }, null, -1),
        vue.createElementVNode("path", { d: "M3 41H45" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
