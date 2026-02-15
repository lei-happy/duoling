import { ref, shallowRef, provide, inject, nextTick } from "vue";
const DROPDOWN_KEY = Symbol(
  "dropdown"
);
function useDropdownProvider() {
  const dropdownRef = ref(null);
  const dropdownVirtualRef = shallowRef();
  const dropdownItems = shallowRef([]);
  const dropdownProps = shallowRef({});
  const openDropdown = (triggerEl, items, props) => {
    if (triggerEl == null || dropdownVirtualRef.value === triggerEl) {
      return;
    }
    dropdownRef.value && dropdownRef.value.handleClose();
    nextTick(() => {
      dropdownProps.value = props || {};
      dropdownItems.value = items || [];
      dropdownVirtualRef.value = triggerEl;
      if (dropdownItems.value.length) {
        nextTick(() => {
          dropdownRef.value && dropdownRef.value.handleOpen();
        });
      }
    });
  };
  provide(DROPDOWN_KEY, {
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
  return inject(DROPDOWN_KEY, {});
}
export {
  DROPDOWN_KEY,
  useDropdown,
  useDropdownProvider
};
