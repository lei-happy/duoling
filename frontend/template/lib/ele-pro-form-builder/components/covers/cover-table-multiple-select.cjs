"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-table-multiple-select",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createVNode(vue.unref(index.IconInput), { size: "sm" }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { flex: 1, maxWidth: "32px" }
            }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { flex: 1, maxWidth: "32px", margin: "0 0 0 6px" }
            }),
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { flex: 1, maxWidth: "32px", margin: "0 6px 0 6px" }
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
          style: { paddingTop: "4px", paddingBottom: "4px" }
        }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(index.IconTable), {
              size: "sm",
              multiple: true
            })
          ]),
          _: 1
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
