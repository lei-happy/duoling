import { defineComponent, createElementBlock, openBlock, Fragment, renderSlot, createVNode, mergeProps, unref } from "vue";
import EleDropdown from "../ele-dropdown/index";
import { useDropdownProvider } from "./util";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "EleDropdownProvider" },
  __name: "index",
  setup(__props, { expose: __expose }) {
    const {
      dropdownRef,
      dropdownVirtualRef,
      dropdownItems,
      dropdownProps,
      openDropdown
    } = useDropdownProvider();
    __expose({
      openDropdown
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock(Fragment, null, [
        renderSlot(_ctx.$slots, "default"),
        createVNode(EleDropdown, mergeProps({
          triggerKeys: [],
          persistent: false
        }, unref(dropdownProps), {
          ref_key: "dropdownRef",
          ref: dropdownRef,
          componentType: "pro",
          virtualTriggering: true,
          virtualRef: unref(dropdownVirtualRef),
          disabled: !unref(dropdownItems).length,
          items: unref(dropdownItems)
        }), null, 16, ["virtualRef", "disabled", "items"])
      ], 64);
    };
  }
});
export {
  _sfc_main as default
};
