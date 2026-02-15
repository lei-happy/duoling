"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-input",
  props: {
    size: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-icon-border-color-primary5",
        style: vue.normalizeStyle({
          display: "flex",
          alignItems: "center",
          height: __props.size === "sm" ? "20px" : "26px",
          padding: "0 6px",
          boxSizing: "border-box",
          borderStyle: "solid",
          borderWidth: "1px",
          borderRadius: "4px"
        })
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ], 4);
    };
  }
});
module.exports = _sfc_main;
