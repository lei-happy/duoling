"use strict";
const vue = require("vue");
const index = require("./index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-card",
  props: {
    size: {},
    checked: { type: Boolean }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass([
          { "ele-icon-border-color-primary5": __props.checked },
          { "ele-icon-border-color-base": !__props.checked }
        ]),
        style: vue.normalizeStyle({
          padding: __props.size === "sm" ? "8px" : "10px",
          borderRadius: "4px",
          borderStyle: "solid",
          borderWidth: "1px",
          position: "relative"
        })
      }, [
        vue.createVNode(vue.unref(index.IconSkeleton), {
          size: __props.size === "sm" ? "xs" : "sm"
        }, null, 8, ["size"]),
        __props.checked ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-icon-border-color-primary",
          style: vue.normalizeStyle({
            borderRadius: "2px",
            borderStyle: "solid",
            borderWidth: "4px",
            borderLeftColor: "transparent",
            borderBottomColor: "transparent",
            position: "absolute",
            right: __props.size === "sm" ? "2px" : "4px",
            top: __props.size === "sm" ? "2px" : "4px"
          })
        }, null, 4)) : vue.createCommentVNode("", true)
      ], 6);
    };
  }
});
module.exports = _sfc_main;
