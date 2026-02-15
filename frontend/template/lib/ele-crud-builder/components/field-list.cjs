"use strict";
const vue = require("vue");
const VueDraggable = require("vuedraggable");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = ["title"];
const _hoisted_2 = { class: "ele-crud-builder-field-item-content" };
const _hoisted_3 = { class: "ele-crud-builder-field-item-prop" };
const _hoisted_4 = {
  key: 0,
  class: "ele-crud-builder-field-item-label"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "FieldList" },
  __name: "field-list",
  props: {
    items: {},
    collapseItemIds: {},
    parent: {}
  },
  emits: ["toggleItemCollapse", "deleteItem", "copyItem", "editItem", "addChildren", "updateItemChildren"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const handleToggleItemCollapse = (key) => {
      emit("toggleItemCollapse", key);
    };
    const handleDeleteItem = (key) => {
      emit("deleteItem", key);
    };
    const handleCopyItem = (key) => {
      emit("copyItem", key);
    };
    const handleEditItem = (item) => {
      emit("editItem", item);
    };
    const handleAddChildren = (parentKey) => {
      emit("addChildren", parentKey);
    };
    const handleUpdateItemChildren = (data, parentKey) => {
      emit("updateItemChildren", data, parentKey);
    };
    const handleUpdateModelValue = (data) => {
      if (props.parent != null && props.parent.key == null) {
        return;
      }
      handleUpdateItemChildren(data, props.parent?.key);
    };
    return (_ctx, _cache) => {
      const _component_FieldList = vue.resolveComponent("FieldList", true);
      return vue.openBlock(), vue.createBlock(vue.unref(VueDraggable), {
        itemKey: "key",
        modelValue: __props.items,
        forceFallback: true,
        fallbackOnBody: true,
        setData: () => void 0,
        group: "CrudBuilderFieldSortGroup",
        handle: ".ele-crud-builder-field-item-handle",
        class: "ele-crud-builder-field",
        "onUpdate:modelValue": handleUpdateModelValue
      }, {
        item: vue.withCtx(({ element }) => [
          vue.createElementVNode("div", {
            class: vue.normalizeClass(["ele-crud-builder-field-item", {
              "is-collapse": element.key != null && __props.collapseItemIds && __props.collapseItemIds.includes(element.key)
            }])
          }, [
            vue.createVNode(_component_FieldList, {
              items: element.children || [],
              collapseItemIds: __props.collapseItemIds,
              parent: element,
              onToggleItemCollapse: handleToggleItemCollapse,
              onDeleteItem: handleDeleteItem,
              onCopyItem: handleCopyItem,
              onEditItem: handleEditItem,
              onAddChildren: handleAddChildren,
              onUpdateItemChildren: handleUpdateItemChildren
            }, null, 8, ["items", "collapseItemIds", "parent"]),
            vue.createElementVNode("div", {
              class: "ele-crud-builder-field-item-body",
              title: `${element.prop ?? ""} ${element.label ?? ""}`
            }, [
              element.children && element.children.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 0,
                class: "ele-crud-builder-field-item-arrow",
                onClick: vue.withModifiers(($event) => handleToggleItemCollapse(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.ArrowDown))
                ]),
                _: 1
              }, 8, ["onClick"])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", _hoisted_2, [
                vue.createElementVNode("span", _hoisted_3, vue.toDisplayString(element.prop), 1),
                element.label ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_4, vue.toDisplayString(element.label), 1)) : vue.createCommentVNode("", true)
              ]),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                class: "ele-crud-builder-field-item-tool is-danger",
                title: "删除",
                onClick: vue.withModifiers(($event) => handleDeleteItem(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DeleteOutlined))
                ]),
                _: 1
              }, 8, ["onClick"]),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                class: "ele-crud-builder-field-item-tool",
                title: "复制",
                onClick: vue.withModifiers(($event) => handleCopyItem(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.CopyOutlined), { style: { transform: "scale(0.96)" } })
                ]),
                _: 1
              }, 8, ["onClick"]),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                class: "ele-crud-builder-field-item-tool",
                title: "修改",
                onClick: vue.withModifiers(($event) => handleEditItem(element), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.EditOutlined))
                ]),
                _: 1
              }, 8, ["onClick"]),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                class: "ele-crud-builder-field-item-tool",
                title: "添加子级",
                onClick: vue.withModifiers(($event) => handleAddChildren(element.key), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.PlusOutlined), { style: { transform: "scale(1.1)" } })
                ]),
                _: 1
              }, 8, ["onClick"]),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                title: "",
                class: "ele-crud-builder-field-item-handle",
                onClick: _cache[0] || (_cache[0] = vue.withModifiers(() => {
                }, ["stop"]))
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DragOutlined), { style: { transform: "scale(1.1)" } })
                ]),
                _: 1
              })
            ], 8, _hoisted_1),
            _cache[1] || (_cache[1] = vue.createElementVNode("div", { class: "ele-crud-builder-field-item-border" }, null, -1))
          ], 2)
        ]),
        _: 1
      }, 8, ["modelValue"]);
    };
  }
});
module.exports = _sfc_main;
