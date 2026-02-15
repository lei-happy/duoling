"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const hook = require("../utils/hook");
const MainContent = require("../ele-loading/components/main-content");
const util = require("../ele-pro-layout/util");
const props = require("./props");
const _hoisted_1 = { class: "ele-split-panel-tools" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleSplitPanel" },
  __name: "index",
  props: props.splitPanelProps,
  emits: props.splitPanelEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const isResponsive = util.useResponsive(props2);
    const wrapperRef = vue.ref(null);
    const sideWrapperRef = vue.ref(null);
    const isCollapse = vue.ref(false);
    const resizedSize = vue.ref(null);
    const resizing = vue.ref(false);
    const sideSize = vue.computed(() => {
      const size = resizedSize.value ?? props2.size ?? "20%";
      if (typeof size === "number") {
        return `${size}px`;
      }
      return size;
    });
    const spaceSize = vue.computed(() => {
      const size = props2.space ?? "16px";
      if (typeof size === "number") {
        return `${size}px`;
      }
      return size;
    });
    const sideWrapStyle = vue.computed(() => {
      const style = {};
      if (props2.vertical) {
        style.height = sideSize.value;
      } else {
        style.width = sideSize.value;
      }
      if (isCollapse.value === true) {
        const m = `calc(${sideSize.value} * -1)`;
        if (props2.vertical) {
          if (sideSize.value.endsWith("px")) {
            if (props2.reverse) {
              style.margin = `0 0 ${m} 0`;
            } else {
              style.margin = `${m} 0 0 0`;
            }
          } else {
            style.height = 0;
          }
        } else {
          if (sideSize.value.endsWith("px") || sideSize.value.endsWith("%")) {
            if (props2.reverse) {
              style.margin = `0 ${m} 0 0`;
            } else {
              style.margin = `0 0 0 ${m}`;
            }
          } else {
            style.width = 0;
          }
        }
      } else {
        if (props2.vertical) {
          if (props2.reverse) {
            style.marginTop = spaceSize.value;
          } else {
            style.marginBottom = spaceSize.value;
          }
        } else {
          if (props2.reverse) {
            style.marginLeft = spaceSize.value;
          } else {
            style.marginRight = spaceSize.value;
          }
        }
      }
      return style;
    });
    const btnOffsetStyle = vue.computed(() => {
      const offset = props2.collapseBtnOffset;
      if (isCollapse.value !== true || offset == null || offset === "") {
        return {};
      }
      const p = typeof offset === "number" ? `${offset}px` : offset;
      return props2.vertical ? props2.reverse ? { marginBottom: p } : { marginTop: p } : props2.reverse ? { marginRight: p } : { marginLeft: p };
    });
    const btnGroupStyle = vue.computed(() => {
      const offset = props2.collapseBtnOffset;
      if (offset == null || offset === "") {
        return {};
      }
      const p = typeof offset === "number" ? `${offset}px` : offset;
      return { gap: `calc(${p} * 2)` };
    });
    const toggleCollapse = (collapse) => {
      const c = collapse === "body" || typeof collapse === "boolean" ? collapse : !isCollapse.value;
      if (isCollapse.value !== c) {
        isCollapse.value = c;
      }
      if (props2.collapse !== isCollapse.value) {
        emit("update:collapse", isCollapse.value);
      }
    };
    const resetSize = () => {
      resizedSize.value = null;
    };
    const getResizedSize = (size) => {
      const el = wrapperRef.value;
      if (!props2.percentage || !el) {
        return `${size}px`;
      }
      const sideSize2 = props2.vertical ? el.offsetHeight : el.offsetWidth;
      return `${size / sideSize2 * 100}%`;
    };
    const getMinSize = () => {
      return !props2.minSize || props2.minSize < 0 ? 0 : props2.minSize;
    };
    const getMaxSize = () => {
      const el = wrapperRef.value;
      if (!el) {
        if (props2.maxSize && props2.maxSize > 1) {
          return props2.maxSize;
        }
        return;
      }
      const size = props2.vertical ? el.offsetHeight : el.offsetWidth;
      if (!props2.maxSize) {
        return size;
      }
      if (props2.maxSize < 0) {
        return size + props2.maxSize;
      } else if (props2.maxSize < 1) {
        return Math.floor(size * props2.maxSize);
      }
      return Math.min(props2.maxSize, size);
    };
    let resizeEventData = null;
    const { handleMousedown, handleTouchstart } = hook.useMoveEvent({
      start: () => {
        const el = sideWrapperRef.value;
        if (!el) {
          resizeEventData = null;
          return;
        }
        resizing.value = true;
        resizeEventData = {
          downW: el.offsetWidth,
          downH: el.offsetHeight,
          min: getMinSize(),
          max: getMaxSize()
        };
        emit(
          "resizeStart",
          props2.vertical ? resizeEventData.downH : resizeEventData.downW
        );
      },
      move: ({ distanceX, distanceY, e }) => {
        if (!resizeEventData) {
          return;
        }
        const dx = distanceX ?? 0;
        const dy = distanceY ?? 0;
        const { downW, downH, min, max } = resizeEventData;
        e.preventDefault();
        const size = props2.vertical ? (props2.reverse ? -dy : dy) + downH : (props2.reverse ? -dx : dx) + downW;
        const rSize = Math.max(size, min);
        resizeEventData.size = max == null ? rSize : Math.min(rSize, max);
        resizedSize.value = getResizedSize(resizeEventData.size);
        emit("resize", resizeEventData.size, resizedSize.value);
      },
      end: () => {
        resizing.value = false;
        const size = resizeEventData?.size;
        resizeEventData = null;
        emit("resizeEnd", size, resizedSize.value);
      },
      touchmoveOptions: { passive: false }
    });
    vue.watch(
      () => props2.size,
      () => {
        resetSize();
      }
    );
    vue.watch(
      () => props2.minSize,
      () => {
        if (resizedSize.value) {
          const min = getMinSize();
          if (resizedSize.value.endsWith("px")) {
            if (Number.parseInt(resizedSize.value) < min) {
              resizedSize.value = getResizedSize(min);
            }
          } else if (resizedSize.value.endsWith("%")) {
            const el = wrapperRef.value;
            if (el) {
              const sideSize2 = props2.vertical ? el.offsetHeight : el.offsetWidth;
              if (Number.parseInt(resizedSize.value) / 100 * sideSize2 < min) {
                resizedSize.value = getResizedSize(min);
              }
            }
          }
        }
      }
    );
    vue.watch([() => props2.maxSize, () => props2.vertical], () => {
      if (resizedSize.value) {
        const max = getMaxSize();
        if (max != null) {
          if (resizedSize.value.endsWith("px")) {
            if (Number.parseInt(resizedSize.value) > max) {
              resizedSize.value = getResizedSize(max);
            }
          } else if (resizedSize.value.endsWith("%")) {
            const el = wrapperRef.value;
            if (el) {
              const sideSize2 = props2.vertical ? el.offsetHeight : el.offsetWidth;
              if (Number.parseInt(resizedSize.value) / 100 * sideSize2 > max) {
                resizedSize.value = getResizedSize(max);
              }
            }
          }
        }
      }
    });
    vue.watch(
      [() => props2.collapse, () => props2.allowCollapse],
      () => {
        if (props2.allowCollapse !== true && props2.allowCollapse !== "both") {
          toggleCollapse(false);
        } else if (props2.allowCollapse !== "both" && props2.collapse === "body") {
          toggleCollapse(false);
        } else {
          toggleCollapse(
            props2.collapse === "body" || props2.collapse === true ? props2.collapse : false
          );
        }
      },
      { immediate: true }
    );
    __expose({
      toggleCollapse,
      resetSize
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "wrapperRef",
        ref: wrapperRef,
        class: vue.normalizeClass(["ele-split-panel", [
          { "is-reverse": _ctx.reverse },
          { "is-vertical": _ctx.vertical },
          { "is-collapse": isCollapse.value === true },
          { "is-maximized": isCollapse.value === "body" },
          { "is-resizing": resizing.value },
          { "is-responsive": vue.unref(isResponsive) },
          { "is-flex-table": _ctx.flexTable && _ctx.flexTable !== "auto" },
          { "is-flex-auto-table": _ctx.flexTable === "auto" }
        ]])
      }, [
        vue.createElementVNode("div", {
          ref_key: "sideWrapperRef",
          ref: sideWrapperRef,
          class: "ele-split-panel-wrap",
          style: vue.normalizeStyle([_ctx.customWrapStyle, sideWrapStyle.value])
        }, [
          vue.createElementVNode("div", {
            class: "ele-split-panel-side",
            style: vue.normalizeStyle(_ctx.customStyle)
          }, [
            _ctx.$slots.sideHeader ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-split-panel-side-header",
              style: vue.normalizeStyle(_ctx.sideHeaderStyle)
            }, [
              vue.renderSlot(_ctx.$slots, "sideHeader")
            ], 4)) : vue.createCommentVNode("", true),
            vue.renderSlot(_ctx.$slots, "default")
          ], 4),
          vue.createElementVNode("div", _hoisted_1, [
            _ctx.resizable ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-split-panel-resize",
              onMousedown: _cache[0] || (_cache[0] = //@ts-ignore
              (...args) => vue.unref(handleMousedown) && vue.unref(handleMousedown)(...args)),
              onTouchstartPassive: _cache[1] || (_cache[1] = //@ts-ignore
              (...args) => vue.unref(handleTouchstart) && vue.unref(handleTouchstart)(...args))
            }, null, 32)) : vue.createCommentVNode("", true),
            _ctx.allowCollapse === "both" ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 1,
              class: "ele-split-panel-collapse-btn-group",
              style: vue.normalizeStyle(btnGroupStyle.value)
            }, [
              vue.createElementVNode("div", {
                style: vue.normalizeStyle(_ctx.collapseStyle),
                class: "ele-split-panel-collapse-btn is-collapse-btn",
                onClick: _cache[2] || (_cache[2] = ($event) => toggleCollapse(isCollapse.value === "body" ? false : true))
              }, [
                vue.renderSlot(_ctx.$slots, "collapse", { collapse: isCollapse.value }, () => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-split-panel-collapse-icon" }, {
                    default: vue.withCtx(() => [
                      _ctx.vertical ? (vue.openBlock(), vue.createBlock(vue.unref(index.ArrowUp), {
                        key: 0,
                        style: { strokeWidth: 5, marginTop: "-1.25px" }
                      })) : (vue.openBlock(), vue.createBlock(vue.unref(index.ArrowLeft), {
                        key: 1,
                        style: { strokeWidth: 5, marginLeft: "-1.25px" }
                      }))
                    ]),
                    _: 1
                  })
                ])
              ], 4),
              vue.createElementVNode("div", {
                style: vue.normalizeStyle(_ctx.collapseStyle),
                class: "ele-split-panel-collapse-btn is-maximized-btn",
                onClick: _cache[3] || (_cache[3] = ($event) => toggleCollapse(isCollapse.value === true ? false : "body"))
              }, [
                vue.renderSlot(_ctx.$slots, "maximized", { collapse: isCollapse.value }, () => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-split-panel-collapse-icon" }, {
                    default: vue.withCtx(() => [
                      _ctx.vertical ? (vue.openBlock(), vue.createBlock(vue.unref(index.ArrowUp), {
                        key: 0,
                        style: { strokeWidth: 5, marginTop: "-1.25px" }
                      })) : (vue.openBlock(), vue.createBlock(vue.unref(index.ArrowLeft), {
                        key: 1,
                        style: { strokeWidth: 5, marginLeft: "-1.25px" }
                      }))
                    ]),
                    _: 1
                  })
                ])
              ], 4)
            ], 4)) : _ctx.allowCollapse === true ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 2,
              style: vue.normalizeStyle([_ctx.collapseStyle, btnOffsetStyle.value]),
              class: "ele-split-panel-collapse-btn",
              onClick: _cache[4] || (_cache[4] = ($event) => toggleCollapse())
            }, [
              vue.renderSlot(_ctx.$slots, "collapse", { collapse: isCollapse.value }, () => [
                vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-split-panel-collapse-icon" }, {
                  default: vue.withCtx(() => [
                    _ctx.vertical ? (vue.openBlock(), vue.createBlock(vue.unref(index.ArrowUp), {
                      key: 0,
                      style: { strokeWidth: 5, marginTop: "-1.25px" }
                    })) : (vue.openBlock(), vue.createBlock(vue.unref(index.ArrowLeft), {
                      key: 1,
                      style: { strokeWidth: 5, marginLeft: "-1.25px" }
                    }))
                  ]),
                  _: 1
                })
              ])
            ], 4)) : vue.createCommentVNode("", true)
          ])
        ], 4),
        vue.createVNode(MainContent, {
          class: "ele-split-panel-body",
          style: vue.normalizeStyle(_ctx.bodyStyle)
        }, {
          default: vue.withCtx(() => [
            _ctx.$slots.bodyHeader ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-split-panel-body-header",
              style: vue.normalizeStyle(_ctx.bodyHeaderStyle)
            }, [
              vue.renderSlot(_ctx.$slots, "bodyHeader")
            ], 4)) : vue.createCommentVNode("", true),
            vue.renderSlot(_ctx.$slots, "body", { collapse: isCollapse.value })
          ]),
          _: 3
        }, 8, ["style"]),
        vue.createElementVNode("div", {
          class: "ele-split-panel-mask",
          onClick: _cache[5] || (_cache[5] = ($event) => toggleCollapse())
        })
      ], 2);
    };
  }
});
module.exports = _sfc_main;
