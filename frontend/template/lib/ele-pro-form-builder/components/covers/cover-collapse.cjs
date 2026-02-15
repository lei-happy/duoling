"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", flexDirection: "column" } };
const _hoisted_2 = {
  key: 0,
  style: { padding: "6px" }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-collapse",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(2, (index$1) => {
          return vue.createElementVNode("div", {
            key: index$1,
            class: "ele-icon-border-color-base",
            style: vue.normalizeStyle({
              marginTop: index$1 === 1 ? void 0 : "6px",
              borderRadius: "3px",
              borderStyle: "solid",
              borderWidth: "1px"
            })
          }, [
            vue.createElementVNode("div", {
              class: "ele-icon-border-color-base",
              style: vue.normalizeStyle({
                height: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "flex-end",
                paddingLeft: "6px",
                paddingRight: "2px",
                borderBottomStyle: index$1 === 1 ? "solid" : void 0,
                borderBottomWidth: index$1 === 1 ? "1px" : void 0
              })
            }, [
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "xs",
                style: { width: "50%", margin: "0 auto 0 0" }
              }),
              index$1 === 1 ? (vue.openBlock(), vue.createBlock(vue.unref(index.SvgIcon), {
                key: 0,
                name: "ArrowDown",
                size: "sm",
                style: { transform: "scale(0.8)" }
              })) : (vue.openBlock(), vue.createBlock(vue.unref(index.SvgIcon), {
                key: 1,
                name: "ArrowRight",
                size: "sm",
                color: "placeholder",
                style: { transform: "scale(0.8)" }
              }))
            ], 4),
            index$1 === 1 ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
              vue.createVNode(vue.unref(index.IconSkeleton), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "xs",
                style: { marginTop: "4px", width: "50%" }
              })
            ])) : vue.createCommentVNode("", true)
          ], 4);
        }), 64))
      ]);
    };
  }
});
module.exports = _sfc_main;
