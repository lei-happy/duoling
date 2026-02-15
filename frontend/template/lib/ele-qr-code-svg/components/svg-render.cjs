"use strict";
const vue = require("vue");
const common = require("../../utils/common");
const util = require("../util");
const _hoisted_1 = ["id", "width", "height"];
const _hoisted_2 = ["transform"];
const _hoisted_3 = ["href", "width", "height", "x", "y"];
const _hoisted_4 = ["transform"];
const _hoisted_5 = ["href", "width", "height", "x", "y"];
const _hoisted_6 = ["id", "width", "height"];
const _hoisted_7 = ["transform"];
const _hoisted_8 = ["x", "y", "fill", "font-size", "font-weight", "font-family", "font-style"];
const _hoisted_9 = ["transform"];
const _hoisted_10 = ["x", "y", "fill", "font-size", "font-weight", "font-family", "font-style"];
const _hoisted_11 = ["fill", "transform"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MarkSvg" },
  __name: "svg-render",
  props: {
    /** 宽度 */
    width: {
      type: Number,
      default: 236
    },
    /** 高度 */
    height: {
      type: Number,
      default: 74
    },
    /** 旋转角度 */
    rotate: {
      type: Number,
      default: -22
    },
    /** 水平间距 */
    gapX: {
      type: Number,
      default: 100
    },
    /** 垂直间距 */
    gapY: {
      type: Number,
      default: 100
    },
    /** 多行文字的行间距 */
    lineGap: {
      type: Number,
      default: 3
    },
    /** 文字样式 */
    font: {
      type: Object,
      required: true
    },
    /** 文字内容 */
    contents: {
      type: Array,
      required: true
    },
    /** 图片源 */
    image: String,
    /** 水平偏移量 */
    offsetX: {
      type: Number,
      default: 50
    },
    /** 垂直偏移量 */
    offsetY: {
      type: Number,
      default: 50
    },
    /** 公共样式 */
    commonStyle: Object
  },
  setup(__props) {
    const props = __props;
    const svgId = vue.useId();
    const svgStyle = vue.computed(() => common.joinStyle(props.commonStyle));
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("svg", {
        style: vue.normalizeStyle(svgStyle.value)
      }, [
        vue.createElementVNode("defs", null, [
          __props.image ? (vue.openBlock(), vue.createElementBlock("pattern", {
            key: 0,
            id: `imgPattern-${vue.unref(svgId)}`,
            patternUnits: "userSpaceOnUse",
            width: (__props.width + __props.gapX) * vue.unref(util.MARK_SIZE),
            height: (__props.height + __props.gapY) * vue.unref(util.MARK_SIZE)
          }, [
            vue.createElementVNode("g", {
              transform: `rotate(${__props.rotate}, ${(__props.width + __props.gapX) / 2}, ${(__props.height + __props.gapY) / 2})`
            }, [
              vue.createElementVNode("image", {
                href: __props.image,
                width: __props.width,
                height: __props.height,
                x: __props.gapX / 2,
                y: __props.gapY / 2
              }, null, 8, _hoisted_3)
            ], 8, _hoisted_2),
            vue.unref(util.MARK_SIZE) > 1 ? (vue.openBlock(), vue.createElementBlock("g", {
              key: 0,
              transform: `rotate(${__props.rotate}, ${(__props.width + __props.gapX) / 2 + __props.width + __props.gapX}, ${(__props.height + __props.gapY) / 2 + __props.height + __props.gapY})`
            }, [
              vue.createElementVNode("image", {
                href: __props.image,
                width: __props.width,
                height: __props.height,
                x: __props.gapX / 2 + __props.width + __props.gapX,
                y: __props.gapY / 2 + __props.height + __props.gapY
              }, null, 8, _hoisted_5)
            ], 8, _hoisted_4)) : vue.createCommentVNode("", true)
          ], 8, _hoisted_1)) : (vue.openBlock(), vue.createElementBlock("pattern", {
            key: 1,
            id: `textPattern-${vue.unref(svgId)}`,
            patternUnits: "userSpaceOnUse",
            width: (__props.width + __props.gapX) * vue.unref(util.MARK_SIZE),
            height: (__props.height + __props.gapY) * vue.unref(util.MARK_SIZE)
          }, [
            vue.createElementVNode("g", {
              transform: `rotate(${__props.rotate}, ${(__props.width + __props.gapX) / 2}, ${(__props.height + __props.gapY) / 2})`
            }, [
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.contents, (text, index) => {
                return vue.openBlock(), vue.createElementBlock("text", {
                  key: index,
                  x: (__props.width + __props.gapX) / 2,
                  y: __props.gapY / 2 + index * (__props.font.fontSize + __props.lineGap),
                  fill: __props.font.color,
                  "font-size": __props.font.fontSize,
                  "font-weight": __props.font.fontWeight,
                  "font-family": __props.font.fontFamily,
                  "font-style": __props.font.fontStyle,
                  "text-anchor": "middle",
                  "alignment-baseline": "hanging",
                  "vector-effect": "non-scaling-stroke"
                }, vue.toDisplayString(text), 9, _hoisted_8);
              }), 128))
            ], 8, _hoisted_7),
            vue.unref(util.MARK_SIZE) > 1 ? (vue.openBlock(), vue.createElementBlock("g", {
              key: 0,
              transform: `rotate(${__props.rotate}, ${(__props.width + __props.gapX) / 2 + __props.width + __props.gapX}, ${(__props.height + __props.gapY) / 2 + __props.height + __props.gapY})`
            }, [
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.contents, (text, index) => {
                return vue.openBlock(), vue.createElementBlock("text", {
                  key: index,
                  x: (__props.width + __props.gapX) / 2 + __props.width + __props.gapX,
                  y: __props.gapY / 2 + index * (__props.font.fontSize + __props.lineGap) + __props.height + __props.gapY,
                  fill: __props.font.color,
                  "font-size": __props.font.fontSize,
                  "font-weight": __props.font.fontWeight,
                  "font-family": __props.font.fontFamily,
                  "font-style": __props.font.fontStyle,
                  "text-anchor": "middle",
                  "alignment-baseline": "hanging",
                  "vector-effect": "non-scaling-stroke"
                }, vue.toDisplayString(text), 9, _hoisted_10);
              }), 128))
            ], 8, _hoisted_9)) : vue.createCommentVNode("", true)
          ], 8, _hoisted_6))
        ]),
        vue.createElementVNode("rect", {
          width: "100%",
          height: "100%",
          fill: `url(#${__props.image ? "img" : "text"}Pattern-${vue.unref(svgId)})`,
          transform: `translate(${__props.offsetX - __props.gapX / 2}, ${__props.offsetY - __props.gapY / 2})`
        }, null, 8, _hoisted_11)
      ], 4);
    };
  }
});
module.exports = _sfc_main;
