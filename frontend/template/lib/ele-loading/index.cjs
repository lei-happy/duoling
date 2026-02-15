"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const ReceiverView = require("../ele-config-provider/components/receiver-view");
const LoadingSpinner = require("./components/loading-spinner");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleLoading", inheritAttrs: false },
  __name: "index",
  props: props.loadingProps,
  setup(__props) {
    const props2 = __props;
    const isCircle = vue.computed(() => {
      return props2.type === "circle";
    });
    return (_ctx, _cache) => {
      return _ctx.plain ? (vue.openBlock(), vue.createBlock(LoadingSpinner, vue.mergeProps({ key: 0 }, _ctx.$attrs, {
        loading: _ctx.loading,
        text: _ctx.text,
        blur: _ctx.blur,
        size: _ctx.size,
        spinnerStyle: _ctx.spinnerStyle,
        textStyle: _ctx.textStyle,
        plain: true
      }), {
        default: vue.withCtx(() => [
          _ctx.$slots.spinner ? vue.renderSlot(_ctx.$slots, "spinner", { key: 0 }) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 16, ["loading", "text", "blur", "size", "spinnerStyle", "textStyle"])) : vue.withDirectives((vue.openBlock(), vue.createBlock(vue.unref(ReceiverView), vue.mergeProps({ key: 1 }, _ctx.$attrs, {
        "element-loading-text": isCircle.value ? _ctx.text : void 0,
        "element-loading-background": isCircle.value ? _ctx.background : void 0,
        "element-loading-spinner": isCircle.value ? _ctx.spinner : void 0,
        "element-loading-svg-view-box": isCircle.value ? _ctx.svgViewBox : void 0,
        class: ["ele-loading", { "ele-loading-show": _ctx.loading }]
      }), {
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "default"),
          !isCircle.value ? (vue.openBlock(), vue.createBlock(LoadingSpinner, {
            key: 0,
            loading: _ctx.loading,
            text: _ctx.text,
            blur: _ctx.blur,
            size: _ctx.size,
            spinnerStyle: _ctx.spinnerStyle,
            textStyle: _ctx.textStyle,
            plain: false
          }, {
            default: vue.withCtx(() => [
              _ctx.$slots.spinner ? vue.renderSlot(_ctx.$slots, "spinner", { key: 0 }) : vue.createCommentVNode("", true)
            ]),
            _: 3
          }, 8, ["loading", "text", "blur", "size", "spinnerStyle", "textStyle"])) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 16, ["element-loading-text", "element-loading-background", "element-loading-spinner", "element-loading-svg-view-box", "class"])), [
        [vue.unref(elementPlus.vLoading), isCircle.value && _ctx.loading]
      ]);
    };
  }
});
module.exports = _sfc_main;
