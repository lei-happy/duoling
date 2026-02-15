"use strict";
const vue = require("vue");
const props = require("./props");
const _hoisted_1 = { class: "ele-tab-nav" };
const _hoisted_2 = ["onClick"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTabBar" },
  __name: "index",
  props: props.tabBarProps,
  emits: props.tabBarEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const handleItemClick = (item) => {
      if (props2.modelValue !== item.value) {
        emit("update:modelValue", item.value);
        emit("change", item.value);
      }
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-tab-bar", { "is-plain": _ctx.type === "plain" }])
      }, [
        vue.createElementVNode("div", _hoisted_1, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.items, (item) => {
            return vue.openBlock(), vue.createElementBlock("div", {
              key: item.value,
              style: vue.normalizeStyle(_ctx.itemStyle),
              class: vue.normalizeClass(["ele-tab-item", { "is-active": item.value === _ctx.modelValue }]),
              onClick: ($event) => handleItemClick(item)
            }, [
              vue.renderSlot(_ctx.$slots, "label", {
                label: item.label,
                item
              }, () => [
                vue.createTextVNode(vue.toDisplayString(item.label), 1)
              ])
            ], 14, _hoisted_2);
          }), 128))
        ]),
        vue.renderSlot(_ctx.$slots, "extra")
      ], 2);
    };
  }
});
module.exports = _sfc_main;
