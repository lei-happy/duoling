"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const common = require("../utils/common");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleBacktop", inheritAttrs: false },
  __name: "index",
  props: props.backtopProps,
  emits: props.backtopEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const visible = vue.ref(false);
    const targetEl = vue.shallowRef(null);
    const updateTarget = (el) => {
      if (el !== targetEl.value && !(el == null && targetEl.value == null)) {
        targetEl.value = !el || typeof el === "string" ? null : el;
      }
    };
    const handleClick = (e) => {
      if (targetEl.value) {
        targetEl.value.scrollTo({ top: 0, behavior: "smooth" });
      }
      emit("click", e);
    };
    const handleScroll = () => {
      if (targetEl.value != null && props2.visibilityHeight != null) {
        visible.value = targetEl.value.scrollTop >= props2.visibilityHeight;
      } else {
        visible.value = false;
      }
    };
    const scrollListener = common.throttle(handleScroll, 300, true);
    const unbindEvent = () => {
      if (targetEl.value != null) {
        targetEl.value.removeEventListener("scroll", scrollListener);
        targetEl.value = null;
      }
    };
    const bindEvent = () => {
      unbindEvent();
      if (typeof props2.target === "undefined") {
        updateTarget(document.body);
      } else if (typeof props2.target === "string" && props2.target) {
        updateTarget(document.querySelector(props2.target));
      } else {
        updateTarget(props2.target);
      }
      handleScroll();
      if (targetEl.value) {
        targetEl.value.addEventListener("scroll", scrollListener);
      }
    };
    vue.watch(
      () => props2.target,
      () => {
        bindEvent();
      }
    );
    vue.onMounted(() => {
      bindEvent();
    });
    vue.onBeforeUnmount(() => {
      unbindEvent();
    });
    vue.onDeactivated(() => {
      visible.value = false;
    });
    vue.onActivated(() => {
      handleScroll();
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Transition, { name: _ctx.transitionName }, {
        default: vue.withCtx(() => [
          visible.value ? (vue.openBlock(), vue.createElementBlock("div", vue.mergeProps({ key: 0 }, _ctx.$attrs, {
            class: "ele-backtop",
            style: {
              bottom: typeof _ctx.bottom === "number" ? `${_ctx.bottom}px` : _ctx.bottom,
              right: typeof _ctx.right === "number" ? `${_ctx.right}px` : _ctx.right
            },
            onClick: handleClick
          }), [
            vue.renderSlot(_ctx.$slots, "default", {}, () => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.ArrowUp))
                ]),
                _: 1
              })
            ])
          ], 16)) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 8, ["name"]);
    };
  }
});
module.exports = _sfc_main;
