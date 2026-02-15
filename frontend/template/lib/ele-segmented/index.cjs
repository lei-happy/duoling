"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const util = require("../ele-basic-select/util");
const props = require("./props");
const _hoisted_1 = {
  key: 1,
  class: "ele-segmented-item-label"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleSegmented" },
  __name: "index",
  props: props.segmentedProps,
  emits: props.segmentedEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { validateChange } = util.useFormValidate();
    const tabRef = vue.ref(null);
    const isEmptyActive = vue.computed(() => {
      return props2.modelValue == null || !props2.items || !props2.items.some((d) => d.value === props2.modelValue);
    });
    const handleUpdateModelValue = (value) => {
      if (props2.modelValue !== value) {
        emit("update:modelValue", value);
        if (props2.validateEvent) {
          validateChange();
        }
        emit("change", value);
      }
    };
    const getWrapEl = () => {
      const tabEl = tabRef.value ? tabRef.value.$el : void 0;
      const headerEl = tabEl ? tabEl.querySelector(".el-tabs__header") : void 0;
      return headerEl ? headerEl.querySelector(".el-tabs__nav") : void 0;
    };
    const updateActiveBar = () => {
      const el = getWrapEl();
      if (el) {
        const bar = el.querySelector(".el-tabs__active-bar");
        if (bar) {
          bar.style.width = "0px";
        }
      }
    };
    __expose({
      tabRef,
      updateActiveBar
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTabs), {
        ref_key: "tabRef",
        ref: tabRef,
        modelValue: _ctx.modelValue,
        stretch: _ctx.block,
        class: vue.normalizeClass(["ele-segmented", [
          { "is-block": _ctx.block },
          { "is-large": _ctx.size === "large" },
          { "is-small": _ctx.size === "small" },
          { "is-disabled": _ctx.disabled },
          { "is-single": _ctx.items && _ctx.items.length === 1 },
          { "is-empty": isEmptyActive.value }
        ]]),
        "onUpdate:modelValue": handleUpdateModelValue
      }, {
        default: vue.withCtx(() => [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.items, (item, index) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTabPane), {
              key: `${index}-${item.value}-${item.label}`,
              name: item.value,
              disabled: _ctx.disabled || item.disabled
            }, {
              label: vue.withCtx(() => [
                vue.renderSlot(_ctx.$slots, "label", { item }, () => [
                  item.icon ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.mergeProps({
                    key: 0,
                    ref_for: true
                  }, item.iconProps || {}, { class: "ele-segmented-item-icon" }), {
                    default: vue.withCtx(() => [
                      (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(item.icon), {
                        style: vue.normalizeStyle(item.iconStyle)
                      }, null, 8, ["style"]))
                    ]),
                    _: 2
                  }, 1040)) : vue.createCommentVNode("", true),
                  item.label ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, vue.toDisplayString(item.label), 1)) : vue.createCommentVNode("", true)
                ])
              ]),
              _: 2
            }, 1032, ["name", "disabled"]);
          }), 128))
        ]),
        _: 3
      }, 8, ["modelValue", "stretch", "class"]);
    };
  }
});
module.exports = _sfc_main;
