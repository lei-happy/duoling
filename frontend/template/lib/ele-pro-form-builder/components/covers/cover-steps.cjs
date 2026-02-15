"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", position: "relative" } };
const _hoisted_2 = { style: { flex: 1, paddingTop: "3px" } };
const _hoisted_3 = { style: { display: "flex", marginTop: "8px", position: "relative" } };
const _hoisted_4 = { style: { flex: 1, paddingTop: "3px" } };
const _hoisted_5 = { style: { display: "flex", marginTop: "8px" } };
const _hoisted_6 = { style: { flex: 1, paddingTop: "3px" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-steps",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createElementVNode("div", _hoisted_1, [
          vue.createVNode(vue.unref(index.IconRadio), {
            size: "xl",
            class: "ele-icon-bg-primary9",
            style: {
              border: "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.SvgIcon), {
                name: "CheckOutlined",
                size: "sm"
              })
            ]),
            _: 1
          }),
          vue.createElementVNode("div", _hoisted_2, [
            vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "xs",
              style: { marginTop: "4px", width: "60%" }
            })
          ]),
          _cache[0] || (_cache[0] = vue.createElementVNode("div", {
            class: "ele-icon-border-color-primary",
            style: {
              borderLeftStyle: "solid",
              borderLeftWidth: "1px",
              height: "6px",
              position: "absolute",
              top: "19px",
              left: "9px"
            }
          }, null, -1))
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          vue.createVNode(vue.unref(index.IconRadio), {
            size: "xl",
            class: "ele-icon-bg-primary",
            style: { color: "#fff", border: "none" }
          }, {
            default: vue.withCtx(() => [..._cache[1] || (_cache[1] = [
              vue.createTextVNode(" 2 ", -1)
            ])]),
            _: 1
          }),
          vue.createElementVNode("div", _hoisted_4, [
            vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "xs",
              style: { marginTop: "4px", width: "60%" }
            })
          ]),
          _cache[2] || (_cache[2] = vue.createElementVNode("div", {
            class: "ele-icon-border-color-base",
            style: {
              borderLeftStyle: "solid",
              borderLeftWidth: "1px",
              height: "6px",
              position: "absolute",
              top: "19px",
              left: "9px"
            }
          }, null, -1))
        ]),
        vue.createElementVNode("div", _hoisted_5, [
          vue.createVNode(vue.unref(index.IconRadio), {
            size: "xl",
            class: "ele-icon-bg-fill-lighter",
            style: { border: "none" }
          }, {
            default: vue.withCtx(() => [..._cache[3] || (_cache[3] = [
              vue.createTextVNode(" 3 ", -1)
            ])]),
            _: 1
          }),
          vue.createElementVNode("div", _hoisted_6, [
            vue.createVNode(vue.unref(index.IconSkeleton), { size: "sm" }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "xs",
              style: { marginTop: "4px", width: "60%" }
            })
          ])
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
