"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { width: "82%", margin: "0 auto" } };
const _hoisted_2 = { style: { display: "flex", alignItems: "center" } };
const _hoisted_3 = { style: { display: "flex", alignItems: "center", marginTop: "6px" } };
const _hoisted_4 = { style: { display: "flex", alignItems: "center", marginTop: "6px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-radio",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createElementVNode("div", _hoisted_2, [
          vue.createVNode(vue.unref(index.IconRadio), { size: "md" }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { flex: 1 }
          })
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          vue.createVNode(vue.unref(index.IconRadio), {
            size: "md",
            checked: true
          }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { flex: 1 }
          })
        ]),
        vue.createElementVNode("div", _hoisted_4, [
          vue.createVNode(vue.unref(index.IconRadio), { size: "md" }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { flex: 1 }
          })
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
