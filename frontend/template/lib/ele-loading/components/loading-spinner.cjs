"use strict";
const vue = require("vue");
const props = require("../props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "LoadingSpinner" },
  __name: "loading-spinner",
  props: {
    ...props.loadingProps,
    plain: {
      type: Boolean,
      default: true
    }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        style: vue.normalizeStyle(_ctx.spinnerStyle),
        class: vue.normalizeClass(["ele-loading-spinner", [
          { "ele-loading": __props.plain },
          { "ele-loading-blur": _ctx.blur },
          { "ele-loading-small": _ctx.size === "small" },
          { "ele-loading-large": _ctx.size === "large" },
          { "ele-loading-spinner-show": _ctx.loading }
        ]])
      }, [
        vue.renderSlot(_ctx.$slots, "spinner", {}, () => [
          _cache[0] || (_cache[0] = vue.createElementVNode("div", { class: "ele-loading-dot" }, [
            vue.createElementVNode("i"),
            vue.createElementVNode("i"),
            vue.createElementVNode("i"),
            vue.createElementVNode("i")
          ], -1))
        ]),
        _ctx.text ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-loading-text",
          style: vue.normalizeStyle(_ctx.textStyle)
        }, vue.toDisplayString(_ctx.text), 5)) : vue.createCommentVNode("", true)
      ], 6);
    };
  }
});
module.exports = _sfc_main;
