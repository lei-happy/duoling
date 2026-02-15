"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "currentColor"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EllipsisOutlined" },
  __name: "EllipsisOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("circle", {
          cx: "8",
          cy: "24",
          r: "4"
        }, null, -1),
        vue.createElementVNode("circle", {
          cx: "24",
          cy: "24",
          r: "4"
        }, null, -1),
        vue.createElementVNode("circle", {
          cx: "40",
          cy: "24",
          r: "4"
        }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
