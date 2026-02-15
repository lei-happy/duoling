"use strict";
const vue = require("vue");
const EleTooltip = require("../ele-tooltip/index");
const EleText = require("../ele-text/index");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleToolbar" },
  __name: "index",
  props: props.toolbarProps,
  setup(__props, { expose: __expose }) {
    const tooltipRef = vue.ref(null);
    const virtualRef = vue.ref();
    const tooltipContent = vue.ref("");
    const tooltipProps = vue.ref({});
    const showTooltip = (text, el, options) => {
      virtualRef.value = el;
      tooltipContent.value = text ?? "";
      tooltipProps.value = options || {};
    };
    const hideTooltip = () => {
      tooltipRef.value && tooltipRef.value.hide();
    };
    const toolbarProvide = vue.shallowReactive({
      showTooltip,
      hideTooltip
    });
    vue.provide(props.TOOLBAR_KEY, toolbarProvide);
    __expose({
      tooltipRef,
      showTooltip,
      hideTooltip
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-toolbar", [
          { "is-default": "plain" !== _ctx.theme },
          { "is-plain": "plain" === _ctx.theme }
        ]])
      }, [
        _ctx.title || _ctx.subtitle ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-toolbar-title",
          style: vue.normalizeStyle(_ctx.titleStyle)
        }, [
          _ctx.title ? (vue.openBlock(), vue.createBlock(EleText, vue.mergeProps({
            key: 0,
            type: "heading"
          }, _ctx.titleProps || {}), {
            default: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(_ctx.title), 1)
            ]),
            _: 1
          }, 16)) : vue.createCommentVNode("", true),
          _ctx.subtitle ? (vue.openBlock(), vue.createBlock(EleText, vue.mergeProps({
            key: 1,
            size: "xs"
          }, _ctx.subtitleProps || {}), {
            default: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(_ctx.subtitle), 1)
            ]),
            _: 1
          }, 16)) : vue.createCommentVNode("", true)
        ], 4)) : vue.createCommentVNode("", true),
        vue.createElementVNode("div", {
          class: "ele-toolbar-body",
          style: vue.normalizeStyle(_ctx.bodyStyle)
        }, [
          vue.renderSlot(_ctx.$slots, "default")
        ], 4),
        vue.createElementVNode("div", {
          class: "ele-toolbar-tools",
          style: vue.normalizeStyle(_ctx.toolsStyle)
        }, [
          vue.renderSlot(_ctx.$slots, "tools")
        ], 4),
        vue.createVNode(EleTooltip, vue.mergeProps({
          trigger: "hover",
          placement: "top",
          persistent: false,
          content: tooltipContent.value
        }, tooltipProps.value || {}, {
          virtualTriggering: true,
          virtualRef: virtualRef.value,
          ref_key: "tooltipRef",
          ref: tooltipRef
        }), null, 16, ["content", "virtualRef"])
      ], 2);
    };
  }
});
module.exports = _sfc_main;
