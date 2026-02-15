"use strict";
const vue = require("vue");
const index = require("../../../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{
    components: {
      ArrowUp: index.ArrowUp,
      ArrowDown: index.ArrowDown,
      ArrowRight: index.ArrowRight,
      ArrowLeft: index.ArrowLeft,
      CheckOutlined: index.CheckOutlined,
      CalendarOutlined: index.CalendarOutlined,
      PlusOutlined: index.PlusOutlined,
      StarFilled: index.StarFilled,
      ClockCircleOutlined: index.ClockCircleOutlined,
      EnvironmentOutlined: index.EnvironmentOutlined,
      CheckCircleFilled: index.CheckCircleFilled,
      StepForwardFilled: index.StepForwardFilled,
      ExclamationCircleFilled: index.ExclamationCircleFilled,
      UserOutlined: index.UserOutlined,
      CloseOutlined: index.CloseOutlined
    }
  },
  __name: "svg-icon",
  props: {
    name: {},
    iconStyle: {},
    size: {},
    color: {}
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass([
          {
            "ele-icon-color-primary": __props.color !== "secondary" && __props.color !== "lighter" && __props.color !== "base" && __props.color !== "placeholder" && __props.color !== "light" && __props.color !== "primary5" && __props.color !== "success"
          },
          { "ele-icon-color-secondary": __props.color === "secondary" },
          { "ele-icon-color-lighter": __props.color === "lighter" },
          { "ele-icon-color-base": __props.color === "base" },
          { "ele-icon-color-placeholder": __props.color === "placeholder" },
          { "ele-icon-color-light": __props.color === "light" },
          { "ele-icon-color-primary5": __props.color === "primary5" },
          { "ele-icon-color-success": __props.color === "success" }
        ]),
        style: vue.normalizeStyle({
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: __props.size === "sm" ? "12px" : "14px"
        })
      }, [
        vue.renderSlot(_ctx.$slots, "default", {}, () => [
          (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.name), {
            width: "1em",
            height: "1em",
            style: vue.normalizeStyle(__props.iconStyle)
          }, null, 8, ["style"]))
        ])
      ], 6);
    };
  }
});
module.exports = _sfc_main;
