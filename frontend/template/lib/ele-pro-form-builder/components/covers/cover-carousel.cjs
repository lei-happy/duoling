"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", alignItems: "center" } };
const _hoisted_2 = {
  class: "ele-icon-border-color-base",
  style: {
    flex: 1,
    height: "40px",
    borderStyle: "solid",
    borderWidth: "1px",
    borderRadius: "3px",
    margin: "0 3px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  }
};
const _hoisted_3 = { style: { display: "flex", justifyContent: "center", marginTop: "4px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-carousel",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createElementVNode("div", _hoisted_1, [
          vue.createVNode(vue.unref(index.SvgIcon), {
            name: "ArrowLeft",
            color: "placeholder",
            class: "ele-icon-border-color-base",
            style: {
              width: "10px",
              height: "10px",
              borderStyle: "solid",
              borderWidth: "1px",
              borderRadius: "50%",
              fontSize: "12px"
            },
            iconStyle: { transform: "scale(0.8)" }
          }),
          vue.createElementVNode("div", _hoisted_2, [
            vue.createVNode(vue.unref(index.IconImage), { size: "sm" })
          ]),
          vue.createVNode(vue.unref(index.SvgIcon), {
            name: "ArrowRight",
            color: "placeholder",
            class: "ele-icon-border-color-base",
            style: {
              width: "10px",
              height: "10px",
              borderStyle: "solid",
              borderWidth: "1px",
              borderRadius: "50%",
              fontSize: "12px"
            },
            iconStyle: { transform: "scale(0.8)" }
          })
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(3, (index$1) => {
            return vue.createVNode(vue.unref(index.IconSkeleton), {
              key: index$1,
              color: index$1 === 1 ? "primary" : void 0,
              style: { width: "8px", height: "2px", margin: "0 3px" }
            }, null, 8, ["color"]);
          }), 64))
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
