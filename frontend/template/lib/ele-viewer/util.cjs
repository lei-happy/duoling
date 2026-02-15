"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const util = require("../ele-pro-layout/util");
const SvgRender = require("../ele-qr-code-svg/components/svg-render");
const util$1 = require("../ele-qr-code-svg/util");
function getRotatedBounds(w, h, r) {
  const radians = r * (Math.PI / 180);
  const cosR = Math.cos(radians);
  const sinR = Math.sin(radians);
  const width = Math.abs(w * cosR) + Math.abs(h * sinR);
  const height = Math.abs(w * sinR) + Math.abs(h * cosR);
  return { width, height };
}
function useContentRatio(updateStyle) {
  const state = util.useLayoutState();
  const to = vue.computed(() => state.modalsEl || "body");
  const { svgProps, svgKey, imageId } = util$1.useSvgOption();
  const updateSpinnerStyle = () => {
    updateStyle && updateStyle({
      font: {
        color: "rgba(122, 122, 122, 0.35)",
        fontSize: 16,
        fontWeight: "normal",
        fontFamily: "sans-serif",
        fontStyle: "normal"
      },
      commonStyle: {
        position: "fixed",
        pointerEvents: "none",
        zIndex: 9999
      },
      contents: [svgKey.value]
    });
  };
  vue.onMounted(() => {
    updateSpinnerStyle();
  });
  vue.watch(svgKey, () => {
    updateSpinnerStyle();
  });
  return { LoadingSpinner: SvgRender, slotProps: svgProps, show: imageId, to };
}
exports.getRotatedBounds = getRotatedBounds;
exports.useContentRatio = useContentRatio;
