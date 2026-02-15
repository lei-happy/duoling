"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleSelectTree" },
  __name: "index",
  props: props.selectTreeProps,
  emits: props.selectTreeEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.selectTreeEmits, emit);
    const { optionData, reloadOptions } = hook.useProOptions(
      props$1,
      "data"
    );
    const treeSelectRef = vue.ref(null);
    __expose({
      reloadOptions,
      treeSelectRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTreeSelect), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["data"]), {
        ref_key: "treeSelectRef",
        ref: treeSelectRef,
        data: vue.unref(optionData),
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"]
      }), vue.createSlots({ _: 2 }, [
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["data", "onUpdate:modelValue"]);
    };
  }
});
module.exports = _sfc_main;
