"use strict";
const vue = require("vue");
const BuilderToolWrapper = require("./builder-tool-wrapper");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "BuilderWrapper" },
  __name: "builder-wrapper",
  props: {
    item: {},
    activeItemKey: {},
    handle: { type: Boolean }
  },
  emits: ["update:activeItemKey"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const handleItemBuilderWrapperClick = () => {
      emit("update:activeItemKey", props.item.key);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-pro-form-builder-item-wrapper", [
          { "is-div-type": __props.item.type === "div" },
          { "is-active": __props.activeItemKey != null && __props.activeItemKey === __props.item.key }
        ]]),
        onClick: vue.withModifiers(handleItemBuilderWrapperClick, ["stop"])
      }, [
        vue.renderSlot(_ctx.$slots, "default"),
        vue.createVNode(BuilderToolWrapper, {
          item: __props.item,
          activeItemKey: __props.activeItemKey,
          handle: __props.handle
        }, vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1032, ["item", "activeItemKey", "handle"])
      ], 2);
    };
  }
});
module.exports = _sfc_main;
