"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-input",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(index.IconInput), { size: "sm" }, {
        default: vue.withCtx(() => [
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { width: "50%" }
          }),
          vue.createVNode(vue.unref(index.IconCursor))
        ]),
        _: 1
      });
    };
  }
});
module.exports = _sfc_main;
