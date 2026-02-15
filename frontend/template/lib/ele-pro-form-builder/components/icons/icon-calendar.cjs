"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-calendar",
  props: {
    size: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-icon-bg-calendar",
        style: vue.normalizeStyle({
          height: __props.size === "sm" ? "38px" : "66px",
          width: __props.size === "sm" ? "82px" : "144px",
          margin: "0 auto",
          backgroundPosition: "center",
          backgroundSize: __props.size === "sm" ? "12px 12px" : "20px 20px",
          maxWidth: "100%"
        })
      }, null, 4);
    };
  }
});
module.exports = _sfc_main;
