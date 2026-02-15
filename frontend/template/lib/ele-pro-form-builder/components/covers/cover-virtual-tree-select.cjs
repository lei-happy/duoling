"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", alignItems: "center" } };
const _hoisted_2 = { style: {
  display: "flex",
  alignItems: "center",
  marginTop: "4px",
  paddingLeft: "8px"
} };
const _hoisted_3 = { style: { display: "flex", alignItems: "center", marginTop: "4px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-virtual-tree-select",
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
              name: "ArrowUp",
              size: "sm",
              style: { margin: "0 0 0 auto" }
            })
          ]),
          _: 1
        }),
        vue.createVNode(vue.unref(index.IconPanel), {
          size: "sm",
          style: { paddingRight: "10px", position: "relative" }
        }, {
          default: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_1, [
              vue.createVNode(vue.unref(index.IconArrow), {
                size: "sm",
                direction: "down",
                color: "primary",
                style: { marginRight: "1px", transform: "translate(-2px, 1px)" }
              }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_2, [
              vue.createVNode(vue.unref(index.IconArrow), {
                size: "sm",
                style: { marginRight: "1px" }
              }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            vue.createElementVNode("div", _hoisted_3, [
              vue.createVNode(vue.unref(index.IconArrow), {
                size: "sm",
                style: { marginRight: "1px" }
              }),
              vue.createVNode(vue.unref(index.IconSkeleton), {
                size: "sm",
                style: { flex: 1 }
              })
            ]),
            _cache[0] || (_cache[0] = vue.createElementVNode("div", {
              class: "ele-icon-bg-primary7",
              style: {
                width: "4px",
                height: "18px",
                borderRadius: "2px",
                position: "absolute",
                top: "4px",
                right: "3px"
              }
            }, null, -1))
          ]),
          _: 1
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
