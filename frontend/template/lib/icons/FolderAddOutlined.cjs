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
  ...{ name: "FolderAddOutlined" },
  __name: "FolderAddOutlined",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("path", { d: "M3 6H16L25 14H45V42H3Z" }, null, -1),
        vue.createElementVNode("path", { d: "M16 28H32M24 20V36" }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
