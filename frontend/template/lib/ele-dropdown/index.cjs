"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const util = require("../ele-basic-select/util");
const ProDropdown = require("./components/pro-dropdown");
const props = require("./props");
const _hoisted_1 = {
  key: 1,
  class: "ele-dropdown-trigger"
};
const _hoisted_2 = { key: 1 };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleDropdown" },
  __name: "index",
  props: props.dropdownProps,
  emits: props.dropdownEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { validateChange } = util.useFormValidate();
    const dropdownRef = vue.ref(null);
    const dropdownPropsData = vue.computed(() => {
      const options = common.pick(props$1, props.elDropdownPropKeys);
      const classes = ["ele-popper", "ele-dropdown"];
      if (props$1.popperClass) {
        classes.push(props$1.popperClass);
      }
      options.popperClass = classes.join(" ");
      return options;
    });
    const selected = vue.computed(() => {
      if (props$1.modelValue == null || props$1.modelValue === "" || !props$1.items) {
        return;
      }
      return props$1.items.find((d) => d.command === props$1.modelValue);
    });
    const updateModelValue = (value) => {
      if (value !== props$1.modelValue) {
        emit("update:modelValue", value);
        if (props$1.validateEvent) {
          validateChange();
        }
        emit("change", value);
      }
    };
    const handleMenuClick = (command) => {
      updateModelValue(command);
      emit("command", command);
    };
    const handleBtnClick = (e) => {
      emit("click", e);
    };
    const handlePopVisibleChange = (visible) => {
      emit("visibleChange", visible);
    };
    const handleOpen = () => {
      if (dropdownRef.value) {
        dropdownRef.value.handleOpen();
      }
    };
    const handleClose = () => {
      if (dropdownRef.value) {
        dropdownRef.value.handleClose();
      }
    };
    const updatePopper = () => {
      if (dropdownRef.value && dropdownRef.value.updatePopper) {
        dropdownRef.value.updatePopper();
      }
    };
    __expose({
      dropdownRef,
      handleOpen,
      handleClose,
      updatePopper
    });
    return (_ctx, _cache) => {
      return _ctx.componentType === "pro" ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
        _ctx.virtualTriggering ? (vue.openBlock(), vue.createBlock(ProDropdown, vue.mergeProps({ key: 0 }, _ctx.$props, {
          ref_key: "dropdownRef",
          ref: dropdownRef,
          splitButton: false,
          selected: selected.value,
          onCommand: handleMenuClick,
          onVisibleChange: handlePopVisibleChange
        }), vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1040, ["selected"])) : (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
          _ctx.splitButton ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButtonGroup), { key: 0 }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElButton), vue.mergeProps({
                type: _ctx.type,
                size: _ctx.size,
                disabled: _ctx.disabled
              }, _ctx.splitButtonProps || {}, { onClick: handleBtnClick }), {
                default: vue.withCtx(() => [
                  vue.renderSlot(_ctx.$slots, "default", {
                    active: _ctx.modelValue,
                    selected: selected.value
                  })
                ]),
                _: 3
              }, 16, ["type", "size", "disabled"]),
              vue.createVNode(ProDropdown, vue.mergeProps(_ctx.$props, {
                ref_key: "dropdownRef",
                ref: dropdownRef,
                selected: selected.value,
                onCommand: handleMenuClick,
                onVisibleChange: handlePopVisibleChange
              }), vue.createSlots({ _: 2 }, [
                vue.renderList(Object.keys(_ctx.$slots), (name) => {
                  return {
                    name,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                    ])
                  };
                })
              ]), 1040, ["selected"])
            ]),
            _: 3
          })) : (vue.openBlock(), vue.createBlock(ProDropdown, vue.mergeProps({ key: 1 }, _ctx.$props, {
            ref_key: "dropdownRef",
            ref: dropdownRef,
            selected: selected.value,
            onCommand: handleMenuClick,
            onVisibleChange: handlePopVisibleChange
          }), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["selected"]))
        ]))
      ], 64)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElDropdown), vue.mergeProps({
        key: 1,
        class: "ele-dropdown-trigger"
      }, dropdownPropsData.value, {
        ref_key: "dropdownRef",
        ref: dropdownRef,
        onClick: handleBtnClick,
        onCommand: handleMenuClick,
        onVisibleChange: handlePopVisibleChange
      }), {
        dropdown: vue.withCtx(() => [
          !_ctx.items && _ctx.$slots.dropdown ? vue.renderSlot(_ctx.$slots, "dropdown", { key: 0 }) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElDropdownMenu), {
            key: 1,
            style: vue.normalizeStyle(_ctx.menuStyle),
            class: vue.normalizeClass({ "ele-dropdown-icon-small": _ctx.iconSize === "small" })
          }, {
            default: vue.withCtx(() => [
              _ctx.items ? (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 0 }, vue.renderList(_ctx.items, (item) => {
                return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElDropdownItem), vue.mergeProps(
                  {
                    key: item.key == null ? JSON.stringify(item.command) : item.key,
                    class: [
                      { "is-active": _ctx.modelValue === item.command },
                      { "is-danger": !!item.danger }
                    ]
                  },
                  { ref_for: true },
                  vue.unref(common.omit)(item, [
                    "icon",
                    "title",
                    "iconProps",
                    "iconStyle",
                    "slot",
                    "danger"
                  ])
                ), {
                  default: vue.withCtx(() => [
                    item.slot && item.slot !== "default" && _ctx.$slots[item.slot] ? vue.renderSlot(_ctx.$slots, item.slot, {
                      key: 0,
                      item
                    }) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                      item.icon ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.mergeProps({
                        key: 0,
                        ref_for: true
                      }, { ..._ctx.iconProps || {}, ...item.iconProps || {} }), {
                        default: vue.withCtx(() => [
                          (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(item.icon), {
                            style: vue.normalizeStyle(item.iconStyle)
                          }, null, 8, ["style"]))
                        ]),
                        _: 2
                      }, 1040)) : vue.createCommentVNode("", true),
                      item.title ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_2, vue.toDisplayString(item.title), 1)) : vue.createCommentVNode("", true)
                    ], 64))
                  ]),
                  _: 2
                }, 1040, ["class"]);
              }), 128)) : _ctx.$slots.dropdownMenu ? vue.renderSlot(_ctx.$slots, "dropdownMenu", { key: 1 }) : vue.createCommentVNode("", true)
            ]),
            _: 3
          }, 8, ["style", "class"]))
        ]),
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "default", {
            active: _ctx.modelValue,
            selected: selected.value
          })
        ]),
        _: 3
      }, 16));
    };
  }
});
module.exports = _sfc_main;
