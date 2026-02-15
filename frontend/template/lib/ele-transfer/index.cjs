"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTransfer" },
  __name: "index",
  props: props.transferProps,
  emits: props.transferEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.transferEmits, emit);
    const { optionData, reloadOptions } = hook.useProOptions(
      props$1,
      "data"
    );
    const transferRef = vue.ref(null);
    __expose({
      reloadOptions,
      transferRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTransfer), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["data"]), {
        ref_key: "transferRef",
        ref: transferRef,
        data: vue.unref(optionData),
        onChange: vue.unref(emitMethods)["change"],
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"],
        onLeftCheckChange: vue.unref(emitMethods)["left-check-change"],
        onRightCheckChange: vue.unref(emitMethods)["right-check-change"]
      }), vue.createSlots({ _: 2 }, [
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["data", "onChange", "onUpdate:modelValue", "onLeftCheckChange", "onRightCheckChange"]);
    };
  }
});
module.exports = _sfc_main;
