"use strict";
const vue = require("vue");
const qrcodegen = require("../qrcodegen");
const props = require("../props");
const util = require("../util");
const _hoisted_1 = {
  class: "ele-qr-code",
  style: { display: "inline-flex" }
};
const _hoisted_2 = ["src"];
const _hoisted_3 = ["src"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CanvasRender" },
  __name: "canvas-render",
  props: props.qrCodeProps,
  emits: props.qrCodeEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const imgData = vue.ref("");
    const canvasRef = vue.ref(null);
    const imageRef = vue.ref(null);
    const render = () => {
      const { value, size, level, bgColor, fgColor, margin, imageSettings } = props2;
      const canvas = canvasRef.value;
      if (!canvas) {
        return;
      }
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        return;
      }
      if (!value) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
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
      const image = imageRef.value;
      const haveImageToRender = calculatedImageSettings != null && image != null && image.complete && image.naturalHeight !== 0 && image.naturalWidth !== 0;
      if (haveImageToRender && calculatedImageSettings.excavation != null) {
        cells = util.excavateModules(cells, calculatedImageSettings.excavation);
      }
      const pixelRatio = window.devicePixelRatio || 1;
      canvas.height = canvas.width = size * pixelRatio;
      const scale = size / numCells * pixelRatio;
      ctx.scale(scale, scale);
      ctx.fillStyle = bgColor;
      ctx.fillRect(0, 0, numCells, numCells);
      ctx.fillStyle = fgColor;
      if (util.SUPPORTS_PATH2D) {
        ctx.fill(new Path2D(util.generatePath(cells, margin)));
      } else {
        cells.forEach(function(row, rdx) {
          row.forEach(function(cell, cdx) {
            if (cell) {
              ctx.fillRect(cdx + margin, rdx + margin, 1, 1);
            }
          });
        });
      }
      if (haveImageToRender) {
        ctx.drawImage(
          image,
          calculatedImageSettings.x + margin,
          calculatedImageSettings.y + margin,
          calculatedImageSettings.w,
          calculatedImageSettings.h
        );
      }
      if (props2.tag === "img") {
        imgData.value = canvas.toDataURL();
      }
      emit("done");
    };
    vue.watch(
      [
        () => props2.value,
        () => props2.size,
        () => props2.level,
        () => props2.margin,
        () => props2.bgColor,
        () => props2.fgColor,
        () => props2.tag
      ],
      () => {
        render();
      }
    );
    vue.watch(
      () => props2.imageSettings,
      () => {
        render();
      },
      { deep: true }
    );
    vue.onMounted(() => {
      render();
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        _ctx.tag === "img" ? (vue.openBlock(), vue.createElementBlock("img", {
          key: 0,
          src: imgData.value,
          style: vue.normalizeStyle([{ width: _ctx.size + "px", height: _ctx.size + "px" }, _ctx.customStyle || {}])
        }, null, 12, _hoisted_2)) : vue.createCommentVNode("", true),
        vue.createElementVNode("canvas", {
          ref_key: "canvasRef",
          ref: canvasRef,
          style: vue.normalizeStyle([
            {
              width: _ctx.size + "px",
              height: _ctx.size + "px",
              display: _ctx.tag === "img" ? "none" : void 0
            },
            _ctx.customStyle || {}
          ])
        }, null, 4),
        _ctx.imageSettings && _ctx.imageSettings.src ? (vue.openBlock(), vue.createElementBlock("img", {
          key: 1,
          ref_key: "imageRef",
          ref: imageRef,
          src: _ctx.imageSettings.src,
          crossorigin: "anonymous",
          referrerpolicy: "no-referrer",
          style: { display: "none" },
          onLoad: render
        }, null, 40, _hoisted_3)) : vue.createCommentVNode("", true)
      ]);
    };
  }
});
module.exports = _sfc_main;
