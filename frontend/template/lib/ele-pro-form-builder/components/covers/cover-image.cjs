"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-image",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(index.IconImage), { style: { margin: "0 auto" } });
    };
  }
});
module.exports = _sfc_main;
