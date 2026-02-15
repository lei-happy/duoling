"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { flex: 1 } };
const _hoisted_2 = { style: { flex: 1, marginLeft: "4px" } };
const _hoisted_3 = { style: { flex: 1, marginLeft: "4px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-time",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createVNode(vue.unref(index.IconInput), { size: "sm" }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { width: "50%" }
            }),
            vue.createVNode(vue.unref(index.SvgIcon), {
              name: "ClockCircleOutlined",
              size: "sm",
              style: { margin: "0 0 0 auto" }
            })
          ]),
          _: 1
        }),
        vue.createVNode(vue.unref(index.IconPanel), {
          size: "sm",
          style: { display: "flex", alignItems: "flex-start" }
        }, {
          default: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_1, [
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
            vue.createElementVNode("div", _hoisted_2, [
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
            vue.createElementVNode("div", _hoisted_3, [
              vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { marginTop: "4px" }
              }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { marginTop: "4px" }
              })
            ])
          ]),
          _: 1
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
