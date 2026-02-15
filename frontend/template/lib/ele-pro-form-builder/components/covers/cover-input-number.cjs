"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", alignItems: "center", justifyContent: "center" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-input-number",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        _cache[0] || (_cache[0] = vue.createElementVNode("div", {
          class: "ele-icon-bg-fill-light",
          style: {
            width: "20px",
            height: "20px",
            borderRadius: "4px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }
        }, [
          vue.createElementVNode("div", {
            class: "ele-icon-border-color-text-light",
            style: {
              width: "8px",
              borderTopStyle: "solid",
              borderTopWidth: "2px"
            }
          })
        ], -1)),
        _cache[1] || (_cache[1] = vue.createElementVNode("div", {
          class: "ele-icon-color-base",
          style: { padding: "0 8px", fontSize: "16px", lineHeight: 1 }
        }, " 999 ", -1)),
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "PlusOutlined",
          color: "secondary",
          class: "ele-icon-bg-fill-light",
          style: {
            width: "20px",
            height: "20px",
            borderRadius: "4px",
            fontSize: "12px"
          }
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
