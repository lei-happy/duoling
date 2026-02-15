"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const EleTooltip = require("../ele-tooltip/index");
const receiver = require("../ele-config-provider/receiver");
const util = require("./util");
const props = require("./props");
const _hoisted_1 = {
  key: 0,
  class: "ele-popover-body"
};
const _hoisted_2 = {
  key: 0,
  class: "ele-tour-title"
};
const _hoisted_3 = { class: "ele-tour-text" };
const _hoisted_4 = { class: "ele-tour-footer" };
const _hoisted_5 = { class: "ele-tour-counter" };
const _hoisted_6 = { class: "ele-tour-action" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTour", inheritAttrs: false },
  __name: "index",
  props: props.tourProps,
  emits: props.tourEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("tour", props2);
    const triggerRef = vue.ref(null);
    const tooltipRef = vue.ref(null);
    const tooltipProps = vue.shallowRef({});
    const visible = vue.ref(false);
    const step = vue.shallowRef(null);
    const isLast = vue.ref(false);
    const boxStyle = vue.ref({});
    const showMask = vue.ref(false);
    const start = () => {
      if (!props2.steps || props2.modelValue == null || props2.modelValue < 0 || props2.modelValue >= props2.steps.length) {
        close();
        return;
      }
      step.value = props2.steps[props2.modelValue];
      if (!step.value) {
        return;
      }
      isLast.value = props2.modelValue === props2.steps.length - 1;
      const { mask, popoverProps, target, padding } = step.value;
      showMask.value = mask ?? props2.mask;
      const el = typeof target === "function" ? target() : target;
      if (el) {
        util.scrollIntoView(el);
        const { width, height } = el.getBoundingClientRect();
        const { top, left } = util.getOffset(el);
        const space = padding ?? props2.padding ?? 0;
        boxStyle.value = {
          width: width + space + space + "px",
          height: height + space + space + "px",
          top: top - space + "px",
          left: left - space + "px"
        };
      } else {
        boxStyle.value = {
          width: "0px",
          height: "0px",
          top: "50%",
          left: "50%"
        };
      }
      visible.value = true;
      tooltipProps.value = util.getPopperProps(true, !el, popoverProps);
      vue.nextTick(() => {
        updatePopper();
      });
    };
    const close = () => {
      visible.value = false;
      boxStyle.value = {};
      step.value = null;
      showMask.value = false;
      tooltipProps.value = util.getPopperProps();
    };
    const updateModelValue = (value) => {
      emit("update:modelValue", value);
    };
    const handlePrev = () => {
      if (props2.modelValue != null && props2.steps != null && props2.steps.length && props2.modelValue > 0) {
        updateModelValue(props2.modelValue - 1);
      }
    };
    const handleNext = () => {
      if (props2.modelValue != null && props2.steps != null && props2.steps.length && props2.modelValue < props2.steps.length - 1) {
        updateModelValue(props2.modelValue + 1);
      }
    };
    const handleFinish = () => {
      updateModelValue(null);
    };
    const updatePopper = () => {
      tooltipRef.value && tooltipRef.value.updatePopper();
    };
    vue.onMounted(() => {
      start();
    });
    vue.watch(
      () => props2.modelValue,
      () => {
        start();
      }
    );
    __expose({
      tooltipRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Teleport, { to: "body" }, [
        vue.createElementVNode("div", vue.mergeProps(_ctx.$attrs, {
          class: ["ele-tour", [{ "show-mask": showMask.value }, { "is-open": visible.value }]],
          style: { zIndex: _ctx.zIndex }
        }), [
          vue.createElementVNode("div", {
            class: "ele-tour-box",
            style: vue.normalizeStyle(boxStyle.value)
          }, null, 4),
          vue.createElementVNode("div", {
            ref_key: "triggerRef",
            ref: triggerRef,
            class: "ele-tour-reference",
            style: vue.normalizeStyle(boxStyle.value)
          }, null, 4),
          vue.createVNode(EleTooltip, vue.mergeProps(tooltipProps.value, {
            ref_key: "tooltipRef",
            ref: tooltipRef,
            virtualRef: triggerRef.value,
            virtualTriggering: true,
            disabled: !visible.value,
            hideAfter: 0
          }), {
            body: vue.withCtx(() => [
              _ctx.steps && step.value ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
                step.value.title ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
                  vue.renderSlot(_ctx.$slots, "title", {
                    step: step.value,
                    current: _ctx.modelValue
                  }, () => [
                    vue.createTextVNode(vue.toDisplayString(step.value.title), 1)
                  ])
                ])) : vue.createCommentVNode("", true),
                vue.createElementVNode("div", _hoisted_3, [
                  vue.renderSlot(_ctx.$slots, "text", {
                    step: step.value,
                    current: _ctx.modelValue
                  }, () => [
                    vue.createTextVNode(vue.toDisplayString(step.value.description), 1)
                  ])
                ]),
                vue.renderSlot(_ctx.$slots, "footer", {
                  step: step.value,
                  current: _ctx.modelValue
                }, () => [
                  vue.createElementVNode("div", _hoisted_4, [
                    vue.createElementVNode("div", _hoisted_5, vue.toDisplayString((_ctx.modelValue || 0) + 1) + "/" + vue.toDisplayString(_ctx.steps.length), 1),
                    vue.createElementVNode("div", _hoisted_6, [
                      !isLast.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                        key: 0,
                        size: "small",
                        onClick: handleFinish
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode(vue.toDisplayString(vue.unref(lang).skip), 1)
                        ]),
                        _: 1
                      })) : vue.createCommentVNode("", true),
                      _ctx.modelValue !== 0 ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                        key: 1,
                        size: "small",
                        onClick: handlePrev
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode(vue.toDisplayString(vue.unref(lang).prev), 1)
                        ]),
                        _: 1
                      })) : vue.createCommentVNode("", true),
                      !isLast.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                        key: 2,
                        size: "small",
                        type: "primary",
                        onClick: handleNext
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode(vue.toDisplayString(vue.unref(lang).next), 1)
                        ]),
                        _: 1
                      })) : vue.createCommentVNode("", true),
                      isLast.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                        key: 3,
                        size: "small",
                        type: "primary",
                        onClick: handleFinish
                      }, {
                        default: vue.withCtx(() => [
                          vue.createTextVNode(vue.toDisplayString(vue.unref(lang).finish), 1)
                        ]),
                        _: 1
                      })) : vue.createCommentVNode("", true)
                    ])
                  ])
                ])
              ])) : vue.createCommentVNode("", true)
            ]),
            _: 3
          }, 16, ["virtualRef", "disabled"])
        ], 16)
      ]);
    };
  }
});
module.exports = _sfc_main;
