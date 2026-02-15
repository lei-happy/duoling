"use strict";
const vue = require("vue");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ElePage" },
  __name: "index",
  props: props.pageProps,
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-page", [
          { "is-plain": _ctx.plain },
          { "is-multi-card": _ctx.multiCard },
          { "is-flex-table": _ctx.flexTable && _ctx.flexTable !== "auto" },
          { "is-flex-auto-table": _ctx.flexTable === "auto" },
          { "is-hide-footer": _ctx.hideFooter }
        ]])
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ], 2);
    };
  }
});
module.exports = _sfc_main;
