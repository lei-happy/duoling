"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "currentColor"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MessageOutlined" },
  __name: "MessageOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", {
          d: "M5 8H43V38H31L24 45 17 38H5Z",
          fill: "none",
          stroke: "currentColor",
          "stroke-width": "4",
          "stroke-linejoin": "round"
        }, null, -1),
        vue.createElementVNode("circle", {
          cx: "14",
          cy: "23",
          r: "3"
        }, null, -1),
        vue.createElementVNode("circle", {
          cx: "24",
          cy: "23",
          r: "3"
        }, null, -1),
        vue.createElementVNode("circle", {
          cx: "34",
          cy: "23",
          r: "3"
        }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
