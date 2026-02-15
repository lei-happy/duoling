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
  ...{ name: "FormOutlined" },
  __name: "FormOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M42 26V42H6V6L22 6" }, null, -1),
        vue.createElementVNode("path", { d: "M16 32H22L43 11 37 5 16 26Z" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
