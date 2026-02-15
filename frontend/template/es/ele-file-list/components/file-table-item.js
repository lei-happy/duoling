import { defineComponent, ref, computed, createElementBlock, openBlock, withModifiers, normalizeClass, createElementVNode, createCommentVNode, renderSlot, toDisplayString, Fragment, renderList, normalizeStyle, createTextVNode } from "vue";
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
const _sfc_main = /* @__PURE__ */ defineComponent({
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
    const dropdownTriggerRef = ref(null);
    const selectable = computed(() => {
      return props.selectionType === "checkbox" || props.selectionType === "radio";
    });
    const selected = computed(() => {
      if (!selectable.value || !props.item) {
        return false;
      }
      if (props.selectionType === "checkbox") {
        return !!(props.selections && props.selections.some((t) => t.key === props.item.key));
      }
      return !!(props.current && props.current.key === props.item.key);
    });
    const icon = computed(() => {
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
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["ele-file-list-item", [
          { "is-checked": selected.value },
          { "is-active": __props.ctxMenuDropdownVisible }
        ]]),
        onClick: withModifiers(handleClick, ["stop"])
      }, [
        createElementVNode("div", {
          class: "ele-file-list-item-body",
          onContextmenu: handleContextmenu
        }, [
          selectable.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
            createElementVNode("i", {
              class: normalizeClass(["ele-file-list-checkbox", [
                { "is-radio": __props.selectionType === "radio" },
                { "is-checked": selected.value }
              ]]),
              onClick: withModifiers(handleCheckChange, ["stop"])
            }, null, 2)
          ])) : createCommentVNode("", true),
          createElementVNode("div", _hoisted_2, [
            createElementVNode("div", _hoisted_3, [
              renderSlot(_ctx.$slots, "icon", {
                icon: icon.value,
                item: __props.item
              }, () => [
                createElementVNode("img", {
                  src: icon.value,
                  class: normalizeClass({ "ele-file-list-item-image": !!__props.item.thumbnail })
                }, null, 10, _hoisted_4)
              ]),
              renderSlot(_ctx.$slots, "title", { item: __props.item }, () => [
                createElementVNode("div", {
                  title: __props.item.name,
                  class: "ele-file-list-item-title"
                }, toDisplayString(__props.item.name), 9, _hoisted_5)
              ])
            ]),
            _ctx.$slots.tool ? (openBlock(), createElementBlock("div", _hoisted_6, [
              renderSlot(_ctx.$slots, "tool", { item: __props.item })
            ])) : createCommentVNode("", true)
          ]),
          (openBlock(true), createElementBlock(Fragment, null, renderList(__props.columns, (col) => {
            return openBlock(), createElementBlock("div", {
              key: col.prop,
              style: normalizeStyle(col.style),
              class: "ele-file-list-item-cell"
            }, [
              col.slot && !["icon", "title", "tool", "contextMenu"].includes(col.slot) && _ctx.$slots[col.slot] ? renderSlot(_ctx.$slots, col.slot, {
                key: 0,
                item: __props.item,
                col
              }) : __props.item && col && col.prop ? (openBlock(), createElementBlock(Fragment, { key: 1 }, [
                createTextVNode(toDisplayString(__props.item[col.prop]), 1)
              ], 64)) : createCommentVNode("", true)
            ], 4);
          }), 128))
        ], 32),
        createElementVNode("div", {
          ref_key: "dropdownTriggerRef",
          ref: dropdownTriggerRef,
          class: "ele-file-list-item-dropdown",
          onClick: _cache[0] || (_cache[0] = withModifiers(() => {
          }, ["stop"]))
        }, null, 512)
      ], 2);
    };
  }
});
export {
  _sfc_main as default
};
