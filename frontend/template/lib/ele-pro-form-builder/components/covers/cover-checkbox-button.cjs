"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  margin: "0 auto",
  width: "150px",
  maxWidth: "100%"
} };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-checkbox-button",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(index.IconRadioButton), {
          size: "sm",
          type: 1,
          checked: true,
          style: { borderRight: "1px solid #fff" }
        }),
        vue.createVNode(vue.unref(index.IconRadioButton), {
          size: "sm",
          type: 2,
          checked: true
        }),
        vue.createVNode(vue.unref(index.IconRadioButton), {
          size: "sm",
          type: 3
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
