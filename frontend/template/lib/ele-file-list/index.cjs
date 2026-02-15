"use strict";
const vue = require("vue");
const common = require("../utils/common");
const receiver = require("../ele-config-provider/receiver");
const EleDropdown = require("../ele-dropdown/index");
const FileGrid = require("./components/file-grid");
const FileTable = require("./components/file-table");
const props = require("./props");
const GRID_ITEM_SEL = ".ele-file-list-body>.ele-file-list-item";
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleFileList" },
  __name: "index",
  props: props.fileListProps,
  emits: props.fileListEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("fileList", props2);
    const selectorStyle = vue.reactive({
      top: "0px",
      left: "0px",
      width: "0px",
      height: "0px",
      display: "none"
    });
    const ctxMenuDropdownRef = vue.ref(null);
    const ctxMenuDropdownItems = vue.shallowRef([]);
    const ctxMenuDropdownVirtualRef = vue.ref();
    const ctxMenuDropdownVisible = vue.ref(false);
    const contextMenuFileItem = vue.ref(null);
    const isCheckAll = vue.computed(() => {
      return !!(props2.data && props2.data.length && props2.selections && props2.selections.length && !props2.data.some((d) => !props2.selections?.some?.((t) => d.key === t.key)));
    });
    const isIndeterminate = vue.computed(() => {
      return !!(!isCheckAll.value && props2.selections && props2.selections.length);
    });
    const updateSelections = (selection) => {
      emit("update:selections", selection);
    };
    const updateCurrent = (current) => {
      emit("update:current", current);
    };
    const handleCheckAllChange = () => {
      if (props2.selectionType !== "checkbox") {
        return;
      }
      if (isCheckAll.value || props2.data == null || !props2.data.length) {
        if (!props2.selections) {
          updateSelections([]);
          return;
        }
        const temp2 = props2.selections.filter((d) => {
          return props2.data ? !props2.data.some((t) => t.key === d.key) : true;
        });
        updateSelections(temp2);
        return;
      }
      if (!props2.selections) {
        updateSelections([...props2.data]);
        return;
      }
      const temp = props2.selections.concat(
        props2.data.filter((d) => {
          return props2.selections ? !props2.selections.some((t) => t.key === d.key) : true;
        })
      );
      updateSelections(temp);
    };
    const handleItemCheckChange = (item) => {
      if (props2.selectionType === "radio") {
        updateCurrent(
          props2.current && props2.current.key === item.key ? null : item
        );
        return;
      }
      if (props2.selectionType !== "checkbox") {
        return;
      }
      if (!props2.selections || !props2.selections.length) {
        updateSelections([item]);
        return;
      }
      if (!props2.selections.some((t) => t.key === item.key)) {
        updateSelections(props2.selections.concat([item]));
        return;
      }
      updateSelections(props2.selections.filter((t) => t.key !== item.key));
    };
    const handleItemClick = (item) => {
      emit("itemClick", item);
    };
    const handleSortChange = (name) => {
      const sorter = { sort: name };
      if (props2.order && name === props2.sort) {
        sorter.order = props2.order === "asc" ? "desc" : null;
      } else {
        sorter.order = "asc";
      }
      emit("sortChange", sorter);
    };
    const handleItemCtxMenuClick = (key) => {
      if (contextMenuFileItem.value != null) {
        const option = {
          key,
          item: contextMenuFileItem.value
        };
        emit("itemContextMenu", option);
      }
    };
    const handleItemCtxMenuVisible = (visible) => {
      ctxMenuDropdownVisible.value = visible;
      if (visible && ctxMenuDropdownRef.value != null && contextMenuFileItem.value != null) {
        emit(
          "itemContextOpen",
          ctxMenuDropdownRef.value,
          contextMenuFileItem.value
        );
      }
    };
    const getContextMenus = (item) => {
      if (typeof props2.contextMenus === "function") {
        return props2.contextMenus(item);
      }
      return props2.contextMenus;
    };
    const hideAllDropdown = () => {
      if (ctxMenuDropdownRef.value) {
        ctxMenuDropdownRef.value.handleClose();
      }
    };
    const showItemContextMenu = (item, triggerEl) => {
      if (contextMenuFileItem.value != null && contextMenuFileItem.value === item) {
        return;
      }
      hideAllDropdown();
      vue.nextTick(() => {
        contextMenuFileItem.value = item;
        ctxMenuDropdownItems.value = getContextMenus(item) || [];
        ctxMenuDropdownVirtualRef.value = triggerEl;
        if (ctxMenuDropdownItems.value.length) {
          vue.nextTick(() => {
            ctxMenuDropdownRef.value && ctxMenuDropdownRef.value.handleOpen();
          });
        }
      });
    };
    const handleItemContextOpen = (option) => {
      if (props2.contextMenus == null) {
        return;
      }
      option.e.preventDefault();
      option.e.stopPropagation();
      if (ctxMenuDropdownVirtualRef.value !== option.triggerEl) {
        showItemContextMenu(option.item, option.triggerEl);
        return;
      }
      if (ctxMenuDropdownItems.value.length && ctxMenuDropdownRef.value) {
        ctxMenuDropdownRef.value.handleOpen();
      }
    };
    const handleMousedown = (event) => {
      if (!props2.boxChoose || props2.selectionType !== "checkbox") {
        return;
      }
      const downX = event.clientX;
      const downY = event.clientY;
      const target = event.currentTarget;
      const position = target.getBoundingClientRect();
      const items = Array.from(target.querySelectorAll(GRID_ITEM_SEL));
      const mousemoveFn = common.throttle((e) => {
        const moveX = Math.max(e.clientX, position.left);
        const moveY = Math.max(e.clientY, position.top);
        const left = Math.min(moveX, downX) - position.left;
        const top = Math.min(moveY, downY) - position.top;
        const width = Math.min(
          Math.abs(moveX - downX),
          target.clientWidth - left
        );
        const height = Math.min(
          Math.abs(moveY - downY),
          target.clientHeight - top
        );
        selectorStyle.left = left + "px";
        selectorStyle.top = top + "px";
        selectorStyle.width = width + "px";
        selectorStyle.height = height + "px";
        selectorStyle.display = "block";
        if (width < 6 || height < 6) {
          items.forEach((item) => {
            item.classList.remove("is-active");
          });
          return;
        }
        event.stopPropagation();
        event.preventDefault();
        e.stopPropagation();
        e.preventDefault();
        items.forEach((item) => {
          const itemX = item.offsetLeft + item.clientWidth;
          const itemY = item.offsetTop + item.clientHeight;
          if (itemX > left && itemY > top && item.offsetLeft < left + width && item.offsetTop < top + height) {
            item.classList.add("is-active");
          } else {
            item.classList.remove("is-active");
          }
        });
      }, 60);
      const mouseupFn = (e) => {
        selectorStyle.display = "none";
        const moveX = Math.max(e.clientX, position.left);
        const moveY = Math.max(e.clientY, position.top);
        const left = Math.min(moveX, downX) - position.left;
        const top = Math.min(moveY, downY) - position.top;
        const width = Math.min(
          Math.abs(moveX - downX),
          target.clientWidth - left
        );
        const height = Math.min(
          Math.abs(moveY - downY),
          target.clientHeight - top
        );
        if (width > 6 && height > 6) {
          const checked = [];
          items.forEach((item, i) => {
            if (item.classList.contains("is-active")) {
              item.classList.remove("is-active");
              if (props2.data && props2.data[i]) {
                checked.push(props2.data[i]);
              }
            }
          });
          if (checked.length) {
            updateSelections(checked);
          }
        }
        document.removeEventListener("mousemove", mousemoveFn);
        document.removeEventListener("mouseup", mouseupFn);
      };
      document.addEventListener("mousemove", mousemoveFn);
      document.addEventListener("mouseup", mouseupFn);
    };
    vue.watch(
      [() => props2.grid, () => props2.data],
      () => {
        hideAllDropdown();
        ctxMenuDropdownVirtualRef.value = null;
        contextMenuFileItem.value = null;
      },
      { deep: true }
    );
    vue.onBeforeUnmount(() => {
      contextMenuFileItem.value = null;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-file-list-group",
        onMousedown: handleMousedown
      }, [
        _ctx.grid ? (vue.openBlock(), vue.createBlock(FileGrid, {
          key: 0,
          data: _ctx.data,
          icons: _ctx.icons,
          selectionType: _ctx.selectionType,
          selections: _ctx.selections,
          current: _ctx.current,
          isCheckAll: isCheckAll.value,
          isIndeterminate: isIndeterminate.value,
          checkAllText: vue.unref(lang).selectAll,
          selectedText: vue.unref(lang).selectTips,
          ctxMenuDropdownVisible: ctxMenuDropdownVisible.value,
          contextMenuFileItem: contextMenuFileItem.value,
          onCheckAllChange: handleCheckAllChange,
          onItemClick: handleItemClick,
          onItemCheckChange: handleItemCheckChange,
          onItemContextOpen: handleItemContextOpen
        }, vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1032, ["data", "icons", "selectionType", "selections", "current", "isCheckAll", "isIndeterminate", "checkAllText", "selectedText", "ctxMenuDropdownVisible", "contextMenuFileItem"])) : (vue.openBlock(), vue.createBlock(FileTable, {
          key: 1,
          data: _ctx.data,
          icons: _ctx.icons,
          selectionType: _ctx.selectionType,
          selections: _ctx.selections,
          current: _ctx.current,
          isCheckAll: isCheckAll.value,
          isIndeterminate: isIndeterminate.value,
          nameText: vue.unref(lang).fileName,
          sizeText: vue.unref(lang).fileSize,
          timeText: vue.unref(lang).fileTimestamp,
          sortable: _ctx.sortable,
          sort: _ctx.sort,
          order: _ctx.order,
          columns: _ctx.columns,
          ctxMenuDropdownVisible: ctxMenuDropdownVisible.value,
          contextMenuFileItem: contextMenuFileItem.value,
          onCheckAllChange: handleCheckAllChange,
          onItemClick: handleItemClick,
          onItemCheckChange: handleItemCheckChange,
          onItemContextOpen: handleItemContextOpen,
          onSortChange: handleSortChange
        }, vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1032, ["data", "icons", "selectionType", "selections", "current", "isCheckAll", "isIndeterminate", "nameText", "sizeText", "timeText", "sortable", "sort", "order", "columns", "ctxMenuDropdownVisible", "contextMenuFileItem"])),
        vue.createElementVNode("div", {
          class: "ele-file-list-selector",
          style: vue.normalizeStyle(selectorStyle)
        }, null, 4),
        _ctx.contextMenus ? (vue.openBlock(), vue.createBlock(EleDropdown, vue.mergeProps({
          key: 2,
          persistent: false,
          placement: "bottom-start",
          popperClass: "ele-file-list-item-context",
          validateEvent: false
        }, _ctx.contextMenuProps || {}, {
          ref_key: "ctxMenuDropdownRef",
          ref: ctxMenuDropdownRef,
          componentType: "pro",
          preventContextmenu: true,
          trigger: "click",
          virtualTriggering: true,
          virtualRef: ctxMenuDropdownVirtualRef.value,
          disabled: !ctxMenuDropdownItems.value.length,
          items: ctxMenuDropdownItems.value,
          onCommand: handleItemCtxMenuClick,
          onVisibleChange: handleItemCtxMenuVisible
        }), null, 16, ["virtualRef", "disabled", "items"])) : vue.createCommentVNode("", true)
      ], 32);
    };
  }
});
module.exports = _sfc_main;
