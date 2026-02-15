import { defineComponent, ref, createBlock, openBlock, unref, mergeProps, createSlots, renderList, withCtx, renderSlot, normalizeProps, guardReactiveProps } from "vue";
import { ElAutocomplete } from "element-plus";
import { omit } from "../utils/common";
import { useComponentEvents } from "../utils/hook";
import { autocompleteEmits, autocompleteProps } from "./props";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "EleAutocomplete" },
  __name: "index",
  props: autocompleteProps,
  emits: autocompleteEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { emitMethods } = useComponentEvents(autocompleteEmits, emit);
    const autocompleteRef = ref(null);
    const handleFetchSuggestions = (keyword, callback) => {
      if (props.fetchSuggestions == null) {
        callback([]);
        return;
      }
      if (typeof props.fetchSuggestions === "function") {
        const result2 = props.fetchSuggestions(keyword, callback);
        if (result2 != null && typeof result2 === "object" && typeof result2.then === "function") {
          result2.then((data) => {
            callback(data || []);
          });
        }
        return;
      }
      const kw = (keyword ?? "").toLowerCase();
      const options = props.fetchSuggestions || [];
      const result = options.filter(
        (d) => !kw || (d.value ?? "").toLowerCase().includes(kw)
      );
      callback(result);
    };
    __expose({
      autocompleteRef
    });
    return (_ctx, _cache) => {
      return openBlock(), createBlock(unref(ElAutocomplete), mergeProps(unref(omit)(_ctx.$props, ["fetchSuggestions"]), {
        ref_key: "autocompleteRef",
        ref: autocompleteRef,
        fetchSuggestions: handleFetchSuggestions,
        "onUpdate:modelValue": unref(emitMethods)["update:modelValue"],
        onInput: unref(emitMethods)["input"],
        onChange: unref(emitMethods)["change"],
        onFocus: unref(emitMethods)["focus"],
        onBlur: unref(emitMethods)["blur"],
        onClear: unref(emitMethods)["clear"],
        onSelect: unref(emitMethods)["select"]
      }), createSlots({ _: 2 }, [
        renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: withCtx((slotProps) => [
              renderSlot(_ctx.$slots, name, normalizeProps(guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["onUpdate:modelValue", "onInput", "onChange", "onFocus", "onBlur", "onClear", "onSelect"]);
    };
  }
});
export {
  _sfc_main as default
};
