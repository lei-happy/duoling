"use strict";
const vue = require("vue");
const common = require("../utils/common");
const util$1 = require("../ele-qr-code-svg/util");
const SvgRender = require("../ele-qr-code-svg/components/svg-render");
const util = require("./util");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleWatermark" },
  __name: "index",
  props: props.watermarkProps,
  setup(__props) {
    const props2 = __props;
    const wrapperRef = vue.ref(null);
    const imageRef = vue.ref(null);
    const markCommonStyle = vue.computed(() => {
      const position = props2.fixed ? "fixed" : "absolute";
      const width = props2.fixed ? "100vw" : "100%";
      const height = props2.fixed ? "100vh" : "100%";
      return {
        position: `${position} !important`,
        top: "0 !important",
        left: "0 !important",
        right: "0 !important",
        bottom: "0 !important",
        width: `${width} !important`,
        height: `${height} !important`,
        zIndex: `${props2.zIndex ?? 2147483647} !important`,
        pointerEvents: "none !important",
        ...props2.customStyle || {}
      };
    });
    const isDeactivated = vue.ref(false);
    const svgMarkOption = vue.ref();
    const imageConfig = vue.inject(util.svgContents, null);
    const markWrapperHeight = vue.computed(() => {
      if (props2.wrapHeight != null && typeof props2.wrapHeight === "number") {
        return `${props2.wrapHeight}px`;
      }
      return props2.wrapHeight;
    });
    const markWrapperStyle = vue.computed(() => {
      const styles = [];
      if (markWrapperHeight.value) {
        styles.push({ height: markWrapperHeight.value });
      }
      if (props2.wrapPosition && !props2.fixed) {
        styles.push({ position: "relative" });
      }
      return styles;
    });
    const markId = vue.computed(() => imageConfig ? !imageConfig.id : 1);
    const getImageStyleOption = () => {
      if (!markDisabled.value) {
        svgMarkOption.value = void 0;
        return;
      }
      const defaultWidth = 120;
      const defaultHeight = 64;
      const gapX = props2.gap?.[0] ?? 100;
      const gapY = props2.gap?.[1] ?? 100;
      const option = {
        rotate: props2.rotate ?? -22,
        lineGap: props2.lineGap ?? 3,
        font: {
          color: "rgba(122, 122, 122, 0.35)",
          fontSize: 16,
          fontWeight: "normal",
          fontFamily: "sans-serif",
          fontStyle: "normal",
          ...props2.font || {}
        },
        contents: common.normalizeStringArray(
          props2.content,
          [imageConfig && !imageConfig.id, "el", "NDSP"],
          observeText
        ),
        image: props2.image,
        width: props2.width,
        height: props2.height,
        gapX,
        gapY,
        commonStyle: markCommonStyle.value
      };
      if (props2.svgRender) {
        svgMarkOption.value = {
          ...option,
          width: option.width ?? defaultWidth,
          height: option.height ?? defaultHeight,
          offsetX: props2.offset?.[0] ?? gapX / 2,
          offsetY: props2.offset?.[1] ?? gapY / 2
        };
        return;
      }
      return {
        ...option,
        defaultWidth,
        defaultHeight,
        offsetX: props2.offset?.[0] ?? 0,
        offsetY: props2.offset?.[1] ?? 0
      };
    };
    const { imageId, imageStyleId, imageStyle, observeText, updateImageStyle } = util$1.useMutation({
      getWrapperEl: () => wrapperRef.value,
      getImageEl: () => imageRef.value,
      getImageStyleOption
    });
    const markTeleport = vue.computed(() => isDeactivated.value || !props2.fixed);
    const markDisabled = vue.computed(() => !props2.disabled || markId.value);
    vue.watch(
      [
        () => props2.offset,
        () => props2.width,
        () => props2.height,
        () => props2.gap,
        () => props2.font,
        () => props2.content,
        () => props2.rotate,
        () => props2.image,
        () => props2.lineGap,
        () => props2.svgRender,
        markCommonStyle,
        markDisabled
      ],
      () => {
        updateImageStyle();
      },
      { deep: true }
    );
    vue.onActivated(() => {
      isDeactivated.value = false;
    });
    vue.onDeactivated(() => {
      isDeactivated.value = true;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "wrapperRef",
        ref: wrapperRef,
        key: vue.unref(imageId),
        style: vue.normalizeStyle(markWrapperStyle.value)
      }, [
        vue.renderSlot(_ctx.$slots, "default"),
        !_ctx.svgRender && markDisabled.value ? (vue.openBlock(), vue.createElementBlock("div", {
          ref_key: "imageRef",
          ref: imageRef,
          key: vue.unref(imageStyleId),
          style: vue.normalizeStyle(vue.unref(imageStyle))
        }, null, 4)) : svgMarkOption.value && markDisabled.value ? (vue.openBlock(), vue.createBlock(vue.Teleport, {
          key: 1,
          to: "body",
          disabled: markTeleport.value
        }, [
          vue.createVNode(SvgRender, vue.normalizeProps(vue.guardReactiveProps(svgMarkOption.value)), null, 16)
        ], 8, ["disabled"])) : vue.createCommentVNode("", true)
      ], 4);
    };
  }
});
module.exports = _sfc_main;
