"use strict";
const vue = require("vue");
const qrcodegen = require("../ele-qr-code/qrcodegen");
const util = require("../ele-qr-code/util");
const props = require("../ele-qr-code/props");
const _hoisted_1 = {
  class: "ele-qr-code",
  style: { display: "inline-flex" }
};
const _hoisted_2 = ["height", "width", "viewBox"];
const _hoisted_3 = ["fill", "d"];
const _hoisted_4 = ["fill", "d"];
const _hoisted_5 = ["xlink:href", "height", "width", "x", "y"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleQrCodeSvg" },
  __name: "index",
  props: props.qrCodeProps,
  emits: props.qrCodeEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const viewBox = vue.ref("");
    const path = vue.ref("");
    const fgPath = vue.ref("");
    const imageHeight = vue.ref(0);
    const imageWidth = vue.ref(0);
    const imageX = vue.ref(0);
    const imageY = vue.ref(0);
    const render = () => {
      const { value, size, level, margin, imageSettings } = props2;
      if (!value) {
        viewBox.value = "";
        return;
      }
      let cells = qrcodegen.QrCode.encodeText(
        value,
        util.ERROR_LEVEL_MAP[level]
      ).getModules();
      const numCells = cells.length + margin * 2;
      const calculatedImageSettings = util.getImageSettings(
        imageSettings,
        size,
        margin,
        cells
      );
      if (imageSettings != null && calculatedImageSettings != null) {
        if (calculatedImageSettings.excavation != null) {
          cells = util.excavateModules(cells, calculatedImageSettings.excavation);
        }
        imageHeight.value = calculatedImageSettings.h;
        imageWidth.value = calculatedImageSettings.w;
        imageX.value = calculatedImageSettings.x + margin;
        imageY.value = calculatedImageSettings.y + margin;
      }
      viewBox.value = `0 0 ${numCells} ${numCells}`;
      path.value = `M0,0 h${numCells}v${numCells}H0z`;
      fgPath.value = util.generatePath(cells, margin);
      emit("done");
    };
    vue.watch(
      [
        () => props2.value,
        () => props2.size,
        () => props2.level,
        () => props2.margin
      ],
      () => {
        render();
      },
      { immediate: true }
    );
    vue.watch(
      () => props2.imageSettings,
      () => {
        render();
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        viewBox.value ? (vue.openBlock(), vue.createElementBlock("svg", {
          key: 0,
          shapeRendering: "crispEdges",
          height: _ctx.size,
          width: _ctx.size,
          viewBox: viewBox.value,
          style: vue.normalizeStyle(_ctx.customStyle)
        }, [
          vue.createElementVNode("path", {
            fill: _ctx.bgColor,
            d: path.value
          }, null, 8, _hoisted_3),
          vue.createElementVNode("path", {
            fill: _ctx.fgColor,
            d: fgPath.value
          }, null, 8, _hoisted_4),
          _ctx.imageSettings && _ctx.imageSettings.src ? (vue.openBlock(), vue.createElementBlock("image", {
            key: 0,
            "xlink:href": _ctx.imageSettings.src,
            height: imageHeight.value,
            width: imageWidth.value,
            x: imageX.value,
            y: imageY.value,
            preserveAspectRatio: "none"
          }, null, 8, _hoisted_5)) : vue.createCommentVNode("", true)
        ], 12, _hoisted_2)) : vue.createCommentVNode("", true)
      ]);
    };
  }
});
module.exports = _sfc_main;
