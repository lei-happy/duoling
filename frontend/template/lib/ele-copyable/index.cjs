"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const common = require("../utils/common");
const receiver = require("../ele-config-provider/receiver");
const EleTooltip = require("../ele-tooltip/index");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCopyable" },
  __name: "index",
  props: props.copyableProps,
  emits: props.copyableEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("copyable", props2);
    const state = { timer: null };
    const innerRef = vue.ref(null);
    const tooltipRef = vue.ref(null);
    const virtualRef = vue.ref();
    const copied = vue.ref(false);
    const updateTooltip = () => {
      tooltipRef.value && tooltipRef.value.updatePopper();
    };
    const getText = () => {
      if (props2.text) {
        return props2.text;
      }
      return innerRef.value?.innerText || "";
    };
    const handleCopyClick = () => {
      common.copyText(getText()).then(() => {
        copied.value = true;
        updateTooltip();
        state.timer && clearTimeout(state.timer);
        state.timer = setTimeout(() => {
          copied.value = false;
          updateTooltip();
        }, props2.resetAfter || 1e3);
        emit("copy");
      }).catch((error) => {
        copied.value = false;
        updateTooltip();
        emit("copy", error);
      });
    };
    const handleCopyHover = (e) => {
      if (props2.tooltip) {
        virtualRef.value = e.currentTarget;
      }
    };
    vue.onDeactivated(() => {
      state.timer && clearTimeout(state.timer);
      state.timer = null;
      copied.value = false;
    });
    vue.onBeforeUnmount(() => {
      state.timer && clearTimeout(state.timer);
      state.timer = null;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-copyable", { "ele-copyable-done": copied.value }])
      }, [
        vue.createElementVNode("div", {
          ref_key: "innerRef",
          ref: innerRef,
          class: "ele-copyable-inner",
          style: vue.normalizeStyle(_ctx.innerStyle)
        }, [
          vue.renderSlot(_ctx.$slots, "default")
        ], 4),
        vue.createElementVNode("div", {
          class: "ele-copyable-icon",
          style: vue.normalizeStyle(_ctx.customStyle),
          onMouseover: handleCopyHover,
          onClick: handleCopyClick
        }, [
          copied.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.mergeProps({ key: 0 }, _ctx.copiedIconProps || {})), {
            default: vue.withCtx(() => [
              _ctx.copiedIcon ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.copiedIcon), {
                key: 0,
                style: vue.normalizeStyle(_ctx.copiedIconStyle)
              }, null, 8, ["style"])) : (vue.openBlock(), vue.createBlock(vue.unref(index.CheckOutlined), {
                key: 1,
                style: vue.normalizeStyle(_ctx.copiedIconStyle)
              }, null, 8, ["style"]))
            ]),
            _: 1
          }, 16)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.mergeProps({ key: 1 }, _ctx.iconProps || {})), {
            default: vue.withCtx(() => [
              _ctx.icon ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.icon), {
                key: 0,
                style: vue.normalizeStyle(_ctx.iconStyle)
              }, null, 8, ["style"])) : (vue.openBlock(), vue.createBlock(vue.unref(index.CopyOutlined), {
                key: 1,
                style: vue.normalizeStyle(_ctx.iconStyle)
              }, null, 8, ["style"]))
            ]),
            _: 1
          }, 16))
        ], 36),
        vue.createVNode(EleTooltip, vue.mergeProps({
          placement: "top",
          offset: 6
        }, !_ctx.tooltip || _ctx.tooltip === true ? {} : _ctx.tooltip, {
          content: copied.value ? vue.unref(lang).copied : vue.unref(lang).copy,
          virtualRef: virtualRef.value,
          virtualTriggering: true,
          ref_key: "tooltipRef",
          ref: tooltipRef
        }), null, 16, ["content", "virtualRef"])
      ], 2);
    };
  }
});
module.exports = _sfc_main;
