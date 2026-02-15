"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-skeleton",
  props: {
    size: {},
    color: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass([
          { "ele-icon-bg-fill-light": __props.color !== "primary" },
          { "ele-icon-bg-primary": __props.color === "primary" }
        ]),
        style: vue.normalizeStyle({
          flexShrink: 0,
          height: { xl: "18px", lg: "12px", md: "10px", sm: "6px", xs: "4px" }[__props.size || "md"],
          borderRadius: __props.size === "sm" ? "3px" : __props.size === "xs" ? "2px" : "4px"
        })
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ], 6);
    };
  }
});
module.exports = _sfc_main;
