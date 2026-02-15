"use strict";
const vue = require("vue");
const EleModalRender = require("../ele-modal-render/index");
const util = require("../ele-modal-render/util");
const EleDropdown = require("../ele-dropdown/index");
const util$1 = require("../ele-dropdown-provider/util");
const ElePopconfirm = require("../ele-popconfirm/index");
const util$2 = require("../ele-popconfirm-provider/util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleApp" },
  __name: "index",
  setup(__props, { expose: __expose }) {
    const {
      modals,
      openModal,
      closeModal,
      closeAllModal,
      removeModal,
      updateModalVisible,
      updateModalProps
    } = util.useModalRenderProvider();
    const {
      dropdownRef,
      dropdownVirtualRef,
      dropdownItems,
      dropdownProps,
      openDropdown
    } = util$1.useDropdownProvider();
    const {
      popconfirmRef,
      popconfirmVirtualRef,
      popconfirmProps,
      openPopconfirm
    } = util$2.usePopconfirmProvider();
    __expose({
      // 弹窗操作
      openModal,
      closeModal,
      closeAllModal,
      updateModalProps,
      // 下拉菜单操作
      openDropdown,
      // 气泡确认框操作
      openPopconfirm
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.renderSlot(_ctx.$slots, "default"),
        vue.createVNode(vue.unref(EleModalRender), {
          modals: vue.unref(modals),
          onRemoveItem: vue.unref(removeModal),
          onUpdateItemVisible: vue.unref(updateModalVisible),
          onUpdateItemProps: vue.unref(updateModalProps)
        }, null, 8, ["modals", "onRemoveItem", "onUpdateItemVisible", "onUpdateItemProps"]),
        vue.createVNode(EleDropdown, vue.mergeProps(vue.unref(dropdownProps), {
          ref_key: "dropdownRef",
          ref: dropdownRef,
          triggerKeys: [],
          persistent: false,
          componentType: "pro",
          virtualTriggering: true,
          virtualRef: vue.unref(dropdownVirtualRef),
          disabled: !vue.unref(dropdownItems).length,
          items: vue.unref(dropdownItems)
        }), null, 16, ["virtualRef", "disabled", "items"]),
        vue.createVNode(ElePopconfirm, vue.mergeProps({
          width: 200,
          triggerKeys: [],
          persistent: false,
          placement: "top-end"
        }, vue.unref(popconfirmProps), {
          ref_key: "popconfirmRef",
          ref: popconfirmRef,
          virtualTriggering: true,
          virtualRef: vue.unref(popconfirmVirtualRef)
        }), null, 16, ["virtualRef"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
