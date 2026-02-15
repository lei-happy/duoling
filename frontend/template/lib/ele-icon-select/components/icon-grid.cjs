"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const EleTooltip = require("../../ele-tooltip/index");
const _hoisted_1 = ["title", "onClick", "onMouseover"];
const _hoisted_2 = {
  key: 0,
  class: "ele-icon-select-item-name"
};
const _hoisted_3 = {
  key: 0,
  class: "ele-icon-select-empty"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "IconGrid" },
  __name: "icon-grid",
  props: {
    /** 选中的图标 */
    icon: String,
    /** 图标数据 */
    data: {
      type: Array,
      required: true
    },
    /** 空组件属性 */
    emptyProps: Object,
    /** 是否显示提示 */
    tooltip: [Boolean, String],
    /** 提示属性 */
    tooltipProps: Object,
    /** 气泡是否展开 */
    popperVisible: Boolean,
    /** 网格样式 */
    gridStyle: Object,
    /** 图标样式 */
    itemStyle: Object,
    /** 下拉组件类型 */
    popperType: String
  },
  emits: {
    select: (_icon) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const tooltipVisible = vue.ref(false);
    const tooltipContent = vue.ref("");
    const virtualRef = vue.ref();
    const updateTooltipVisible = (visible) => {
      tooltipVisible.value = visible;
    };
    const hideTooltip = () => {
      updateTooltipVisible(false);
    };
    const handleItemHover = (icon, e) => {
      if (props.tooltip === true && (props.popperVisible || props.popperType === "default") && icon) {
        virtualRef.value = e.currentTarget;
        tooltipContent.value = icon;
        tooltipVisible.value = true;
      }
    };
    const handleItemClick = (icon) => {
      emit("select", icon);
    };
    vue.watch(
      () => props.popperVisible,
      (visible) => {
        if (!visible) {
          hideTooltip();
        }
      }
    );
    __expose({
      hideTooltip
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElScrollbar), { class: "ele-icon-select-body" }, {
        default: vue.withCtx(() => [
          vue.createElementVNode("div", {
            class: vue.normalizeClass(["ele-icon-select-grid", { "is-loose": __props.tooltip === "static" }]),
            style: vue.normalizeStyle(__props.gridStyle)
          }, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.data, (d, i) => {
              return vue.openBlock(), vue.createElementBlock("div", {
                key: `${i}-${d}`,
                class: vue.normalizeClass(["ele-icon-select-item", { "is-active": __props.icon && d === __props.icon }]),
                title: !__props.tooltip || __props.tooltip === "static" ? d : void 0,
                style: vue.normalizeStyle(__props.itemStyle),
                onClick: ($event) => handleItemClick(d),
                onMouseover: (e) => handleItemHover(d, e)
              }, [
                vue.renderSlot(_ctx.$slots, "icon", {
                  icon: d,
                  prefix: false
                }),
                __props.tooltip === "static" ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, vue.toDisplayString(d), 1)) : vue.createCommentVNode("", true)
              ], 46, _hoisted_1);
            }), 128))
          ], 6),
          !__props.data || !__props.data.length ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_3, [
            vue.createVNode(vue.unref(elementPlus.ElEmpty), vue.mergeProps({ imageSize: 60 }, __props.emptyProps || {}), null, 16)
          ])) : vue.createCommentVNode("", true),
          __props.tooltip === true ? (vue.openBlock(), vue.createBlock(EleTooltip, vue.mergeProps({
            key: 1,
            placement: "top",
            offset: 6,
            teleported: __props.popperType !== "popper"
          }, __props.tooltipProps || {}, {
            visible: tooltipVisible.value,
            content: tooltipContent.value,
            virtualRef: virtualRef.value,
            virtualTriggering: true,
            "onUpdate:visible": updateTooltipVisible
          }), null, 16, ["teleported", "visible", "content", "virtualRef"])) : vue.createCommentVNode("", true)
        ]),
        _: 3
      });
    };
  }
});
module.exports = _sfc_main;
