"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { display: "flex", alignItems: "center", justifyContent: "center" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-rate",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "StarFilled",
          style: { color: "#f7ba2a", fontSize: "20px" }
        }),
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "StarFilled",
          style: { color: "#f7ba2a", fontSize: "20px", marginLeft: "4px" }
        }),
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "StarFilled",
          style: { color: "#f7ba2a", fontSize: "20px", marginLeft: "4px" }
        }),
        vue.createVNode(vue.unref(index.SvgIcon), {
          name: "StarFilled",
          color: "lighter",
          style: { fontSize: "20px", marginLeft: "4px" }
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
