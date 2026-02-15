"use strict";
const vue = require("vue");
const EleQrCodeSvg = require("../ele-qr-code-svg/index");
const CanvasRender = require("./components/canvas-render");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleQrCode" },
  __name: "index",
  props: props.qrCodeProps,
  emits: props.qrCodeEmits,
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const handleDone = () => {
      emit("done");
    };
    return (_ctx, _cache) => {
      return _ctx.tag === "svg" ? (vue.openBlock(), vue.createBlock(EleQrCodeSvg, {
        key: 0,
        value: _ctx.value,
        size: _ctx.size,
        level: _ctx.level,
        bgColor: _ctx.bgColor,
        fgColor: _ctx.fgColor,
        margin: _ctx.margin,
        imageSettings: _ctx.imageSettings,
        customStyle: _ctx.customStyle,
        onDone: handleDone
      }, null, 8, ["value", "size", "level", "bgColor", "fgColor", "margin", "imageSettings", "customStyle"])) : (vue.openBlock(), vue.createBlock(CanvasRender, {
        key: 1,
        value: _ctx.value,
        size: _ctx.size,
        level: _ctx.level,
        bgColor: _ctx.bgColor,
        fgColor: _ctx.fgColor,
        margin: _ctx.margin,
        imageSettings: _ctx.imageSettings,
        customStyle: _ctx.customStyle,
        tag: _ctx.tag,
        onDone: handleDone
      }, null, 8, ["value", "size", "level", "bgColor", "fgColor", "margin", "imageSettings", "customStyle", "tag"]));
    };
  }
});
module.exports = _sfc_main;
