"use strict";
const vue = require("vue");
const hook = require("../../utils/hook");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MainContent" },
  __name: "main-content",
  props: {
    /** 内容高度 */
    wrapHeight: [String, Number]
  },
  setup(__props) {
    const props = __props;
    const contentHeight = vue.computed(() => {
      if (props.wrapHeight != null && typeof props.wrapHeight === "number") {
        return `${props.wrapHeight}px`;
      }
      return props.wrapHeight;
    });
    const { show, slotProps, LoadingSpinner, customProps, to } = hook.useContentSlot();
    const isShowLoading = vue.computed(() => customProps.value && !show.value);
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        style: vue.normalizeStyle({ height: contentHeight.value }),
        class: vue.normalizeClass({ "ele-loading-show": isShowLoading.value })
      }, [
        vue.renderSlot(_ctx.$slots, "default", vue.normalizeProps(vue.guardReactiveProps(vue.unref(slotProps)))),
        isShowLoading.value ? (vue.openBlock(), vue.createBlock(vue.Teleport, {
          key: 0,
          to: vue.unref(to)
        }, [
          vue.createVNode(vue.unref(LoadingSpinner), vue.mergeProps({ style: { "top": "0", "left": "0", "right": "0", "bottom": "0", "width": "100%", "height": "100%" } }, vue.unref(customProps)), null, 16)
        ], 8, ["to"])) : vue.createCommentVNode("", true)
      ], 6);
    };
  }
});
module.exports = _sfc_main;
