"use strict";
const vue = require("vue");
const hook = require("../utils/hook");
const util = require("./util");
const props = require("./props");
const _hoisted_1 = ["src"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleViewer" },
  __name: "index",
  props: props.viewerProps,
  emits: props.viewerEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const viewerRef = vue.ref(null);
    const bodyRef = vue.ref(null);
    const contentRef = vue.ref(null);
    const viewerMoving = vue.ref(false);
    const viewerTranslateX = vue.ref(0);
    const viewerTranslateY = vue.ref(0);
    const viewerScale = vue.ref(100);
    const viewerFlipX = vue.ref(false);
    const viewerFlipY = vue.ref(false);
    const viewerRotate = vue.ref(0);
    const imageTransform = vue.computed(() => {
      const sx = viewerFlipX.value ? -1 : 1;
      const sy = viewerFlipY.value ? -1 : 1;
      return `scaleX(${sx}) scaleY(${sy}) rotate(${viewerRotate.value}deg)`;
    });
    const scaleReverse = vue.computed(() => {
      return (100 / viewerScale.value).toFixed(6);
    });
    const imageTransformReverse = vue.computed(() => {
      const sx = viewerFlipX.value ? -1 : 1;
      const sy = viewerFlipY.value ? -1 : 1;
      return `scaleX(${sx}) scaleY(${sy}) rotate(${360 - viewerRotate.value}deg)`;
    });
    const handleClick = (e) => {
      emit("contentClick", e);
    };
    const handleContextmenu = (e) => {
      emit("contentContextmenu", e);
    };
    const handleImgLoad = () => {
      autoIntoView();
    };
    const getZoomStep = () => {
      return props2.zoomStep;
    };
    const zoomIn = () => {
      if (viewerScale.value >= props2.zoomMax) {
        return;
      }
      viewerScale.value += getZoomStep();
    };
    const zoomOut = () => {
      if (viewerScale.value <= props2.zoomMin) {
        return;
      }
      viewerScale.value -= getZoomStep();
    };
    const flipX = () => {
      viewerFlipX.value = !viewerFlipX.value;
    };
    const flipY = () => {
      viewerFlipY.value = !viewerFlipY.value;
    };
    const rotateLeft = () => {
      if (viewerRotate.value === 0) {
        viewerRotate.value = 360 - props2.rotateStep;
        return;
      }
      if (viewerRotate.value <= props2.rotateStep) {
        viewerRotate.value = 0;
        return;
      }
      viewerRotate.value -= props2.rotateStep;
    };
    const rotateRight = () => {
      if (viewerRotate.value >= 360 - props2.rotateStep) {
        viewerRotate.value = 0;
        return;
      }
      viewerRotate.value += props2.rotateStep;
    };
    const setTranslateX = (xValue) => {
      viewerTranslateX.value = xValue;
    };
    const setTranslateY = (yValue) => {
      viewerTranslateY.value = yValue;
    };
    const autoIntoView = () => {
      const pEl = viewerRef.value;
      const pw = pEl?.offsetWidth || 0;
      const ph = pEl?.offsetHeight || 0;
      const el = bodyRef.value;
      const w = el?.offsetWidth || 0;
      const h = el?.offsetHeight || 0;
      viewerTranslateX.value = Math.floor((pw - w) / 2);
      viewerTranslateY.value = Math.floor((ph - h) / 2);
      const { width, height } = util.getRotatedBounds(w, h, viewerRotate.value);
      viewerScale.value = Math.min(pw / width * 100, ph / height * 100);
    };
    const autoIntoViewWidth = () => {
      const pEl = viewerRef.value;
      const pw = pEl?.offsetWidth || 0;
      const ph = pEl?.offsetHeight || 0;
      const el = bodyRef.value;
      const w = el?.offsetWidth || 0;
      const h = el?.offsetHeight || 0;
      viewerScale.value = pw / w * 100;
      const sh = h * (viewerScale.value / 100);
      viewerTranslateX.value = Math.floor((pw - w) / 2);
      if (sh < ph) {
        viewerTranslateY.value = Math.floor((ph - h) / 2);
      } else {
        viewerTranslateY.value = Math.floor((sh - h) / 2);
      }
    };
    const autoIntoViewHeight = () => {
      const pEl = viewerRef.value;
      const pw = pEl?.offsetWidth || 0;
      const ph = pEl?.offsetHeight || 0;
      const el = bodyRef.value;
      const w = el?.offsetWidth || 0;
      const h = el?.offsetHeight || 0;
      viewerScale.value = ph / h * 100;
      const sw = w * (viewerScale.value / 100);
      if (sw < pw) {
        viewerTranslateX.value = Math.floor((pw - w) / 2);
      } else {
        viewerTranslateX.value = Math.floor((sw - w) / 2);
      }
      viewerTranslateY.value = Math.floor((ph - h) / 2);
    };
    const reset = () => {
      viewerFlipX.value = false;
      viewerFlipY.value = false;
      viewerRotate.value = 0;
      autoIntoView();
    };
    let startX = null;
    let startY = null;
    const { handleMousedown, handleTouchstart } = hook.useMoveEvent({
      start: () => {
        viewerMoving.value = true;
        startX = viewerTranslateX.value;
        startY = viewerTranslateY.value;
      },
      move: ({ distanceX, distanceY, e }) => {
        if (startX == null || startY == null || distanceX == null || distanceY == null || !contentStyle.show.value) {
          return;
        }
        e.preventDefault();
        e.stopPropagation();
        viewerTranslateX.value = Math.floor(distanceX + startX);
        viewerTranslateY.value = Math.floor(distanceY + startY);
      },
      end: () => {
        startX = null;
        startY = null;
        viewerMoving.value = false;
      },
      touchmoveOptions: { passive: false }
    });
    const { bindMousewheel, unbindMousewheel } = hook.useMousewheel(
      ({ e, direction }) => {
        e.preventDefault();
        e.stopPropagation();
        if (direction === "up") {
          zoomIn();
          return;
        }
        zoomOut();
      }
    );
    const contentStyle = util.useContentRatio();
    vue.onMounted(() => {
      viewerRef.value && bindMousewheel(viewerRef.value);
      autoIntoView();
    });
    vue.onBeforeUnmount(() => {
      viewerRef.value && unbindMousewheel(viewerRef.value);
    });
    __expose({
      viewerMoving,
      viewerTranslateX,
      viewerTranslateY,
      viewerScale,
      viewerFlipX,
      viewerFlipY,
      viewerRotate,
      zoomIn,
      zoomOut,
      flipX,
      flipY,
      rotateLeft,
      rotateRight,
      setTranslateX,
      setTranslateY,
      autoIntoView,
      autoIntoViewWidth,
      autoIntoViewHeight,
      reset
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "viewerRef",
        ref: viewerRef,
        class: "ele-viewer"
      }, [
        vue.createElementVNode("div", {
          ref_key: "bodyRef",
          ref: bodyRef,
          class: "ele-viewer-body",
          style: vue.normalizeStyle({
            transform: `translate(${viewerTranslateX.value}px, ${viewerTranslateY.value}px)`
          })
        }, [
          vue.createElementVNode("div", {
            class: "ele-viewer-main",
            style: vue.normalizeStyle({ transform: `scale(${(viewerScale.value / 100).toFixed(6)})` })
          }, [
            vue.createElementVNode("div", {
              ref_key: "contentRef",
              ref: contentRef,
              class: vue.normalizeClass(["ele-viewer-content", { "is-moving": viewerMoving.value }]),
              style: vue.normalizeStyle([vue.unref(contentStyle) || {}, { transform: imageTransform.value }]),
              onMousedown: _cache[0] || (_cache[0] = //@ts-ignore
              (...args) => vue.unref(handleMousedown) && vue.unref(handleMousedown)(...args)),
              onTouchstartPassive: _cache[1] || (_cache[1] = //@ts-ignore
              (...args) => vue.unref(handleTouchstart) && vue.unref(handleTouchstart)(...args)),
              onClick: handleClick,
              onContextmenu: handleContextmenu
            }, [
              _ctx.src ? (vue.openBlock(), vue.createElementBlock("img", {
                key: 0,
                src: _ctx.src,
                class: "ele-viewer-image",
                style: vue.normalizeStyle(_ctx.imageStyle),
                onLoad: handleImgLoad
              }, null, 44, _hoisted_1)) : (vue.openBlock(), vue.createElementBlock("div", {
                key: 1,
                class: "ele-viewer-image",
                style: vue.normalizeStyle(_ctx.imageStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "default")
              ], 4)),
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.markers, (marker) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: marker.key,
                  style: vue.normalizeStyle({
                    left: (marker.x || 0) + "px",
                    top: (marker.y || 0) + "px",
                    transform: marker.fixed ? `scale(${scaleReverse.value})` : void 0
                  }),
                  class: "ele-viewer-marker"
                }, [
                  vue.createElementVNode("div", {
                    class: "ele-viewer-marker-content",
                    style: vue.normalizeStyle({
                      transform: marker.fixed ? imageTransformReverse.value : void 0
                    })
                  }, [
                    vue.renderSlot(_ctx.$slots, "markerItem", { item: marker })
                  ], 4)
                ], 4);
              }), 128))
            ], 38)
          ], 4)
        ], 4)
      ], 512);
    };
  }
});
module.exports = _sfc_main;
