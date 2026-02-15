"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleAutocomplete" },
  __name: "index",
  props: props.autocompleteProps,
  emits: props.autocompleteEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { emitMethods } = hook.useComponentEvents(props.autocompleteEmits, emit);
    const autocompleteRef = vue.ref(null);
    const handleFetchSuggestions = (keyword, callback) => {
      if (props$1.fetchSuggestions == null) {
        callback([]);
        return;
      }
      if (typeof props$1.fetchSuggestions === "function") {
        const result2 = props$1.fetchSuggestions(keyword, callback);
        if (result2 != null && typeof result2 === "object" && typeof result2.then === "function") {
          result2.then((data) => {
            callback(data || []);
          });
        }
        return;
      }
      const kw = (keyword ?? "").toLowerCase();
      const options = props$1.fetchSuggestions || [];
      const result = options.filter(
        (d) => !kw || (d.value ?? "").toLowerCase().includes(kw)
      );
      callback(result);
    };
    __expose({
      autocompleteRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElAutocomplete), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["fetchSuggestions"]), {
        ref_key: "autocompleteRef",
        ref: autocompleteRef,
        fetchSuggestions: handleFetchSuggestions,
        "onUpdate:modelValue": vue.unref(emitMethods)["update:modelValue"],
        onInput: vue.unref(emitMethods)["input"],
        onChange: vue.unref(emitMethods)["change"],
        onFocus: vue.unref(emitMethods)["focus"],
        onBlur: vue.unref(emitMethods)["blur"],
        onClear: vue.unref(emitMethods)["clear"],
        onSelect: vue.unref(emitMethods)["select"]
      }), vue.createSlots({ _: 2 }, [
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["onUpdate:modelValue", "onInput", "onChange", "onFocus", "onBlur", "onClear", "onSelect"]);
    };
  }
});
module.exports = _sfc_main;
