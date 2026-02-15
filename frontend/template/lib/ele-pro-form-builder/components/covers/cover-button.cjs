"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-button",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(index.IconButton), {
        size: "sm",
        type: "primary",
        style: {
          margin: "0 auto",
          width: "58px",
          padding: "0 12px"
        }
      });
    };
  }
});
module.exports = _sfc_main;
