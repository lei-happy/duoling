"use strict";
const vue = require("vue");
const common = require("../utils/common");
const EleTooltip = require("../ele-tooltip/index");
const EleText = require("../ele-text/index");
const props$1 = require("../ele-text/props");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleEllipsis" },
  __name: "index",
  props: props.ellipsisProps,
  setup(__props, { expose: __expose }) {
    const props2 = __props;
    const textRef = vue.ref(null);
    const virtualRef = vue.ref();
    const text = vue.ref("");
    const title = vue.computed(() => {
      if (!props2.tooltip || typeof props2.tooltip !== "object" || props2.tooltip.original !== true) {
        return;
      }
      return text.value;
    });
    const tooltipProps = vue.computed(() => {
      const isObj = props2.tooltip && props2.tooltip !== true;
      const opt = isObj ? { ...props2.tooltip } : {};
      opt.content = text.value;
      opt.virtualRef = virtualRef.value;
      opt.virtualTriggering = true;
      return common.omit(opt, ["original"]);
    });
    const multiLine = vue.computed(() => {
      return !!(props2.maxLine && props2.maxLine > 1);
    });
    const textProps = vue.computed(() => {
      return Object.assign({ title: title.value }, common.pick(props2, props$1.textPropKeys));
    });
    const rootStyle = vue.computed(() => {
      const style = {};
      const { lineHeight, maxLine } = props2;
      if (lineHeight != null) {
        const h = typeof lineHeight === "number" ? `${lineHeight}px` : lineHeight;
        style.lineHeight = h;
        if (multiLine.value) {
          style.height = `calc(${h} * ${maxLine})`;
        }
      }
      if (multiLine.value) {
        style["-webkit-line-clamp"] = maxLine;
      }
      return style;
    });
    const handleHover = (e) => {
      if (!props2.tooltip) {
        virtualRef.value = void 0;
        return;
      }
      const target = e.currentTarget;
      if (typeof props2.tooltip === "object" && props2.tooltip.content) {
        if (text.value !== props2.tooltip.content) {
          text.value = props2.tooltip.content;
        }
      } else {
        if (target) {
          const temp = common.contentIsEllipsis(target) ? target.innerText : "";
          if (text.value !== temp) {
            text.value = temp;
          }
        }
      }
      if (text.value && (props2.tooltip === true || !props2.tooltip.original)) {
        if (virtualRef.value !== target) {
          virtualRef.value = target;
        }
      } else {
        virtualRef.value = void 0;
      }
    };
    __expose({
      textRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleText, vue.mergeProps(textProps.value, {
        ref_key: "textRef",
        ref: textRef,
        style: rootStyle.value,
        class: ["ele-ellipsis", { "is-multi-line": multiLine.value }],
        onMouseover: handleHover
      }), {
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "default"),
          virtualRef.value ? (vue.openBlock(), vue.createBlock(EleTooltip, vue.normalizeProps(vue.mergeProps({ key: 0 }, tooltipProps.value)), null, 16)) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 16, ["style", "class"]);
    };
  }
});
module.exports = _sfc_main;
