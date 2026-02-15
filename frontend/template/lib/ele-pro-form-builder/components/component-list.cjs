"use strict";
const vue = require("vue");
const VueDraggable = require("vuedraggable");
const common = require("../../utils/common");
const util = require("../../ele-pro-form/util");
const buildCore = require("./build-core");
const _hoisted_1 = { class: "ele-pro-form-builder-component-wrapper" };
const _hoisted_2 = ["onClick"];
const _hoisted_3 = { class: "ele-pro-form-builder-component-item-body" };
const _hoisted_4 = { class: "ele-pro-form-builder-component-item-cover" };
const _hoisted_5 = { class: "ele-pro-form-builder-component-item-label" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ComponentList" },
  __name: "component-list",
  props: {
    formItems: {},
    parentFormItemId: {},
    draggable: { type: Boolean },
    componentData: {},
    itemTypeData: {},
    selectedType: {},
    selectedFormItemId: {}
  },
  emits: ["updateItems", "itemClick"],
  setup(__props, { emit: __emit }) {
    const sortableGroup = { name: util.sortableGroupName, pull: "clone", put: false };
    const props = __props;
    const emit = __emit;
    const groupData = vue.computed(() => {
      return (props.componentData || []).map((groupItem) => {
        return {
          ...groupItem,
          items: groupItem.items.filter((item) => !item.hide).map((d) => ({
            ...d,
            key: `proFormBuilderComponent_${d.type}`
          }))
        };
      });
    });
    const handleCloneItem = (original) => {
      const item = buildCore.generateBuildFormItem(
        original.type,
        props.formItems,
        props.componentData,
        props.itemTypeData
      );
      return item ?? original;
    };
    const handleItemClick = (componentItem) => {
      const item = buildCore.generateBuildFormItem(
        componentItem.type,
        props.formItems,
        props.componentData,
        props.itemTypeData
      );
      if (props.selectedFormItemId == null) {
        const result = {
          addItems: [{ item, parentItemId: props.parentFormItemId }],
          updateItems: [],
          deleteItemIds: []
        };
        emit("updateItems", result);
        return;
      }
      const updateItems = [
        { itemId: props.selectedFormItemId, field: "type", value: item?.type },
        { itemId: props.selectedFormItemId, field: "props", value: item?.props },
        { itemId: props.selectedFormItemId, field: "slots", value: item?.slots }
      ];
      const oldItem = common.findTree(
        props.formItems,
        (d) => d.key === props.selectedFormItemId
      );
      if (oldItem && (buildCore.fixedChildTypes.some((d) => d.type === oldItem.type) || buildCore.fixedChildTypes.some((d) => d.type === item?.type)) && oldItem.type !== item?.type) {
        updateItems.push({
          itemId: props.selectedFormItemId,
          field: "children",
          value: item?.children
        });
      }
      emit("updateItems", { addItems: [], updateItems, deleteItemIds: [] });
    };
    const handleLabelClick = (e) => {
      const el = e.currentTarget?.parentElement;
      el && el.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(groupData.value, (groupItem, index) => {
          return vue.openBlock(), vue.createElementBlock("div", {
            key: `${index}_${groupItem.name}`,
            class: "ele-pro-form-builder-component-group"
          }, [
            vue.createElementVNode("div", {
              class: "ele-pro-form-builder-component-group-label",
              onClick: handleLabelClick
            }, vue.toDisplayString(groupItem.name), 1),
            vue.createVNode(vue.unref(VueDraggable), {
              itemKey: "key",
              sort: false,
              delay: 150,
              delayOnTouchOnly: true,
              fallbackOnBody: true,
              group: sortableGroup,
              disabled: !__props.draggable,
              setData: () => void 0,
              clone: handleCloneItem,
              modelValue: groupItem.items,
              class: "ele-pro-form-builder-component-list"
            }, {
              item: vue.withCtx(({ element }) => [
                vue.createElementVNode("div", {
                  class: vue.normalizeClass(["ele-pro-form-builder-component-item", { "is-selected": element.type === __props.selectedType }]),
                  onClick: ($event) => handleItemClick(element)
                }, [
                  vue.createElementVNode("div", _hoisted_3, [
                    vue.createElementVNode("div", _hoisted_4, [
                      element.cover ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(element.cover), { key: 0 })) : vue.createCommentVNode("", true)
                    ])
                  ]),
                  vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(element.name), 1)
                ], 10, _hoisted_2)
              ]),
              _: 1
            }, 8, ["disabled", "modelValue"])
          ]);
        }), 128))
      ]);
    };
  }
});
module.exports = _sfc_main;
