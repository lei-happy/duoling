"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": "4",
  "stroke-linecap": "round"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "PlusCircleOutlined" },
  __name: "PlusCircleOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M24 45C35 45 45 35 45 24 45 13 35 3 24 3 13 3 3 13 3 24 3 35 13 45 24 45Z" }, null, -1),
        vue.createElementVNode("path", { d: "M14 24H34M24 14V34" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
