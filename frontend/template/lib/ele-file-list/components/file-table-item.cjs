"use strict";
const vue = require("vue");
const _hoisted_1 = {
  key: 0,
  class: "ele-file-list-item-checkbox"
};
const _hoisted_2 = { class: "ele-file-list-item-name" };
const _hoisted_3 = { class: "ele-file-list-item-icon" };
const _hoisted_4 = ["src"];
const _hoisted_5 = ["title"];
const _hoisted_6 = {
  key: 0,
  class: "ele-file-list-item-tools"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "FileTableItem" },
  __name: "file-table-item",
  props: {
    /** 数据 */
    item: {
      type: Object,
      required: true
    },
    /** 选择框类型 */
    selectionType: String,
    /** 多选选中数据 */
    selections: Array,
    /** 单选选中数据 */
    current: Object,
    /** 后缀对应的图标 */
    icons: Array,
    /** 自定义列配置 */
    columns: Array,
    /** 右键下拉菜单是否显示 */
    ctxMenuDropdownVisible: Boolean
  },
  emits: {
    click: (_item) => true,
    checkChange: (_item) => true,
    contextOpen: (_option) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const dropdownTriggerRef = vue.ref(null);
    const selectable = vue.computed(() => {
      return props.selectionType === "checkbox" || props.selectionType === "radio";
    });
    const selected = vue.computed(() => {
      if (!selectable.value || !props.item) {
        return false;
      }
      if (props.selectionType === "checkbox") {
        return !!(props.selections && props.selections.some((t) => t.key === props.item.key));
      }
      return !!(props.current && props.current.key === props.item.key);
    });
    const icon = vue.computed(() => {
      if (props.item.thumbnail) {
        return props.item.thumbnail;
      }
      if (!props.icons) {
        return;
      }
      if (props.item.isDirectory) {
        return props.icons.find((d) => d.type === "dir")?.icon;
      }
      if (props.item.name) {
        const icon2 = props.icons.find((d) => {
          if (!d.suffixes) {
            return false;
          }
          return !!d.suffixes.find((t) => !!props.item.name.endsWith(t));
        })?.icon;
        if (icon2) {
          return icon2;
        }
      }
      return props.icons.find((d) => d.type === "file")?.icon;
    });
    const handleClick = () => {
      emit("click", props.item);
    };
    const handleCheckChange = () => {
      emit("checkChange", props.item);
    };
    const handleContextmenu = (e) => {
      if (dropdownTriggerRef.value != null) {
        emit("contextOpen", {
          item: props.item,
          triggerEl: dropdownTriggerRef.value,
          e
        });
      }
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-file-list-item", [
          { "is-checked": selected.value },
          { "is-active": __props.ctxMenuDropdownVisible }
        ]]),
        onClick: vue.withModifiers(handleClick, ["stop"])
      }, [
        vue.createElementVNode("div", {
          class: "ele-file-list-item-body",
          onContextmenu: handleContextmenu
        }, [
          selectable.value ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
            vue.createElementVNode("i", {
              class: vue.normalizeClass(["ele-file-list-checkbox", [
                { "is-radio": __props.selectionType === "radio" },
                { "is-checked": selected.value }
              ]]),
              onClick: vue.withModifiers(handleCheckChange, ["stop"])
            }, null, 2)
          ])) : vue.createCommentVNode("", true),
          vue.createElementVNode("div", _hoisted_2, [
            vue.createElementVNode("div", _hoisted_3, [
              vue.renderSlot(_ctx.$slots, "icon", {
                icon: icon.value,
                item: __props.item
              }, () => [
                vue.createElementVNode("img", {
                  src: icon.value,
                  class: vue.normalizeClass({ "ele-file-list-item-image": !!__props.item.thumbnail })
                }, null, 10, _hoisted_4)
              ]),
              vue.renderSlot(_ctx.$slots, "title", { item: __props.item }, () => [
                vue.createElementVNode("div", {
                  title: __props.item.name,
                  class: "ele-file-list-item-title"
                }, vue.toDisplayString(__props.item.name), 9, _hoisted_5)
              ])
            ]),
            _ctx.$slots.tool ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_6, [
              vue.renderSlot(_ctx.$slots, "tool", { item: __props.item })
            ])) : vue.createCommentVNode("", true)
          ]),
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.columns, (col) => {
            return vue.openBlock(), vue.createElementBlock("div", {
              key: col.prop,
              style: vue.normalizeStyle(col.style),
              class: "ele-file-list-item-cell"
            }, [
              col.slot && !["icon", "title", "tool", "contextMenu"].includes(col.slot) && _ctx.$slots[col.slot] ? vue.renderSlot(_ctx.$slots, col.slot, {
                key: 0,
                item: __props.item,
                col
              }) : __props.item && col && col.prop ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                vue.createTextVNode(vue.toDisplayString(__props.item[col.prop]), 1)
              ], 64)) : vue.createCommentVNode("", true)
            ], 4);
          }), 128))
        ], 32),
        vue.createElementVNode("div", {
          ref_key: "dropdownTriggerRef",
          ref: dropdownTriggerRef,
          class: "ele-file-list-item-dropdown",
          onClick: _cache[0] || (_cache[0] = vue.withModifiers(() => {
          }, ["stop"]))
        }, null, 512)
      ], 2);
    };
  }
});
module.exports = _sfc_main;
