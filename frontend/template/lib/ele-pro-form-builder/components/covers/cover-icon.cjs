"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", alignItems: "center", justifyContent: "center" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-icon",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "CheckCircleFilled",
          style: { fontSize: "20px" }
        }),
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "StarFilled",
          color: "primary5",
          style: { fontSize: "23px", margin: "-2px 0 0 8px" }
        }),
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "StepForwardFilled",
          color: "light",
          style: { fontSize: "23px", marginLeft: "8px" }
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
