"use strict";
const vue = require("vue");
const index = require("./index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-table",
  props: {
    size: {},
    multiple: { type: Boolean }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-icon-border-color-base",
        style: vue.normalizeStyle({
          borderStyle: "solid",
          borderWidth: "1px",
          borderRadius: __props.size === "sm" ? "2px" : "4px"
        })
      }, [
        vue.createVNode(vue.unref(index.IconTableRow), {
          size: __props.size,
          multiple: __props.multiple,
          class: "ele-icon-bg-fill",
          style: vue.normalizeStyle({ borderRadius: __props.size === "sm" ? "2px 2px 0 0" : "4px 4px 0 0" })
        }, {
          default: vue.withCtx(() => [
            vue.createElementVNode("div", {
              style: vue.normalizeStyle({ flex: 1, marginLeft: __props.size === "sm" ? "4px" : "6px" })
            }, null, 4),
            vue.createElementVNode("div", {
              class: "ele-icon-border-color-base",
              style: vue.normalizeStyle({
                flex: 1,
                height: __props.size === "sm" ? "4px" : "8px",
                borderLeftStyle: "solid",
                borderLeftWidth: "1px",
                borderRightStyle: "solid",
                borderRightWidth: "1px"
              })
            }, null, 4),
            _cache[0] || (_cache[0] = vue.createElementVNode("div", { style: { flex: 1 } }, null, -1))
          ]),
          _: 1
        }, 8, ["size", "multiple", "style"]),
        vue.createVNode(vue.unref(index.IconTableRow), {
          size: __props.size,
          multiple: __props.multiple,
          checkboxChecked: true
        }, null, 8, ["size", "multiple"]),
        vue.createVNode(vue.unref(index.IconTableRow), {
          size: __props.size,
          multiple: __props.multiple
        }, null, 8, ["size", "multiple"]),
        vue.createVNode(vue.unref(index.IconTableRow), {
          size: __props.size,
          multiple: __props.multiple,
          style: { border: "none" }
        }, null, 8, ["size", "multiple"])
      ], 4);
    };
  }
});
module.exports = _sfc_main;
