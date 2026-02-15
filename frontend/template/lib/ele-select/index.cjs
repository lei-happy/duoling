"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleSelect" },
  __name: "index",
  props: props.selectProps,
  emits: props.selectEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.selectEmits, emit);
    const { optionData, reloadOptions } = hook.useProOptions(props$1);
    const selectRef = vue.ref(null);
    __expose({
      reloadOptions,
      selectRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElSelect), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["options"]), {
        ref_key: "selectRef",
        ref: selectRef,
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"],
        onChange: vue.unref(emitMethods)["change"],
        onRemoveTag: vue.unref(emitMethods)["remove-tag"],
        onClear: vue.unref(emitMethods)["clear"],
        onVisibleChange: vue.unref(emitMethods)["visible-change"],
        onFocus: vue.unref(emitMethods)["focus"],
        onBlur: vue.unref(emitMethods)["blur"]
      }), vue.createSlots({
        default: vue.withCtx(() => [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(optionData), (option) => {
            return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
              key: option.value
            }, [
              option.children ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElOptionGroup), {
                key: 0,
                label: option.label
              }, {
                default: vue.withCtx(() => [
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(option.children, (childOption) => {
                    return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElOption), {
                      key: childOption.value,
                      label: childOption.label,
                      value: childOption.value,
                      disabled: childOption.disabled
                    }, null, 8, ["label", "value", "disabled"]);
                  }), 128))
                ]),
                _: 2
              }, 1032, ["label"])) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElOption), {
                key: 1,
                label: option.label,
                value: option.value,
                disabled: option.disabled
              }, null, 8, ["label", "value", "disabled"]))
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
      ]), 1040, ["onUpdate:modelValue", "onChange", "onRemoveTag", "onClear", "onVisibleChange", "onFocus", "onBlur"]);
    };
  }
});
module.exports = _sfc_main;
