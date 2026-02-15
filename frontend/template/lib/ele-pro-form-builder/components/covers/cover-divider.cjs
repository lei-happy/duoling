"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-divider",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: "sm",
          style: { marginBottom: "10px", width: "33%" }
        }),
        _cache[0] || (_cache[0] = vue.createElementVNode("div", {
          class: "ele-icon-border-color-primary",
          style: { borderTopStyle: "solid", borderTopWidth: "1px" }
        }, null, -1)),
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: "sm",
          style: { margin: "10px 0", width: "66%" }
        }),
        _cache[1] || (_cache[1] = vue.createElementVNode("div", {
          class: "ele-icon-border-color-primary",
          style: { borderTopStyle: "dashed", borderTopWidth: "1px" }
        }, null, -1)),
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: "sm",
          style: { marginTop: "10px" }
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
