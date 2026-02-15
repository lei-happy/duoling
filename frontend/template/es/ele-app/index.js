import { defineComponent, createElementBlock, openBlock, Fragment, renderSlot, createVNode, unref, mergeProps } from "vue";
import EleModalRender from "../ele-modal-render/index";
import { useModalRenderProvider } from "../ele-modal-render/util";
import EleDropdown from "../ele-dropdown/index";
import { useDropdownProvider } from "../ele-dropdown-provider/util";
import ElePopconfirm from "../ele-popconfirm/index";
import { usePopconfirmProvider } from "../ele-popconfirm-provider/util";
const _sfc_main = /* @__PURE__ */ defineComponent({
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
    } = useModalRenderProvider();
    const {
      dropdownRef,
      dropdownVirtualRef,
      dropdownItems,
      dropdownProps,
      openDropdown
    } = useDropdownProvider();
    const {
      popconfirmRef,
      popconfirmVirtualRef,
      popconfirmProps,
      openPopconfirm
    } = usePopconfirmProvider();
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
      return openBlock(), createElementBlock(Fragment, null, [
        renderSlot(_ctx.$slots, "default"),
        createVNode(unref(EleModalRender), {
          modals: unref(modals),
          onRemoveItem: unref(removeModal),
          onUpdateItemVisible: unref(updateModalVisible),
          onUpdateItemProps: unref(updateModalProps)
        }, null, 8, ["modals", "onRemoveItem", "onUpdateItemVisible", "onUpdateItemProps"]),
        createVNode(EleDropdown, mergeProps(unref(dropdownProps), {
          ref_key: "dropdownRef",
          ref: dropdownRef,
          triggerKeys: [],
          persistent: false,
          componentType: "pro",
          virtualTriggering: true,
          virtualRef: unref(dropdownVirtualRef),
          disabled: !unref(dropdownItems).length,
          items: unref(dropdownItems)
        }), null, 16, ["virtualRef", "disabled", "items"]),
        createVNode(ElePopconfirm, mergeProps({
          width: 200,
          triggerKeys: [],
          persistent: false,
          placement: "top-end"
        }, unref(popconfirmProps), {
          ref_key: "popconfirmRef",
          ref: popconfirmRef,
          virtualTriggering: true,
          virtualRef: unref(popconfirmVirtualRef)
        }), null, 16, ["virtualRef"])
      ], 64);
    };
  }
});
export {
  _sfc_main as default
};
