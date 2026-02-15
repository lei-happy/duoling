"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-panel",
  props: {
    size: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-icon-border-color-base",
        style: vue.normalizeStyle({
          padding: __props.size === "sm" ? "6px" : "8px",
          margin: "6px 0 0 0",
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
