"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const EleTooltip = require("../ele-tooltip/index");
const props$1 = require("../ele-tooltip/props");
const index = require("../icons/index");
const props = require("./props");
const _hoisted_1 = { class: "ele-popconfirm-main" };
const _hoisted_2 = { class: "ele-popconfirm-body" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ElePopconfirm" },
  __name: "index",
  props: props.popconfirmProps,
  emits: props.popconfirmEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { t } = elementPlus.useLocale();
    const tooltipRef = vue.ref(null);
    const tooltipProps = vue.computed(() => {
      const keys = props$1.tooltipPropKeys.filter(
        (k) => !["content", "bodyStyle"].includes(k)
      );
      const options = common.pick(props2, keys);
      options.ariaLabel = props2.title;
      options.gpuAcceleration = props2.transition === "el-fade-in-linear";
      const classes = ["ele-popconfirm"];
      if (typeof props2.popperClass === "string" && props2.popperClass) {
        classes.push(props2.popperClass);
      }
      options.popperClass = classes.join(" ");
      return options;
    });
    const confirmText = vue.computed(() => {
      return props2.confirmButtonText || t("el.popconfirm.confirmButtonText");
    });
    const cancelText = vue.computed(() => {
      return props2.cancelButtonText || t("el.popconfirm.cancelButtonText");
    });
    const hidePopper = () => {
      tooltipRef.value && tooltipRef.value.hide();
    };
    const handleConfirm = (e) => {
      hidePopper();
      emit("confirm", e);
    };
    const handleCancel = (e) => {
      hidePopper();
      emit("cancel", e);
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
      hidePopper
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
            vue.createElementVNode("div", _hoisted_1, [
              !_ctx.hideIcon ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.mergeProps({ key: 0 }, _ctx.iconProps || {}, {
                style: _ctx.iconColor ? { color: _ctx.iconColor } : void 0,
                class: "ele-popconfirm-icon"
              }), {
                default: vue.withCtx(() => [
                  _ctx.icon ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.icon), {
                    key: 0,
                    style: vue.normalizeStyle(_ctx.iconStyle)
                  }, null, 8, ["style"])) : (vue.openBlock(), vue.createBlock(vue.unref(index.QuestionCircleFilled), {
                    key: 1,
                    style: vue.normalizeStyle(_ctx.iconStyle)
                  }, null, 8, ["style"]))
                ]),
                _: 1
              }, 16, ["style"])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", _hoisted_2, [
                (_ctx.content || _ctx.$slots.content) && (_ctx.title || _ctx.$slots.title) ? (vue.openBlock(), vue.createElementBlock("div", {
                  key: 0,
                  class: "ele-popconfirm-title",
                  style: vue.normalizeStyle(_ctx.titleStyle)
                }, [
                  vue.renderSlot(_ctx.$slots, "title", {}, () => [
                    vue.createTextVNode(vue.toDisplayString(_ctx.title), 1)
                  ])
                ], 4)) : vue.createCommentVNode("", true),
                vue.createElementVNode("div", {
                  class: "ele-popconfirm-content",
                  style: vue.normalizeStyle(_ctx.contentStyle)
                }, [
                  vue.renderSlot(_ctx.$slots, "content", {}, () => [
                    vue.createTextVNode(vue.toDisplayString(_ctx.content || _ctx.title), 1)
                  ])
                ], 4)
              ])
            ]),
            vue.createElementVNode("div", {
              class: "ele-popconfirm-action",
              style: vue.normalizeStyle(_ctx.footerStyle)
            }, [
              vue.renderSlot(_ctx.$slots, "actions", {
                cancel: handleCancel,
                confirm: handleConfirm,
                cancelText: cancelText.value,
                confirmText: confirmText.value
              }, () => [
                vue.renderSlot(_ctx.$slots, "action", {
                  cancel: handleCancel,
                  confirm: handleConfirm,
                  cancelText: cancelText.value,
                  confirmText: confirmText.value
                }),
                !_ctx.hideCancelButton ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), vue.mergeProps({
                  key: 0,
                  size: "small",
                  type: _ctx.cancelButtonType === "text" ? void 0 : _ctx.cancelButtonType,
                  text: _ctx.cancelButtonType === "text"
                }, _ctx.cancelButtonProps || {}, { onClick: handleCancel }), {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(vue.toDisplayString(cancelText.value), 1)
                  ]),
                  _: 1
                }, 16, ["type", "text"])) : vue.createCommentVNode("", true),
                !_ctx.hideConfirmButton ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), vue.mergeProps({
                  key: 1,
                  size: "small",
                  type: _ctx.confirmButtonType === "text" ? void 0 : _ctx.confirmButtonType,
                  text: _ctx.confirmButtonType === "text"
                }, _ctx.confirmButtonProps || {}, { onClick: handleConfirm }), {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(vue.toDisplayString(confirmText.value), 1)
                  ]),
                  _: 1
                }, 16, ["type", "text"])) : vue.createCommentVNode("", true)
              ])
            ], 4)
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
