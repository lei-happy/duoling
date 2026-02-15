"use strict";
const vue = require("vue");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTable" },
  __name: "index",
  props: props.tableProps,
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("table", {
        class: vue.normalizeClass(["ele-table", [
          { "has-header": _ctx.hasHeader },
          { "has-footer": _ctx.hasFooter },
          { "is-stripe": _ctx.stripe },
          { "is-border": _ctx.border },
          { "is-large": _ctx.size === "large" },
          { "is-small": _ctx.size === "small" },
          { "is-print-skin": _ctx.printSkin }
        ]])
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ], 2);
    };
  }
});
module.exports = _sfc_main;
