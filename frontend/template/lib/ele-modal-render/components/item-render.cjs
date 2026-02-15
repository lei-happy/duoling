"use strict";
const vue = require("vue");
const EleModal = require("../../ele-modal/index");
const EleDrawer = require("../../ele-drawer/index");
const util = require("../util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ItemRender" },
  __name: "item-render",
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  emits: {
    removeItem: (_modalId) => true,
    updateItemVisible: (_modalId, _visible) => true,
    updateItemProps: (_modalId, _opt) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const removeModal = () => {
      emit("removeItem", props.item.modalId);
    };
    const setModalProps = (option) => {
      emit("updateItemProps", props.item.modalId, option);
    };
    const handleUpdateItemVisible = (visible) => {
      emit("updateItemVisible", props.item.modalId, visible);
    };
    const closeModal = () => {
      handleUpdateItemVisible(false);
    };
    const modalProps = vue.computed(
      () => {
        return {
          ...props.item.props || {},
          isDeactivated: props.item.isDeactivated,
          compLoading: props.item.compLoading,
          modelValue: props.item.visible,
          "onUpdate:modelValue": handleUpdateItemVisible,
          onClosed: removeModal
        };
      }
    );
    const provideData = {
      modalProps,
      closeModal,
      removeModal,
      setModalProps
    };
    vue.provide(util.MODAL_HOLDER_KEY, provideData);
    return (_ctx, _cache) => {
      return __props.item.custom ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
        __props.item.component ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
          typeof __props.item.componentProps === "function" ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.item.component), vue.normalizeProps(vue.mergeProps({ key: 0 }, __props.item.componentProps(provideData) || {})), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter((k) => k !== "default"), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040)) : (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.item.component), vue.normalizeProps(vue.mergeProps({ key: 1 }, __props.item.componentProps || {})), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter((k) => k !== "default"), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040))
        ], 64)) : vue.createCommentVNode("", true)
      ], 64)) : __props.item.type === "drawer" ? (vue.openBlock(), vue.createBlock(EleDrawer, vue.normalizeProps(vue.mergeProps({ key: 1 }, modalProps.value || {})), vue.createSlots({
        default: vue.withCtx(() => [
          __props.item.component ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.item.component), vue.normalizeProps(vue.mergeProps({ key: 0 }, __props.item.componentProps || {})), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter((k) => k !== "default"), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040)) : vue.createCommentVNode("", true)
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
      ]), 1040)) : (vue.openBlock(), vue.createBlock(EleModal, vue.normalizeProps(vue.mergeProps({ key: 2 }, modalProps.value || {})), vue.createSlots({
        default: vue.withCtx(() => [
          __props.item.component ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.item.component), vue.normalizeProps(vue.mergeProps({ key: 0 }, __props.item.componentProps || {})), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter((k) => k !== "default"), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040)) : vue.createCommentVNode("", true)
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
      ]), 1040));
    };
  }
});
module.exports = _sfc_main;
