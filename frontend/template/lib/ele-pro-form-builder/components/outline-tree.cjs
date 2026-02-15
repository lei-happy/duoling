"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../../utils/common");
const buildCore = require("./build-core");
const buildUtil = require("./build-util");
const OutlineList = require("./outline-list");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "OutlineTree" },
  __name: "outline-tree",
  props: {
    formItems: {},
    currentFormItemId: {},
    componentData: {},
    itemTypeData: {}
  },
  emits: ["update:currentFormItemId", "updateItems", "updateItemChildren", "openTableTool", "openComponentPicker"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const collapseItemIds = vue.ref([]);
    const handleUpdateCurrentFormItemId = (itemId) => {
      emit("update:currentFormItemId", itemId);
    };
    const handleUpdateItems = (result) => {
      emit("updateItems", result);
    };
    const handleDeleteItem = (formItemId) => {
      handleUpdateItems({
        deleteItemIds: [formItemId],
        addItems: [],
        updateItems: []
      });
    };
    const handleCopyItem = (formItemId) => {
      handleUpdateItems(buildUtil.generateCopyItemData(formItemId, props.formItems));
    };
    const handleAddChildren = (triggerItem, action) => {
      if (triggerItem.type && buildCore.fixedChildTypes.some((d) => d.type === triggerItem.type)) {
        const result = buildUtil.generateAddChildData(
          triggerItem,
          void 0,
          void 0,
          action,
          props.formItems,
          void 0,
          props.componentData
        );
        handleUpdateItems(result);
      } else {
        emit("openComponentPicker", triggerItem.key);
      }
    };
    const handleOpenTableTool = (item, e) => {
      const el = e.currentTarget;
      const triggerEl = el?.parentElement?.querySelector?.(
        ".ele-pro-form-builder-outline-item-table-tool-trigger"
      );
      emit("openTableTool", item.key, triggerEl);
    };
    const handleUpdateItemChildren = (children, parentKey) => {
      emit("updateItemChildren", children, parentKey);
    };
    const handleToggleItemCollapse = (formItemId) => {
      const index = collapseItemIds.value.indexOf(formItemId);
      if (index !== -1) {
        collapseItemIds.value.splice(index, 1);
      } else {
        collapseItemIds.value.push(formItemId);
      }
    };
    vue.watch(
      () => props.formItems,
      (items) => {
        for (let i = collapseItemIds.value.length - 1; i >= 0; i--) {
          if (!common.findTree(items, (item) => collapseItemIds.value[i] === item.key)) {
            collapseItemIds.value.splice(i, 1);
          }
        }
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        __props.formItems ? (vue.openBlock(), vue.createBlock(OutlineList, {
          key: 0,
          items: __props.formItems,
          currentFormItemId: __props.currentFormItemId,
          collapseItemIds: collapseItemIds.value,
          componentData: __props.componentData,
          itemTypeData: __props.itemTypeData,
          "onUpdate:currentFormItemId": handleUpdateCurrentFormItemId,
          onToggleItemCollapse: handleToggleItemCollapse,
          onDeleteItem: handleDeleteItem,
          onCopyItem: handleCopyItem,
          onAddChildren: handleAddChildren,
          onOpenTableTool: handleOpenTableTool,
          onUpdateItemChildren: handleUpdateItemChildren
        }, null, 8, ["items", "currentFormItemId", "collapseItemIds", "componentData", "itemTypeData"])) : vue.createCommentVNode("", true),
        !__props.formItems || !__props.formItems.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElEmpty), {
          key: 1,
          imageSize: 58,
          class: "ele-pro-form-builder-form-empty"
        })) : vue.createCommentVNode("", true)
      ], 64);
    };
  }
});
module.exports = _sfc_main;
