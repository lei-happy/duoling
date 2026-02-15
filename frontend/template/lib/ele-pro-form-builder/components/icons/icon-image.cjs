"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-image",
  props: {
    size: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-icon-bg-fill",
        style: vue.normalizeStyle({
          width: __props.size === "sm" ? "32px" : "46px",
          height: __props.size === "sm" ? "24px" : "34px",
          borderRadius: "4px",
          position: "relative",
          overflow: "hidden"
        })
      }, [
        vue.createElementVNode("div", {
          class: "ele-icon-bg-fill-dark",
          style: vue.normalizeStyle({
            width: __props.size === "sm" ? "8px" : "12px",
            height: __props.size === "sm" ? "8px" : "12px",
            borderRadius: "50%",
            position: "absolute",
            right: __props.size === "sm" ? "4px" : "6px",
            top: __props.size === "sm" ? "4px" : "6px"
          })
        }, null, 4),
        vue.createElementVNode("div", {
          class: "ele-icon-bg-fill-dark",
          style: vue.normalizeStyle({
            width: __props.size === "sm" ? "28px" : "40px",
            height: __props.size === "sm" ? "28px" : "40px",
            borderRadius: "6px",
            transform: "rotate(45deg)",
            position: "absolute",
            bottom: __props.size === "sm" ? "-16px" : "-24px",
            left: __props.size === "sm" ? "-2px" : "-4px"
          })
        }, null, 4)
      ], 4);
    };
  }
});
module.exports = _sfc_main;
