import { defineComponent, computed, createElementBlock, openBlock, normalizeClass, normalizeStyle, renderSlot, createBlock, createCommentVNode, normalizeProps, guardReactiveProps, unref, Teleport, createVNode, mergeProps } from "vue";
import { useContentSlot } from "../../utils/hook";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "MainContent" },
  __name: "main-content",
  props: {
    /** 内容高度 */
    wrapHeight: [String, Number]
  },
  setup(__props) {
    const props = __props;
    const contentHeight = computed(() => {
      if (props.wrapHeight != null && typeof props.wrapHeight === "number") {
        return `${props.wrapHeight}px`;
      }
      return props.wrapHeight;
    });
    const { show, slotProps, LoadingSpinner, customProps, to } = useContentSlot();
    const isShowLoading = computed(() => customProps.value && !show.value);
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        style: normalizeStyle({ height: contentHeight.value }),
        class: normalizeClass({ "ele-loading-show": isShowLoading.value })
      }, [
        renderSlot(_ctx.$slots, "default", normalizeProps(guardReactiveProps(unref(slotProps)))),
        isShowLoading.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: unref(to)
        }, [
          createVNode(unref(LoadingSpinner), mergeProps({ style: { "top": "0", "left": "0", "right": "0", "bottom": "0", "width": "100%", "height": "100%" } }, unref(customProps)), null, 16)
        ], 8, ["to"])) : createCommentVNode("", true)
      ], 6);
    };
  }
});
export {
  _sfc_main as default
};
