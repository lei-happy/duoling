"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCascader" },
  __name: "index",
  props: props.cascaderProps,
  emits: props.cascaderEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.cascaderEmits, emit);
    const { optionData, reloadOptions } = hook.useProOptions(props$1);
    const cascaderRef = vue.ref(null);
    const cascaderPropsOption = vue.reactive({
      ...props$1.props || {},
      multiple: !!(props$1.multiple || props$1.props?.multiple)
    });
    vue.watch(
      [() => props$1.multiple, () => props$1.props],
      () => {
        const cProps = props$1.props || {};
        [
          "expandTrigger",
          "checkStrictly",
          "emitPath",
          "lazy",
          "lazyLoad",
          "value",
          "label",
          "children",
          "disabled",
          "leaf",
          "hoverThreshold"
        ].forEach((k) => {
          if (cascaderPropsOption[k] == null && cProps[k] == null) {
            return;
          }
          if (cascaderPropsOption[k] !== cProps[k]) {
            cascaderPropsOption[k] = cProps[k];
          }
        });
        if (props$1.multiple) {
          if (!cascaderPropsOption.multiple) {
            cascaderPropsOption.multiple = true;
          }
        } else if (!!cascaderPropsOption.multiple !== !!cProps.multiple) {
          cascaderPropsOption.multiple = cProps.multiple;
        }
      },
      {
        immediate: true,
        deep: true
      }
    );
    __expose({
      reloadOptions,
      cascaderRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCascader), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["props", "options", "multiple"]), {
        ref_key: "cascaderRef",
        ref: cascaderRef,
        props: cascaderPropsOption,
        options: vue.unref(optionData),
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"],
        onChange: vue.unref(emitMethods)["change"],
        onFocus: vue.unref(emitMethods)["focus"],
        onBlur: vue.unref(emitMethods)["blur"],
        onClear: vue.unref(emitMethods)["clear"],
        onVisibleChange: vue.unref(emitMethods)["visibleChange"],
        onExpandChange: vue.unref(emitMethods)["expandChange"],
        onRemoveTag: vue.unref(emitMethods)["removeTag"]
      }), vue.createSlots({ _: 2 }, [
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["props", "options", "onUpdate:modelValue", "onChange", "onFocus", "onBlur", "onClear", "onVisibleChange", "onExpandChange", "onRemoveTag"]);
    };
  }
});
module.exports = _sfc_main;
