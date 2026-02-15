"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-radio",
  props: {
    checked: { type: Boolean },
    size: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-icon-color-secondary", [
          { "ele-icon-border-color-primary": __props.checked },
          { "ele-icon-border-color-base": !__props.checked },
          { "ele-icon-bg-white": __props.checked }
        ]]),
        style: vue.normalizeStyle({
          width: { xxl: "22px", xl: "18px", lg: "14px", md: "12px", sm: "8px" }[__props.size || "md"],
          height: { xxl: "22px", xl: "18px", lg: "14px", md: "12px", sm: "8px" }[__props.size || "md"],
          lineHeight: {
            xxl: "22px",
            xl: "18px",
            lg: "14px",
            md: "12px",
            sm: "8px"
          }[__props.size || "md"],
          borderRadius: "50%",
          textAlign: "center",
          borderStyle: "solid",
          borderWidth: __props.checked ? __props.size === "sm" ? "3px" : "4px" : "1px",
          fontSize: "12px",
          boxSizing: "border-box",
          marginRight: __props.size === "lg" || __props.size === "xl" ? "8px" : __props.size === "sm" ? "4px" : "6px"
        })
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ], 6);
    };
  }
});
module.exports = _sfc_main;
