"use strict";
const vue = require("vue");
const EleDropdown = require("../ele-dropdown/index");
const util = require("./util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleDropdownProvider" },
  __name: "index",
  setup(__props, { expose: __expose }) {
    const {
      dropdownRef,
      dropdownVirtualRef,
      dropdownItems,
      dropdownProps,
      openDropdown
    } = util.useDropdownProvider();
    __expose({
      openDropdown
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.renderSlot(_ctx.$slots, "default"),
        vue.createVNode(EleDropdown, vue.mergeProps({
          triggerKeys: [],
          persistent: false
        }, vue.unref(dropdownProps), {
          ref_key: "dropdownRef",
          ref: dropdownRef,
          componentType: "pro",
          virtualTriggering: true,
          virtualRef: vue.unref(dropdownVirtualRef),
          disabled: !vue.unref(dropdownItems).length,
          items: vue.unref(dropdownItems)
        }), null, 16, ["virtualRef", "disabled", "items"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
