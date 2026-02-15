"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleMention" },
  __name: "index",
  props: props.mentionProps,
  emits: props.mentionEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.mentionEmits, emit);
    const { optionData, reloadOptions } = hook.useProOptions(props$1);
    const mentionRef = vue.ref(null);
    __expose({
      reloadOptions,
      mentionRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElMention), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["options"]), {
        ref_key: "mentionRef",
        ref: mentionRef,
        options: vue.unref(optionData),
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"],
        onSearch: vue.unref(emitMethods)["search"],
        onSelect: vue.unref(emitMethods)["select"],
        onFocus: vue.unref(emitMethods)["focus"],
        onBlur: vue.unref(emitMethods)["blur"]
      }), vue.createSlots({ _: 2 }, [
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["options", "onUpdate:modelValue", "onSearch", "onSelect", "onFocus", "onBlur"]);
    };
  }
});
module.exports = _sfc_main;
