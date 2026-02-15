import { ref, shallowRef, provide, inject, nextTick, unref } from "vue";
const POPCONFIRM_KEY = Symbol(
  "popconfirm"
);
function usePopconfirmProvider() {
  const popconfirmRef = ref(null);
  const popconfirmVirtualRef = shallowRef();
  const popconfirmProps = shallowRef({});
  const openPopconfirm = (triggerEl, props) => {
    if (triggerEl == null || popconfirmVirtualRef.value === triggerEl) {
      return;
    }
    popconfirmRef.value && popconfirmRef.value.hidePopper();
    nextTick(() => {
      popconfirmProps.value = props || {};
      popconfirmVirtualRef.value = triggerEl;
      nextTick(() => {
        if (popconfirmRef.value) {
          unref(popconfirmRef.value.tooltipRef)?.handleOpen?.();
        }
      });
    });
  };
  provide(POPCONFIRM_KEY, {
    openPopconfirm
  });
  return {
    popconfirmRef,
    popconfirmVirtualRef,
    popconfirmProps,
    openPopconfirm
  };
}
function usePopconfirm() {
  return inject(POPCONFIRM_KEY, {});
}
export {
  POPCONFIRM_KEY,
  usePopconfirm,
  usePopconfirmProvider
};
