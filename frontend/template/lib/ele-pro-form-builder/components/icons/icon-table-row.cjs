"use strict";
const vue = require("vue");
const index = require("./index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-table-row",
  props: {
    size: {},
    multiple: { type: Boolean },
    checkboxChecked: { type: Boolean },
    skeletonStyle: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-icon-border-color-base",
        style: vue.normalizeStyle({
          display: "flex",
          alignItems: "center",
          borderBottomStyle: "solid",
          borderBottomWidth: "1px",
          boxSizing: "border-box",
          padding: __props.size === "sm" ? "0 8px 0 4px" : "0 12px 0 6px",
          height: __props.size === "sm" ? "9px" : "15px"
        })
      }, [
        __props.multiple ? (vue.openBlock(), vue.createBlock(vue.unref(index.IconCheckbox), {
          key: 0,
          size: __props.size === "sm" ? "xs" : "sm",
          checked: __props.checkboxChecked,
          style: { margin: "0" }
        }, null, 8, ["size", "checked"])) : vue.createCommentVNode("", true),
        vue.renderSlot(_ctx.$slots, "default", {}, () => [
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: __props.size === "sm" ? "xs" : "sm",
            style: vue.normalizeStyle({
              flex: 1,
              marginLeft: __props.size === "sm" ? "4px" : "6px",
              ...__props.skeletonStyle || {}
            })
          }, null, 8, ["size", "style"]),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: __props.size === "sm" ? "xs" : "sm",
            style: vue.normalizeStyle({
              flex: 1,
              marginLeft: __props.size === "sm" ? "8px" : "12px",
              ...__props.skeletonStyle || {}
            })
          }, null, 8, ["size", "style"]),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: __props.size === "sm" ? "xs" : "sm",
            style: vue.normalizeStyle({
              flex: 1,
              marginLeft: __props.size === "sm" ? "8px" : "12px",
              ...__props.skeletonStyle || {}
            })
          }, null, 8, ["size", "style"])
        ])
      ], 4);
    };
  }
});
module.exports = _sfc_main;
