"use strict";
const vue = require("vue");
const hook = require("../utils/hook");
const props$1 = require("../ele-toolbar/props");
const props = require("./props");
const _hoisted_1 = { class: "ele-tool-body" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTool" },
  __name: "index",
  props: props.toolProps,
  emits: props.toolEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const toolbarProvide = vue.inject(props$1.TOOLBAR_KEY, {});
    const [startHideTipTimer, stopHideTipTimer] = hook.useTimer(200);
    const showTooltip = (text, el, options) => {
      if (toolbarProvide.showTooltip) {
        toolbarProvide.showTooltip(text, el, options);
      }
    };
    const hideTooltip = () => {
      toolbarProvide.hideTooltip && toolbarProvide.hideTooltip();
    };
    const handleClick = (e) => {
      if (props2.clickHideTooltip) {
        startHideTipTimer(() => {
          hideTooltip();
        });
      }
      emit("click", e);
    };
    const handleMouseover = (e) => {
      if (props2.title && !props2.disabled) {
        stopHideTipTimer();
        showTooltip(props2.title, e.currentTarget, {
          placement: props2.placement,
          offset: 10
        });
      }
    };
    vue.watch([() => props2.disabled, () => props2.title], () => {
      if (!props2.title || props2.disabled) {
        hideTooltip();
      }
    });
    __expose({
      showTooltip,
      hideTooltip
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-tool",
        onClick: handleClick,
        onMouseover: handleMouseover
      }, [
        vue.createElementVNode("div", _hoisted_1, [
          vue.renderSlot(_ctx.$slots, "default")
        ])
      ], 32);
    };
  }
});
module.exports = _sfc_main;
