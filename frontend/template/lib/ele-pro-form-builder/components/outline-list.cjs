"use strict";
const vue = require("vue");
const VueDraggable = require("vuedraggable");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const util = require("../../ele-pro-form/util");
const buildCore = require("./build-core");
const ComponentName = require("./component-name");
const _hoisted_1 = ["title", "onClick"];
const _hoisted_2 = { class: "ele-pro-form-builder-outline-item-content" };
const _hoisted_3 = { class: "ele-pro-form-builder-outline-item-prop" };
const _hoisted_4 = {
  key: 0,
  class: "ele-pro-form-builder-outline-item-label"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "OutlineList" },
  __name: "outline-list",
  props: {
    items: {},
    currentFormItemId: {},
    collapseItemIds: {},
    parent: {},
    componentData: {},
    itemTypeData: {}
  },
  emits: ["update:currentFormItemId", "toggleItemCollapse", "deleteItem", "copyItem", "addChildren", "updateItemChildren", "openTableTool"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const handleOpenTableTool = (item, e) => {
      emit("openTableTool", item, e);
    };
    const handleUpdateCurrentFormItemId = (itemId) => {
      emit("update:currentFormItemId", itemId);
    };
    const handleToggleItemCollapse = (formItemId) => {
      emit("toggleItemCollapse", formItemId);
    };
    const handleDeleteItem = (formItemId) => {
      emit("deleteItem", formItemId);
    };
    const handleCopyItem = (formItemId) => {
      emit("copyItem", formItemId);
    };
    const handleAddChildren = (triggerItem, action) => {
      emit("addChildren", triggerItem, action);
    };
    const handleUpdateItemChildren = (children, parentKey) => {
      emit("updateItemChildren", children, parentKey);
    };
    const handleUpdateModelValue = (data) => {
      if (props.parent != null && props.parent.key == null) {
        return;
      }
      handleUpdateItemChildren(data, props.parent?.key);
    };
    const itemIsContainerType = (item) => {
      return util.isContainerType(item, props.itemTypeData);
    };
    const isTableChildType = (item) => {
      if (!item.type) {
        return false;
      }
      return ["tableRow", "tableCell"].includes(item.type);
    };
    return (_ctx, _cache) => {
      const _component_OutlineList = vue.resolveComponent("OutlineList", true);
      return vue.openBlock(), vue.createBlock(vue.unref(VueDraggable), {
        itemKey: "key",
        modelValue: __props.items,
        forceFallback: true,
        fallbackOnBody: true,
        setData: () => void 0,
        group: "ProFormBuilderOutlineSortGroup",
        handle: ".ele-pro-form-builder-outline-item-handle",
        class: "ele-pro-form-builder-outline",
        "onUpdate:modelValue": handleUpdateModelValue
      }, {
        item: vue.withCtx(({ element }) => [
          vue.createElementVNode("div", {
            class: vue.normalizeClass(["ele-pro-form-builder-outline-item", [
              {
                "is-active": element.key != null && __props.currentFormItemId != null && __props.currentFormItemId === element.key
              },
              {
                "is-collapse": element.key != null && __props.collapseItemIds && __props.collapseItemIds.includes(element.key)
              },
              { "is-form-item": !itemIsContainerType(element) }
            ]])
          }, [
            itemIsContainerType(element) ? (vue.openBlock(), vue.createBlock(_component_OutlineList, {
              key: 0,
              items: element.children || [],
              currentFormItemId: __props.currentFormItemId,
              collapseItemIds: __props.collapseItemIds,
              parent: element,
              componentData: __props.componentData,
              itemTypeData: __props.itemTypeData,
              "onUpdate:currentFormItemId": handleUpdateCurrentFormItemId,
              onToggleItemCollapse: handleToggleItemCollapse,
              onDeleteItem: handleDeleteItem,
              onCopyItem: handleCopyItem,
              onAddChildren: handleAddChildren,
              onOpenTableTool: handleOpenTableTool,
              onUpdateItemChildren: handleUpdateItemChildren
            }, null, 8, ["items", "currentFormItemId", "collapseItemIds", "parent", "componentData", "itemTypeData"])) : vue.createCommentVNode("", true),
            vue.createElementVNode("div", {
              class: "ele-pro-form-builder-outline-item-body",
              title: `${element.prop ?? ""} ${element.label ?? ""}`,
              onClick: ($event) => handleUpdateCurrentFormItemId(element.key)
            }, [
              element.children && element.children.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 0,
                class: "ele-pro-form-builder-outline-item-arrow",
                onClick: vue.withModifiers(($event) => handleToggleItemCollapse(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.ArrowDown))
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", _hoisted_2, [
                vue.createVNode(ComponentName, {
                  itemType: element.type,
                  componentData: __props.componentData,
                  class: "ele-pro-form-builder-outline-item-type-tag"
                }, null, 8, ["itemType", "componentData"]),
                vue.createElementVNode("span", _hoisted_3, vue.toDisplayString(element.prop), 1),
                element.label ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_4, vue.toDisplayString(element.label), 1)) : vue.createCommentVNode("", true)
              ]),
              !isTableChildType(element) ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 1,
                class: "ele-pro-form-builder-outline-item-tool is-danger",
                title: "删除",
                onClick: vue.withModifiers(($event) => handleDeleteItem(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DeleteOutlined))
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              !isTableChildType(element) ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 2,
                class: "ele-pro-form-builder-outline-item-tool",
                title: "复制",
                onClick: vue.withModifiers(($event) => handleCopyItem(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.CopyOutlined))
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              element.type === "table" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 3,
                class: "ele-pro-form-builder-outline-item-tool",
                title: "新增行",
                onClick: vue.withModifiers(($event) => handleAddChildren(element, "addTableRow"), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.InsertRowOutlined))
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              element.type === "table" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 4,
                class: "ele-pro-form-builder-outline-item-tool",
                title: "新增列",
                onClick: vue.withModifiers(($event) => handleAddChildren(element, "addTableCol"), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.InsertColumnOutlined))
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              element.type === "tableCell" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 5,
                class: "ele-pro-form-builder-outline-item-tool",
                title: "更多",
                onClick: vue.withModifiers((e) => handleOpenTableTool(element, e), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.AppstoreAddOutlined), { style: { transform: "scale(1.1)" } })
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              itemIsContainerType(element) && element.type !== "table" && element.type !== "tableRow" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 6,
                class: "ele-pro-form-builder-outline-item-tool",
                title: {
                  tabs: "添加选项卡",
                  tabPane: "插入选项卡",
                  collapse: "添加折叠面板",
                  collapseItem: "插入折叠面板",
                  row: "添加栅格列",
                  col: "插入栅格列",
                  carousel: "添加走马灯",
                  carouselItem: "插入走马灯",
                  descriptions: "添加描述列表",
                  descriptionsItem: "插入描述列表"
                }[element.type] || "添加子级",
                onClick: vue.withModifiers(($event) => handleAddChildren(element), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  element.type && vue.unref(buildCore.fixedChildTypes).some((d) => d.type === element.type) ? (vue.openBlock(), vue.createBlock(vue.unref(index.PlusSquareDashOutlined), { key: 0 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.PlusOutlined), {
                    key: 1,
                    style: { transform: "scale(1.1)" }
                  }))
                ]),
                _: 2
              }, 1032, ["title", "onClick"])) : vue.createCommentVNode("", true),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                title: "",
                class: "ele-pro-form-builder-outline-item-handle",
                onClick: _cache[0] || (_cache[0] = vue.withModifiers(() => {
                }, ["stop"]))
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DragOutlined), { style: { transform: "scale(1.1)" } })
                ]),
                _: 1
              }),
              _cache[1] || (_cache[1] = vue.createElementVNode("div", { class: "ele-pro-form-builder-outline-item-table-tool-trigger" }, null, -1))
            ], 8, _hoisted_1),
            _cache[2] || (_cache[2] = vue.createElementVNode("div", { class: "ele-pro-form-builder-outline-item-border" }, null, -1))
          ], 2)
        ]),
        _: 1
      }, 8, ["modelValue"]);
    };
  }
});
module.exports = _sfc_main;
