"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const props = require("./props");
const defaultIconTag = "i";
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleIcon" },
  __name: "index",
  props: props.iconProps,
  setup(__props, { expose: __expose }) {
    const props2 = __props;
    const iconRef = vue.ref(null);
    const iconComponent = vue.computed(() => {
      if (props2.name != null && (props2.iconType === "fontClass" || typeof props2.name === "string" && props2.name.includes(" "))) {
        return defaultIconTag;
      }
      return props2.name;
    });
    __expose({
      iconRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
        ref_key: "iconRef",
        ref: iconRef,
        size: _ctx.size,
        color: _ctx.color
      }, {
        default: vue.withCtx(() => [
          iconComponent.value ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(iconComponent.value), {
            key: 0,
            class: vue.normalizeClass(iconComponent.value === defaultIconTag ? _ctx.name : void 0)
          }, null, 8, ["class"])) : vue.createCommentVNode("", true),
          vue.renderSlot(_ctx.$slots, "default")
        ]),
        _: 3
      }, 8, ["size", "color"]);
    };
  }
});
module.exports = _sfc_main;
