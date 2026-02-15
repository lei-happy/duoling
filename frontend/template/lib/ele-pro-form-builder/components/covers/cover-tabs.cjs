"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", paddingRight: "12px" } };
const _hoisted_2 = {
  class: "ele-icon-border-color-base",
  style: {
    height: "42px",
    borderStyle: "solid",
    borderWidth: "1px",
    padding: "8px 6px 0 6px",
    boxSizing: "border-box"
  }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-tabs",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createElementVNode("div", _hoisted_1, [
          (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(3, (index$1) => {
            return vue.createElementVNode("div", {
              key: index$1,
              class: "ele-icon-border-color-base",
              style: {
                flex: 1,
                height: "12px",
                borderTopLeftRadius: "3px",
                borderTopRightRadius: "3px",
                borderStyle: "solid",
                borderWidth: "1px",
                borderBottom: "none",
                marginRight: "4px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }
            }, [
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "xs",
                style: { width: "68%" }
              })
            ]);
          }), 64))
        ]),
        vue.createElementVNode("div", _hoisted_2, [
          vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { marginTop: "6px", width: "50%" }
          })
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
