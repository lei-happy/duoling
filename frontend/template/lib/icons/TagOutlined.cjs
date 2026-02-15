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
  ...{ name: "TagOutlined" },
  __name: "TagOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M10 44H38V13L24 2 10 13Z" }, null, -1),
        vue.createElementVNode("path", { d: "M24 25C21 25 19 23 19 20S21 15 24 15 29 17 29 20 27 25 24 25Z" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
