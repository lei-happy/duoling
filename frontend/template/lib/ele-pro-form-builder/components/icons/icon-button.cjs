"use strict";
const vue = require("vue");
const index = require("./index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-button",
  props: {
    size: {},
    type: {},
    hideSkeleton: { type: Boolean }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-icon-border-color-base", [
          { "ele-icon-bg-primary": __props.type === "primary" },
          { "ele-icon-bg-fill": __props.type !== "primary" && __props.type !== "bordered" }
        ]]),
        style: vue.normalizeStyle({
          display: "flex",
          alignItems: "center",
          height: __props.size === "sm" ? "22px" : "28px",
          padding: __props.size === "sm" ? "0 6px" : "0 10px",
          boxSizing: "border-box",
          borderRadius: "4px",
          borderStyle: __props.type === "bordered" ? "solid" : void 0,
          borderWidth: __props.type === "bordered" ? "1px" : void 0
        })
      }, [
        !__props.hideSkeleton && (__props.type === "primary" || __props.type === "bordered") ? (vue.openBlock(), vue.createBlock(vue.unref(index.IconSkeleton), {
          key: 0,
          size: __props.size === "sm" ? "xs" : "sm",
          class: vue.normalizeClass([
            { "ele-icon-bg-white": __props.type === "primary" },
            { "ele-icon-bg-fill-light": __props.type !== "primary" }
          ]),
          style: { flex: 1 }
        }, null, 8, ["size", "class"])) : vue.createCommentVNode("", true)
      ], 6);
    };
  }
});
module.exports = _sfc_main;
