"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCheckboxGroup" },
  __name: "index",
  props: props.checkboxGroupProps,
  emits: props.checkboxGroupEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.checkboxGroupEmits, emit);
    const { optionData, reloadOptions } = hook.useProOptions(props$1);
    const checkboxGroupRef = vue.ref(null);
    __expose({
      reloadOptions,
      checkboxGroupRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCheckboxGroup), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["type", "options"]), {
        ref_key: "checkboxGroupRef",
        ref: checkboxGroupRef,
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"],
        onChange: vue.unref(emitMethods)["change"]
      }), vue.createSlots({
        default: vue.withCtx(() => [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(optionData), (option) => {
            return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
              key: option.value
            }, [
              _ctx.type === "button" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCheckboxButton), {
                key: 0,
                label: option.label,
                value: option.value,
                disabled: option.disabled,
                name: option.name
              }, null, 8, ["label", "value", "disabled", "name"])) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCheckbox), {
                key: 1,
                label: option.label,
                value: option.value,
                disabled: option.disabled,
                border: option.border,
                name: option.name
              }, null, 8, ["label", "value", "disabled", "border", "name"]))
            ], 64);
          }), 128))
        ]),
        _: 2
      }, [
        vue.renderList(Object.keys(_ctx.$slots).filter((k) => "default" !== k), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["onUpdate:modelValue", "onChange"]);
    };
  }
});
module.exports = _sfc_main;
