"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = {
  class: "ele-icon-border-color-base",
  style: {
    borderStyle: "solid",
    borderWidth: "1px",
    borderRadius: "4px"
  }
};
const _hoisted_2 = {
  class: "ele-icon-border-color-base",
  style: {
    padding: "8px 10px",
    borderBottomStyle: "solid",
    borderBottomWidth: "1px"
  }
};
const _hoisted_3 = { style: { padding: "8px 10px 12px 10px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-card",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createElementVNode("div", _hoisted_2, [
          vue.createVNode(vue.unref(index.IconSkeleton), {
            style: { width: "38px" },
            size: "sm"
          })
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { marginTop: "10px", width: "50%" }
          })
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
