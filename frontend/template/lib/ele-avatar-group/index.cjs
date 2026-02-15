"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const EleTooltip = require("../ele-tooltip/index");
const props = require("./props");
const _hoisted_1 = { class: "ele-avatar-more-inner" };
const _hoisted_2 = {
  key: 0,
  class: "ele-popover-body ele-avatar-group"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleAvatarGroup" },
  __name: "index",
  props: props.avatarGroupProps,
  emits: props.avatarGroupEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const tooltipContent = vue.ref("");
    const virtualRef = vue.ref();
    const overflowVisible = vue.ref(false);
    const commonStyle = vue.computed(() => {
      if (props2.size == null || typeof props2.size === "string") {
        const obj = { large: "-12px", default: "-10px", small: "-8px" };
        return { marginLeft: props2.size ? obj[props2.size] : "-10px" };
      }
      if (typeof props2.size === "number" && props2.size >= 0) {
        return { marginLeft: `${-Math.round(props2.size / 3)}px` };
      }
      return {};
    });
    const isOverflow = vue.computed(() => {
      return props2.maxCount != null && props2.maxCount > 0 && props2.data != null && props2.data.length > props2.maxCount;
    });
    const avatarData = vue.computed(() => {
      if (props2.data == null) {
        return [];
      }
      return isOverflow.value ? props2.data.slice(0, props2.maxCount) : props2.data;
    });
    const overflowCount = vue.computed(() => {
      if (!isOverflow.value || !props2.data || props2.maxCount == null) {
        return 0;
      }
      return props2.data.length - props2.maxCount;
    });
    const overflowData = vue.computed(() => {
      if (props2.data == null || !isOverflow.value) {
        return [];
      }
      return props2.data.slice(props2.maxCount);
    });
    const handleItemHover = (item, e) => {
      if (props2.tooltip && item.label) {
        virtualRef.value = e.currentTarget;
        tooltipContent.value = item.label;
      }
    };
    const handleItemClick = (item) => {
      emit("itemClick", item);
    };
    const handleMoreClick = () => {
      emit("moreClick");
    };
    const handleError = (option) => {
      emit("error", option);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-avatar-group", { "is-hover-open": _ctx.hoverOpen }])
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(avatarData.value, (item, index) => {
          return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElAvatar), {
            key: item.key ?? `${index}-${item.value || item.label}`,
            size: _ctx.size,
            shape: _ctx.shape,
            src: item.value,
            style: vue.normalizeStyle([commonStyle.value, _ctx.itemStyle, _ctx.avatarStyle]),
            onClick: ($event) => handleItemClick(item),
            onError: (e) => handleError({ item, e }),
            onMouseover: (e) => handleItemHover(item, e)
          }, {
            default: vue.withCtx(() => [
              _ctx.$slots.item ? vue.renderSlot(_ctx.$slots, "item", {
                key: 0,
                item
              }) : vue.createCommentVNode("", true)
            ]),
            _: 2
          }, 1032, ["size", "shape", "src", "style", "onClick", "onError", "onMouseover"]);
        }), 128)),
        isOverflow.value ? (vue.openBlock(), vue.createBlock(EleTooltip, vue.mergeProps({
          key: 0,
          effect: "light",
          isPopover: true,
          gpuAcceleration: true,
          placement: "top",
          popperClass: "ele-avatar-popover",
          offset: 6
        }, _ctx.overflowPopoverProps || {}, {
          disabled: !_ctx.overflowPopover,
          visible: overflowVisible.value,
          "onUpdate:visible": _cache[0] || (_cache[0] = ($event) => overflowVisible.value = $event)
        }), {
          body: vue.withCtx(() => [
            _ctx.overflowPopover ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
              vue.renderSlot(_ctx.$slots, "overflow", { overflowData: overflowData.value }, () => [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(overflowData.value, (item, index) => {
                  return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElAvatar), {
                    key: item.key ?? `${index}-${item.value || item.label}`,
                    size: _ctx.size,
                    shape: _ctx.shape,
                    src: item.value,
                    style: vue.normalizeStyle([commonStyle.value, _ctx.itemStyle, _ctx.avatarStyle]),
                    onClick: ($event) => handleItemClick(item),
                    onError: (e) => handleError({ item, e }),
                    onMouseover: (e) => handleItemHover(item, e)
                  }, {
                    default: vue.withCtx(() => [
                      _ctx.$slots.item ? vue.renderSlot(_ctx.$slots, "item", {
                        key: 0,
                        item
                      }) : vue.createCommentVNode("", true)
                    ]),
                    _: 2
                  }, 1032, ["size", "shape", "src", "style", "onClick", "onError", "onMouseover"]);
                }), 128))
              ])
            ])) : vue.createCommentVNode("", true)
          ]),
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElAvatar), {
              size: _ctx.size,
              shape: _ctx.shape,
              style: vue.normalizeStyle([commonStyle.value, _ctx.itemStyle, _ctx.moreStyle]),
              class: "ele-avatar-more",
              onClick: handleMoreClick
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("span", _hoisted_1, [
                  vue.renderSlot(_ctx.$slots, "more", {
                    overflowCount: overflowCount.value,
                    overflowData: overflowData.value
                  }, () => [
                    vue.createElementVNode("span", null, "+" + vue.toDisplayString(overflowCount.value), 1)
                  ])
                ])
              ]),
              _: 3
            }, 8, ["size", "shape", "style"])
          ]),
          _: 3
        }, 16, ["disabled", "visible"])) : vue.createCommentVNode("", true),
        vue.createVNode(EleTooltip, vue.mergeProps({
          placement: "top",
          offset: 6
        }, _ctx.tooltipProps || {}, {
          content: tooltipContent.value,
          virtualRef: virtualRef.value,
          virtualTriggering: true
        }), null, 16, ["content", "virtualRef"])
      ], 2);
    };
  }
});
module.exports = _sfc_main;
