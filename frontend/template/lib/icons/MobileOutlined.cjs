"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": "4",
  "stroke-linejoin": "round"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MobileOutlined" },
  __name: "MobileOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M9 4H39V44H9Z" }, null, -1),
        vue.createElementVNode("circle", {
          cx: "24",
          cy: "35",
          r: "3.2",
          stroke: "none",
          fill: "currentColor"
        }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
