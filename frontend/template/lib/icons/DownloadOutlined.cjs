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
  ...{ name: "DownloadOutlined" },
  __name: "DownloadOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M6 24V42H42V24" }, null, -1),
        vue.createElementVNode("path", { d: "M24 6V32M33 23 24 32 15 23" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
