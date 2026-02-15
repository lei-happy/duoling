"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-mention",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createVNode(vue.unref(index.IconInput), { size: "sm" }, {
          default: vue.withCtx(() => [
            _cache[0] || (_cache[0] = vue.createElementVNode("div", {
              class: "ele-icon-color-primary",
              style: {
                fontSize: "13px",
                fontWeight: "bold",
                lineHeight: "13px",
                fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color emoji",
                margin: "0 2px 0 -2px",
                transform: "translateY(-1px)"
              }
            }, " @ ", -1)),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { width: "50%" }
            }),
            vue.createVNode(vue.unref(index.IconCursor))
          ]),
          _: 1
        }),
        vue.createVNode(vue.unref(index.IconPanel), { size: "sm" }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { marginTop: "4px" }
            }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { marginTop: "4px" }
            })
          ]),
          _: 1
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
