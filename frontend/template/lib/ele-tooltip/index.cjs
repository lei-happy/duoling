"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const props = require("./props");
const _hoisted_1 = ["innerHTML"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTooltip" },
  __name: "index",
  props: props.tooltipProps,
  emits: props.tooltipEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const tooltipRef = vue.ref();
    const rootProps = vue.computed(() => {
      const options = common.omit(props2, [
        "content",
        "bodyStyle",
        "bg",
        "arrowBg",
        "width",
        "isPopover",
        "onUpdate:visible",
        "onBeforeShow",
        "onBeforeHide",
        "onBefore-show",
        "onBefore-hide",
        "onShow",
        "onHide",
        "onOpen",
        "onClose"
      ]);
      const classes = ["ele-popper"];
      if (props2.isPopover && props2.effect === "light") {
        classes.push("ele-popover");
      } else {
        classes.push("ele-tooltip");
      }
      if (typeof props2.popperClass === "string" && props2.popperClass) {
        classes.push(props2.popperClass);
      }
      options.popperClass = classes.join(" ");
      const style = {};
      if (props2.bg || props2.arrowBg) {
        options.effect = "dark";
        if (props2.bg) {
          style["--ele-tooltip-bg"] = props2.bg;
        }
        if (props2.arrowBg) {
          style["--ele-tooltip-arrow-bg"] = props2.arrowBg;
        }
      }
      const { width, popperStyle } = props2;
      if (width != null) {
        style.width = typeof width === "string" ? width : `${width}px`;
      }
      if (!popperStyle) {
        options.popperStyle = style;
      } else if (Array.isArray(popperStyle)) {
        options.popperStyle = [style, ...popperStyle];
      } else {
        options.popperStyle = [style, popperStyle];
      }
      return options;
    });
    const popperRef = vue.computed(
      () => tooltipRef.value?.popperRef
    );
    const contentRef = vue.computed(
      () => tooltipRef.value?.contentRef
    );
    const isFocusInsideContent = () => {
      tooltipRef.value && tooltipRef.value.isFocusInsideContent();
    };
    const updatePopper = () => {
      tooltipRef.value && tooltipRef.value.updatePopper();
    };
    const handleOpen = (opt) => {
      tooltipRef.value && tooltipRef.value.onOpen(opt);
    };
    const handleClose = (opt) => {
      tooltipRef.value && tooltipRef.value.onClose(opt);
    };
    const hide = (opt) => {
      tooltipRef.value && tooltipRef.value.hide(opt);
    };
    const handleUpdateVisible = (visible) => {
      emit("update:visible", visible);
    };
    const handlePopBeforeShow = (e) => {
      emit("before-show", e);
    };
    const handlePopBeforeHide = (e) => {
      emit("before-hide", e);
    };
    const handlePopShow = (e) => {
      emit("show", e);
    };
    const handlePopHide = (e) => {
      emit("hide", e);
    };
    const handlePopOpen = (e) => {
      emit("open", e);
    };
    const handlePopClose = (e) => {
      emit("close", e);
    };
    __expose({
      tooltipRef,
      popperRef,
      contentRef,
      isFocusInsideContent,
      updatePopper,
      handleOpen,
      handleClose,
      onOpen: handleOpen,
      onClose: handleClose,
      hide
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTooltip), vue.mergeProps(rootProps.value, {
        ref_key: "tooltipRef",
        ref: tooltipRef,
        "onUpdate:visible": handleUpdateVisible,
        onBeforeShow: handlePopBeforeShow,
        onBeforeHide: handlePopBeforeHide,
        onShow: handlePopShow,
        onHide: handlePopHide,
        onOpen: handlePopOpen,
        onClose: handlePopClose
      }), {
        content: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "body", {}, () => [
            _ctx.rawContent && _ctx.content != null && _ctx.content != "" ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              innerHTML: _ctx.content,
              class: "ele-tooltip-body",
              style: vue.normalizeStyle(_ctx.bodyStyle)
            }, null, 12, _hoisted_1)) : (vue.openBlock(), vue.createElementBlock("div", {
              key: 1,
              class: "ele-tooltip-body",
              style: vue.normalizeStyle(_ctx.bodyStyle)
            }, [
              vue.renderSlot(_ctx.$slots, "content", {}, () => [
                vue.createTextVNode(vue.toDisplayString(_ctx.content), 1)
              ])
            ], 4))
          ])
        ]),
        default: vue.withCtx(() => [
          _ctx.$slots.default ? vue.renderSlot(_ctx.$slots, "default", { key: 0 }) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 16);
    };
  }
});
module.exports = _sfc_main;
