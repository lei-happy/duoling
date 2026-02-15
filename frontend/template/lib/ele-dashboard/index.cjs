"use strict";
const vue = require("vue");
const props = require("./props");
const _hoisted_1 = { class: "ele-dashboard-inner" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleDashboard" },
  __name: "index",
  props: props.dashboardProps,
  setup(__props) {
    const props2 = __props;
    const rootStyle = vue.computed(() => {
      const style = {};
      if (props2.size != null) {
        if (typeof props2.size === "number") {
          style.width = `${props2.size}px`;
          style.height = `${props2.size}px`;
        } else {
          style.width = props2.size;
          style.height = props2.size;
        }
      }
      if (props2.space != null) {
        style["--ele-dashboard-space"] = typeof props2.space === "number" ? `${props2.space}px` : props2.space;
      }
      if (props2.color) {
        style["--ele-dashboard-color"] = props2.color;
      }
      return style;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-dashboard", [
          { "is-success": _ctx.type === "success" },
          { "is-warning": _ctx.type === "warning" },
          { "is-danger": _ctx.type === "danger" }
        ]]),
        style: vue.normalizeStyle(rootStyle.value)
      }, [
        vue.createElementVNode("div", _hoisted_1, [
          vue.renderSlot(_ctx.$slots, "default")
        ]),
        _cache[0] || (_cache[0] = vue.createElementVNode("div", { class: "ele-dashboard-outer" }, [
          vue.createElementVNode("div", { class: "ele-dashboard-bg" }),
          vue.createElementVNode("div", { class: "ele-dashboard-bg" }),
          vue.createElementVNode("div", { class: "ele-dashboard-bg" })
        ], -1))
      ], 6);
    };
  }
});
module.exports = _sfc_main;
