"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const DROPDOWN_KEY = Symbol(
  "dropdown"
);
function useDropdownProvider() {
  const dropdownRef = vue.ref(null);
  const dropdownVirtualRef = vue.shallowRef();
  const dropdownItems = vue.shallowRef([]);
  const dropdownProps = vue.shallowRef({});
  const openDropdown = (triggerEl, items, props) => {
    if (triggerEl == null || dropdownVirtualRef.value === triggerEl) {
      return;
    }
    dropdownRef.value && dropdownRef.value.handleClose();
    vue.nextTick(() => {
      dropdownProps.value = props || {};
      dropdownItems.value = items || [];
      dropdownVirtualRef.value = triggerEl;
      if (dropdownItems.value.length) {
        vue.nextTick(() => {
          dropdownRef.value && dropdownRef.value.handleOpen();
        });
      }
    });
  };
  vue.provide(DROPDOWN_KEY, {
    openDropdown
  });
  return {
    dropdownRef,
    dropdownVirtualRef,
    dropdownItems,
    dropdownProps,
    openDropdown
  };
}
function useDropdown() {
  return vue.inject(DROPDOWN_KEY, {});
}
exports.DROPDOWN_KEY = DROPDOWN_KEY;
exports.useDropdown = useDropdown;
exports.useDropdownProvider = useDropdownProvider;
