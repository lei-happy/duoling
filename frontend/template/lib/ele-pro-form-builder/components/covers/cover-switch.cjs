"use strict";
const vue = require("vue");
const _hoisted_1 = {
  class: "ele-icon-bg-primary",
  style: {
    width: "36px",
    height: "18px",
    padding: "2px",
    borderRadius: "9px",
    boxSizing: "border-box",
    margin: "0 auto"
  }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-switch",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [..._cache[0] || (_cache[0] = [
        vue.createElementVNode("div", { style: {
          height: "14px",
          width: "14px",
          borderRadius: "50%",
          background: "#fff",
          margin: "0 0 0 auto"
        } }, null, -1)
      ])]);
    };
  }
});
module.exports = _sfc_main;
