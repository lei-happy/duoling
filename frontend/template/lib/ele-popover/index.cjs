"use strict";
const vue = require("vue");
const common = require("../utils/common");
const EleTooltip = require("../ele-tooltip/index");
const props$1 = require("../ele-tooltip/props");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ElePopover" },
  __name: "index",
  props: props.popoverProps,
  emits: props.popoverEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const tooltipRef = vue.ref(null);
    const tooltipProps = vue.computed(() => {
      const keys = props$1.tooltipPropKeys.filter(
        (k) => !["content", "bodyStyle"].includes(k)
      );
      const options = common.pick(props2, keys);
      options.ariaLabel = props2.title;
      options.gpuAcceleration = props2.transition === "el-fade-in-linear";
      return options;
    });
    const hide = () => {
      tooltipRef.value && tooltipRef.value.hide();
    };
    const handleUpdateVisible = (visible) => {
      emit("update:visible", visible);
    };
    const handlePopBeforeEnter = () => {
      emit("before-enter");
    };
    const handlePopBeforeLeave = () => {
      emit("before-leave");
    };
    const handlePopAfterEnter = () => {
      emit("after-enter");
    };
    const handlePopAfterLeave = () => {
      emit("after-leave");
    };
    __expose({
      tooltipRef,
      hide
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleTooltip, vue.mergeProps({ tabindex: _ctx.tabindex }, tooltipProps.value, {
        ref_key: "tooltipRef",
        ref: tooltipRef,
        isPopover: true,
        "onUpdate:visible": handleUpdateVisible,
        onBeforeShow: handlePopBeforeEnter,
        onBeforeHide: handlePopBeforeLeave,
        onShow: handlePopAfterEnter,
        onHide: handlePopAfterLeave
      }), {
        body: vue.withCtx(() => [
          vue.createElementVNode("div", {
            class: vue.normalizeClass(["ele-popover-body", _ctx.bodyClass]),
            style: vue.normalizeStyle(_ctx.bodyStyle)
          }, [
            vue.renderSlot(_ctx.$slots, "body", {}, () => [
              _ctx.title != null && _ctx.title != "" || _ctx.$slots.title ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 0,
                class: "ele-popover-title",
                style: vue.normalizeStyle(_ctx.titleStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "title", {}, () => [
                  vue.createTextVNode(vue.toDisplayString(_ctx.title), 1)
                ])
              ], 4)) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", {
                class: "ele-popover-content",
                style: vue.normalizeStyle(_ctx.contentStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "default", {}, () => [
                  vue.createTextVNode(vue.toDisplayString(_ctx.content), 1)
                ])
              ], 4)
            ])
          ], 6)
        ]),
        default: vue.withCtx(() => [
          _ctx.$slots.reference ? vue.renderSlot(_ctx.$slots, "reference", { key: 0 }) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 16, ["tabindex"]);
    };
  }
});
module.exports = _sfc_main;
