"use strict";
const vue = require("vue");
const VueDraggable = require("vuedraggable");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const buildCore = require("./build-core");
const ComponentName = require("./component-name");
const _hoisted_1 = { class: "ele-pro-form-builder-children-edit-item" };
const _hoisted_2 = {
  key: 0,
  class: "ele-pro-form-builder-children-edit-item-body"
};
const _hoisted_3 = {
  key: 1,
  class: "ele-pro-form-builder-children-edit-item-body"
};
const _hoisted_4 = ["onClick"];
const _hoisted_5 = { class: "ele-pro-form-builder-children-edit-item-text" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ChildrenEdit" },
  __name: "children-edit",
  props: {
    addBtnText: {},
    formItem: {},
    componentData: {}
  },
  emits: ["update:currentFormItemId", "updateChildLabel", "sortChildren", "deleteChildren", "addChildren"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const isFixedChildType = vue.computed(() => {
      const parentType = props.formItem?.type;
      return !!(parentType && buildCore.fixedChildTypes.some((d) => d.type === parentType));
    });
    const handleUpdateLabel = (value, item, field) => {
      emit("updateChildLabel", value, item, field);
    };
    const handleUpdateChildren = (children) => {
      emit("sortChildren", children);
    };
    const handleDelete = (item) => {
      emit("deleteChildren", item);
    };
    const handleClick = (item) => {
      emit("update:currentFormItemId", item.key);
    };
    const handleAdd = () => {
      emit("addChildren", props.formItem);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        __props.formItem.children ? (vue.openBlock(), vue.createBlock(vue.unref(VueDraggable), {
          key: 0,
          itemKey: "key",
          animation: 150,
          setData: () => void 0,
          modelValue: __props.formItem.children,
          handle: ".ele-pro-form-builder-children-edit-item-handle",
          class: "ele-pro-form-builder-children-edit-list",
          "onUpdate:modelValue": handleUpdateChildren
        }, {
          item: vue.withCtx(({ element }) => [
            vue.createElementVNode("div", _hoisted_1, [
              vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-pro-form-builder-children-edit-item-handle" }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DragOutlined))
                ]),
                _: 1
              }),
              __props.formItem.type && __props.formItem.type === "tabs" ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
                vue.createVNode(vue.unref(elementPlus.ElInput), {
                  size: "small",
                  modelValue: element.props?.label,
                  "onUpdate:modelValue": (value) => handleUpdateLabel(value, element, "props.label")
                }, null, 8, ["modelValue", "onUpdate:modelValue"])
              ])) : __props.formItem.type && __props.formItem.type === "collapse" ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_3, [
                vue.createVNode(vue.unref(elementPlus.ElInput), {
                  size: "small",
                  modelValue: element.props?.title,
                  "onUpdate:modelValue": (value) => handleUpdateLabel(value, element, "props.title")
                }, null, 8, ["modelValue", "onUpdate:modelValue"])
              ])) : (vue.openBlock(), vue.createElementBlock("div", {
                key: 2,
                class: "ele-pro-form-builder-children-edit-item-body is-clickable",
                onClick: vue.withModifiers(($event) => handleClick(element), ["stop"])
              }, [
                vue.createVNode(ComponentName, {
                  itemType: element.type,
                  componentData: __props.componentData,
                  class: "ele-pro-form-builder-outline-item-type-tag"
                }, null, 8, ["itemType", "componentData"]),
                vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(element.label || element.prop), 1)
              ], 8, _hoisted_4)),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                class: "ele-pro-form-builder-children-edit-item-del-btn",
                title: "删除",
                onClick: vue.withModifiers(($event) => handleDelete(element), ["stop"])
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DeleteOutlined))
                ]),
                _: 1
              }, 8, ["onClick"])
            ])
          ]),
          _: 1
        }, 8, ["modelValue"])) : vue.createCommentVNode("", true),
        vue.createVNode(vue.unref(elementPlus.ElButton), {
          size: "small",
          icon: isFixedChildType.value ? vue.unref(index.PlusSquareDashOutlined) : vue.unref(index.PlusOutlined),
          class: "ele-pro-form-builder-props-fluid-btn is-small-icon",
          onClick: handleAdd
        }, vue.createSlots({ _: 2 }, [
          __props.addBtnText ? {
            name: "default",
            fn: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(__props.addBtnText), 1)
            ]),
            key: "0"
          } : void 0
        ]), 1032, ["icon"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
