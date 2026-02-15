"use strict";
const vue = require("vue");
const index = require("./index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-range-skeleton",
  props: {
    size: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: __props.size,
          style: { flex: 1 }
        }, null, 8, ["size"]),
        vue.createElementVNode("div", {
          class: "ele-icon-border-color-text",
          style: vue.normalizeStyle({
            flexShrink: 0,
            width: __props.size === "sm" ? "6px" : "8px",
            margin: __props.size === "sm" ? "0 4px" : "0 6px",
            borderTopStyle: "solid",
            borderTopWidth: "1px"
          })
        }, null, 4),
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: __props.size,
          style: { flex: 1 }
        }, null, 8, ["size"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
