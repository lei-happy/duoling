"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const EleTooltip = require("../../ele-tooltip/index");
const props$1 = require("../../ele-tooltip/props");
const DropdownMenus = require("./dropdown-menus");
const props = require("../props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ProDropdown" },
  __name: "pro-dropdown",
  props: {
    ...props.dropdownProps,
    /** 当前选中菜单项 */
    selected: Object
  },
  emits: props.dropdownEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const tooltipRef = vue.ref(null);
    const tooltipProps = vue.computed(() => {
      const options = common.pick(props2, props$1.tooltipPropKeys);
      options.showAfter = props2.trigger === "hover" ? props2.showTimeout : 0;
      options.hideAfter = props2.trigger === "hover" ? props2.hideTimeout : 0;
      options.gpuAcceleration = props2.transition === "el-fade-in-linear";
      const classes = ["ele-dropdown"];
      if (props2.preventContextmenu) {
        classes.push("is-prevent-event");
      }
      if (typeof props2.popperClass === "string" && props2.popperClass) {
        classes.push(props2.popperClass);
      }
      options.popperClass = classes.join(" ");
      options.isPopover = true;
      return options;
    });
    const hasSubMenu = vue.computed(
      () => !!(props2.items && props2.items.some((d) => !!d.children?.length))
    );
    const hidePopper = () => {
      tooltipRef.value && tooltipRef.value.hide();
    };
    const updatePopper = () => {
      tooltipRef.value && tooltipRef.value.updatePopper();
    };
    const handleUpdateVisible = (visible) => {
      emit("update:visible", visible);
      emit("visibleChange", visible);
    };
    const handlePopBeforeEnter = () => {
      emit("before-enter");
    };
    const handlePopBeforeLeave = () => {
      emit("before-leave");
    };
    const handlePopAfterEnter = () => {
      emit("after-enter");
    };
    const handlePopAfterLeave = () => {
      emit("after-leave");
    };
    const handleItemClick = (item, e) => {
      if (props2.hideOnClick && !item.children?.length) {
        hidePopper();
      }
      if (item.onClick) {
        item.onClick(e);
      }
      emit("command", item.command);
    };
    const handleOpen = () => {
      if (props2.disabled) {
        return;
      }
      tooltipRef.value && tooltipRef.value.handleOpen();
    };
    const handleClose = () => {
      hidePopper();
    };
    const handleWrapperContext = (e) => {
      if (props2.preventContextmenu) {
        e.preventDefault();
      }
    };
    __expose({
      tooltipRef,
      hidePopper,
      updatePopper,
      handleOpen,
      handleClose
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleTooltip, vue.mergeProps({ tabindex: _ctx.tabindex }, tooltipProps.value, {
        ref_key: "tooltipRef",
        ref: tooltipRef,
        "onUpdate:visible": handleUpdateVisible,
        onBeforeShow: handlePopBeforeEnter,
        onBeforeHide: handlePopBeforeLeave,
        onShow: handlePopAfterEnter,
        onHide: handlePopAfterLeave
      }), {
        body: vue.withCtx(() => [
          hasSubMenu.value ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            class: "ele-dropdown-wrapper",
            onContextmenu: handleWrapperContext
          }, [
            _ctx.items && _ctx.items.length ? (vue.openBlock(), vue.createBlock(DropdownMenus, {
              key: 0,
              role: _ctx.role,
              items: _ctx.items,
              selected: _ctx.modelValue,
              menuStyle: _ctx.menuStyle,
              iconProps: _ctx.iconProps,
              iconSize: _ctx.iconSize,
              size: _ctx.size,
              onItemClick: handleItemClick,
              onWrapperContext: handleWrapperContext
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter((k) => "default" !== k), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["role", "items", "selected", "menuStyle", "iconProps", "iconSize", "size"])) : vue.createCommentVNode("", true)
          ], 32)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElScrollbar), {
            key: 1,
            maxHeight: _ctx.maxHeight,
            class: "ele-dropdown-wrapper",
            onContextmenu: handleWrapperContext
          }, {
            default: vue.withCtx(() => [
              _ctx.items && _ctx.items.length ? (vue.openBlock(), vue.createBlock(DropdownMenus, {
                key: 0,
                role: _ctx.role,
                items: _ctx.items,
                selected: _ctx.modelValue,
                menuStyle: _ctx.menuStyle,
                iconProps: _ctx.iconProps,
                iconSize: _ctx.iconSize,
                size: _ctx.size,
                onItemClick: handleItemClick,
                onWrapperContext: handleWrapperContext
              }, vue.createSlots({ _: 2 }, [
                vue.renderList(Object.keys(_ctx.$slots).filter((k) => "default" !== k), (name) => {
                  return {
                    name,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                    ])
                  };
                })
              ]), 1032, ["role", "items", "selected", "menuStyle", "iconProps", "iconSize", "size"])) : vue.createCommentVNode("", true)
            ]),
            _: 3
          }, 8, ["maxHeight"]))
        ]),
        default: vue.withCtx(() => [
          _ctx.splitButton ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), vue.mergeProps({
            key: 0,
            type: _ctx.type,
            size: _ctx.size,
            disabled: _ctx.disabled,
            icon: vue.unref(index.ArrowDown),
            class: "ele-dropdown-caret-button"
          }, _ctx.caretButtonProps || {}), null, 16, ["type", "size", "disabled", "icon"])) : vue.renderSlot(_ctx.$slots, "default", {
            key: 1,
            active: _ctx.modelValue,
            selected: __props.selected
          })
        ]),
        _: 3
      }, 16, ["tabindex"]);
    };
  }
});
module.exports = _sfc_main;
