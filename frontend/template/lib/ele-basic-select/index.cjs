"use strict";
const vue = require("vue");
const common = require("../utils/common");
const EleTooltip = require("../ele-tooltip/index");
const EleModal = require("../ele-modal/index");
const EleDrawer = require("../ele-drawer/index");
const MainContent = require("../ele-loading/components/main-content");
const SelectView = require("./components/select-view");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleBasicSelect" },
  __name: "index",
  props: props.basicSelectProps,
  emits: props.basicSelectEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const selectViewRef = vue.ref(null);
    const tooltipRef = vue.ref(null);
    const modalRef = vue.ref(null);
    const drawerRef = vue.ref(null);
    const isSelectInputClick = vue.ref(false);
    const updateVisible = (visible) => {
      isSelectInputClick.value = false;
      if (!props2.disabled || !visible) {
        emit("update:visible", visible);
      }
    };
    const updatePopper = () => {
      tooltipRef.value && tooltipRef.value.updatePopper();
    };
    const focusSearchInput = (e) => {
      if (props2.filterable && props2.visible) {
        if (e != null && e.target != null) {
          const target = e.target;
          if (target.nodeName && target.nodeName.toLowerCase() === "input") {
            return;
          }
        }
        selectViewRef.value && selectViewRef.value.focusSearchInput();
      }
    };
    const handleUpdatePopoverVisible = (visible) => {
      if (!visible && props2.filterable && isSelectInputClick.value) {
        isSelectInputClick.value = false;
        return;
      }
      updateVisible(visible);
    };
    const handleWrapClick = (isCustom) => {
      isSelectInputClick.value = true;
      if (!isCustom && (props2.popperType === "modal" || props2.popperType === "drawer")) {
        updateVisible(true);
      }
    };
    const handleInputClick = (e) => {
      if (props2.automaticDropdown && props2.visible) {
        isSelectInputClick.value = true;
        e.stopPropagation();
      }
    };
    const handleRemoveTag = (item) => {
      emit("removeTag", item);
    };
    const handleClear = () => {
      isSelectInputClick.value = false;
      emit("clear");
    };
    const handleFocus = (e) => {
      if (props2.automaticDropdown && !props2.visible) {
        updateVisible(true);
      }
      emit("focus", e);
    };
    const handleBlur = (e) => {
      emit("blur", e);
    };
    const handleFilterChange = (value) => {
      emit("filterChange", value);
    };
    __expose({
      selectViewRef,
      tooltipRef,
      modalRef,
      drawerRef,
      updatePopper,
      focusSearchInput,
      updateVisible
    });
    return (_ctx, _cache) => {
      return _ctx.popperType === "modal" || _ctx.popperType === "drawer" ? (vue.openBlock(), vue.createBlock(SelectView, vue.mergeProps({ key: 0 }, _ctx.$props, {
        ref_key: "selectViewRef",
        ref: selectViewRef,
        "onUpdate:visible": updateVisible,
        onRemoveTag: handleRemoveTag,
        onClear: handleClear,
        onFocus: handleFocus,
        onBlur: handleBlur,
        onFilterChange: handleFilterChange,
        onInputClick: handleInputClick,
        onWrapClick: handleWrapClick
      }), vue.createSlots({
        default: vue.withCtx(() => [
          _ctx.popperType === "drawer" ? (vue.openBlock(), vue.createBlock(EleDrawer, vue.mergeProps({
            key: 0,
            title: _ctx.popperTitle,
            size: _ctx.popperWidth,
            destroyOnClose: !_ctx.persistent,
            appendToBody: _ctx.teleported,
            responsive: _ctx.responsive,
            class: _ctx.popperClass
          }, _ctx.popperProps || {}, {
            ref_key: "drawerRef",
            ref: drawerRef,
            modelValue: _ctx.visible,
            "onUpdate:modelValue": handleUpdatePopoverVisible
          }), vue.createSlots({
            default: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "default")
            ]),
            _: 2
          }, [
            vue.renderList(vue.unref(common.getSlotsMap)(
              _ctx.$slots,
              _ctx.popperSlots,
              ["default"],
              ["default"]
            ), (slotName, compSlotName) => {
              return {
                name: compSlotName,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["title", "size", "destroyOnClose", "appendToBody", "responsive", "class", "modelValue"])) : (vue.openBlock(), vue.createBlock(EleModal, vue.mergeProps({
            key: 1,
            position: "center",
            title: _ctx.popperTitle,
            width: _ctx.popperWidth,
            height: _ctx.popperHeight,
            destroyOnClose: !_ctx.persistent,
            appendToBody: _ctx.teleported,
            responsive: _ctx.responsive,
            class: _ctx.popperClass
          }, _ctx.popperProps || {}, {
            ref_key: "modalRef",
            ref: modalRef,
            modelValue: _ctx.visible,
            "onUpdate:modelValue": handleUpdatePopoverVisible
          }), vue.createSlots({
            default: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "default")
            ]),
            _: 2
          }, [
            vue.renderList(vue.unref(common.getSlotsMap)(
              _ctx.$slots,
              _ctx.popperSlots,
              ["default"],
              ["default"]
            ), (slotName, compSlotName) => {
              return {
                name: compSlotName,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["title", "width", "height", "destroyOnClose", "appendToBody", "responsive", "class", "modelValue"]))
        ]),
        _: 2
      }, [
        vue.renderList(Object.keys(_ctx.$slots).filter((k) => k !== "default"), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040)) : _ctx.popperType === "default" ? (vue.openBlock(), vue.createBlock(MainContent, {
        key: 1,
        wrapHeight: _ctx.popperHeight,
        class: vue.normalizeClass(_ctx.popperClass)
      }, {
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "default")
        ]),
        _: 3
      }, 8, ["wrapHeight", "class"])) : (vue.openBlock(), vue.createBlock(EleTooltip, vue.mergeProps({
        key: 2,
        ref_key: "tooltipRef",
        ref: tooltipRef,
        trigger: "click",
        disabled: _ctx.disabled,
        placement: _ctx.placement,
        teleported: _ctx.teleported,
        width: _ctx.popperWidth,
        popperClass: _ctx.popperClass,
        popperOptions: _ctx.popperOptions,
        transition: _ctx.transition,
        gpuAcceleration: _ctx.transition === "el-fade-in-linear",
        effect: "light",
        persistent: true,
        isPopover: true,
        triggerKeys: []
      }, _ctx.popperProps || {}, {
        visible: _ctx.visible,
        "onUpdate:visible": handleUpdatePopoverVisible
      }), {
        body: vue.withCtx(() => [
          _ctx.persistent || _ctx.visible ? (vue.openBlock(), vue.createBlock(MainContent, {
            key: 0,
            wrapHeight: _ctx.popperHeight,
            class: "ele-popover-body",
            onClick: focusSearchInput,
            onMouseup: focusSearchInput
          }, {
            default: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "default")
            ]),
            _: 3
          }, 8, ["wrapHeight"])) : vue.createCommentVNode("", true)
        ]),
        default: vue.withCtx(() => [
          _ctx.selectStyle === "none" ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            class: vue.normalizeClass(_ctx.selectClass)
          }, null, 2)) : (vue.openBlock(), vue.createBlock(SelectView, vue.mergeProps({ key: 1 }, _ctx.$props, {
            ref_key: "selectViewRef",
            ref: selectViewRef,
            "onUpdate:visible": updateVisible,
            onRemoveTag: handleRemoveTag,
            onClear: handleClear,
            onFocus: handleFocus,
            onBlur: handleBlur,
            onFilterChange: handleFilterChange,
            onInputClick: handleInputClick,
            onWrapClick: handleWrapClick
          }), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter((k) => k !== "default"), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040))
        ]),
        _: 3
      }, 16, ["disabled", "placement", "teleported", "width", "popperClass", "popperOptions", "transition", "gpuAcceleration", "visible"]));
    };
  }
});
module.exports = _sfc_main;
