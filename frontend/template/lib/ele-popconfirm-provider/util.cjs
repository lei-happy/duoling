"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const POPCONFIRM_KEY = Symbol(
  "popconfirm"
);
function usePopconfirmProvider() {
  const popconfirmRef = vue.ref(null);
  const popconfirmVirtualRef = vue.shallowRef();
  const popconfirmProps = vue.shallowRef({});
  const openPopconfirm = (triggerEl, props) => {
    if (triggerEl == null || popconfirmVirtualRef.value === triggerEl) {
      return;
    }
    popconfirmRef.value && popconfirmRef.value.hidePopper();
    vue.nextTick(() => {
      popconfirmProps.value = props || {};
      popconfirmVirtualRef.value = triggerEl;
      vue.nextTick(() => {
        if (popconfirmRef.value) {
          vue.unref(popconfirmRef.value.tooltipRef)?.handleOpen?.();
        }
      });
    });
  };
  vue.provide(POPCONFIRM_KEY, {
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
  return vue.inject(POPCONFIRM_KEY, {});
}
exports.POPCONFIRM_KEY = POPCONFIRM_KEY;
exports.usePopconfirm = usePopconfirm;
exports.usePopconfirmProvider = usePopconfirmProvider;
