"use strict";
const vue = require("vue");
const props = require("./props");
const _hoisted_1 = {
  key: 0,
  class: "ele-dot-text"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleDot" },
  __name: "index",
  props: props.dotProps,
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("span", {
        class: vue.normalizeClass(["ele-dot", [
          { "is-success": "success" === _ctx.type },
          { "is-warning": "warning" === _ctx.type },
          { "is-danger": "danger" === _ctx.type },
          { "is-info": "info" === _ctx.type },
          { "is-ripple": _ctx.ripple }
        ]])
      }, [
        vue.createElementVNode("span", {
          class: "ele-dot-status",
          style: vue.normalizeStyle({ width: _ctx.size, height: _ctx.size, background: _ctx.color })
        }, [
          vue.createElementVNode("span", {
            class: "ele-dot-ripple",
            style: vue.normalizeStyle({ width: _ctx.size, height: _ctx.size, background: _ctx.color })
          }, null, 4)
        ], 4),
        _ctx.text ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_1, vue.toDisplayString(_ctx.text), 1)) : vue.createCommentVNode("", true)
      ], 2);
    };
  }
});
module.exports = _sfc_main;
