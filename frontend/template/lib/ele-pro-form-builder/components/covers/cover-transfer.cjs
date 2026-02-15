"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", alignItems: "center" } };
const _hoisted_2 = { style: { display: "flex", alignItems: "center" } };
const _hoisted_3 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_4 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_5 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_6 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_7 = { style: { margin: "0 6px" } };
const _hoisted_8 = { style: { display: "flex", alignItems: "center" } };
const _hoisted_9 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_10 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_11 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _hoisted_12 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-transfer",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(index.IconPanel), {
          size: "sm",
          style: { flex: 1, marginTop: 0 }
        }, {
          default: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_2, [
              vue.createVNode(vue.unref(index.IconCheckbox), {
                size: "xs",
                checked: true
              }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_3, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_4, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_5, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_6, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ])
          ]),
          _: 1
        }),
        vue.createElementVNode("div", _hoisted_7, [
          vue.createVNode(vue.unref(index.IconArrow), { style: { marginRight: "-4px" } }),
          vue.createVNode(vue.unref(index.IconArrow), {
            direction: "left",
            style: { marginLeft: "-4px", marginTop: "6px" }
          })
        ]),
        vue.createVNode(vue.unref(index.IconPanel), {
          size: "sm",
          style: { flex: 1, marginTop: 0 }
        }, {
          default: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_8, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_9, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_10, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_11, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_12, [
              vue.createVNode(vue.unref(index.IconCheckbox), { size: "xs" }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
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
