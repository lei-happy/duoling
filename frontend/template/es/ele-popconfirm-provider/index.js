import { defineComponent, createElementBlock, openBlock, Fragment, renderSlot, createVNode, mergeProps, unref } from "vue";
import ElePopconfirm from "../ele-popconfirm/index";
import { usePopconfirmProvider } from "./util";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "ElePopconfirmProvider" },
  __name: "index",
  setup(__props, { expose: __expose }) {
    const {
      popconfirmRef,
      popconfirmVirtualRef,
      popconfirmProps,
      openPopconfirm
    } = usePopconfirmProvider();
    __expose({
      openPopconfirm
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock(Fragment, null, [
        renderSlot(_ctx.$slots, "default"),
        createVNode(ElePopconfirm, mergeProps({
          width: 200,
          triggerKeys: [],
          persistent: false,
          placement: "top-end"
        }, unref(popconfirmProps), {
          ref_key: "popconfirmRef",
          ref: popconfirmRef,
          virtualTriggering: true,
          virtualRef: unref(popconfirmVirtualRef)
        }), null, 16, ["virtualRef"])
      ], 64);
    };
  }
});
export {
  _sfc_main as default
};
