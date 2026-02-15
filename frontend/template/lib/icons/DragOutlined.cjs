"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": "4",
  "stroke-linecap": "round",
  "stroke-linejoin": "round"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "DragOutlined" },
  __name: "DragOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M19 9 24 4 29 9M24 4V44M4 24H44M19 39 24 44 29 39M39 19 44 24 39 29M9 19 4 24 9 29" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
