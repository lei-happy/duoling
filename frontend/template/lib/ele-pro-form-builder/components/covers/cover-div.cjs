"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = {
  class: "ele-icon-border-color-base",
  style: {
    padding: "8px 6px 18px 6px",
    borderStyle: "solid",
    borderWidth: "1px",
    borderRadius: "4px"
  }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-div",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: "sm",
          style: { marginTop: "6px" }
        }),
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: "sm",
          style: { marginTop: "6px", width: "50%" }
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
