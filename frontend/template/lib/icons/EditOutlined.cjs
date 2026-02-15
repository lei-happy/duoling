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
  ...{ name: "EditOutlined" },
  __name: "EditOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M4 42H44" }, null, -1),
        vue.createElementVNode("path", { d: "M11 25V33H19L41 11 33 3 11 25Z" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
