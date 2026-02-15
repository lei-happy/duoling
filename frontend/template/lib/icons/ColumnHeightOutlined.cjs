"use strict";
const vue = require("vue");
const _hoisted_1 = {
  viewBox: "0 0 48 48",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": "4"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ColumnHeightOutlined" },
  __name: "ColumnHeightOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", {
          d: "M24 12V36M18 17 24 12 30 17M30 31 24 36 18 31",
          "stroke-width": "3.5"
        }, null, -1),
        vue.createElementVNode("path", { d: "M6 5H42" }, null, -1),
        vue.createElementVNode("path", { d: "M6 43H42" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
