"use strict";
const vue = require("vue");
const SortableJs = require("sortablejs");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const EleDropdown = require("../ele-dropdown/index");
const props = require("./props");
const _hoisted_1 = ["onClick", "onContextmenu"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTabs" },
  __name: "index",
  props: props.tabsProps,
  emits: props.tabsEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    let sortableIns = null;
    let currentSortItemId = null;
    let contextMenuTabItem = null;
    let contextMenuTabName = null;
    const wrapProps = vue.inject(props.TAB_WRAP_KEY, null);
    const [startScrollTimer, _stopScrollTimer, scrollWaiting] = hook.useTimer(320);
    const { bindMousewheel, unbindMousewheel } = hook.useMousewheel((param) => {
      const { e, direction } = param;
      scrollTabs(direction === "up" ? "prev" : "next", () => {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    const { bindTouchEvent, unbindTouchEvent } = hook.useTouchEvent({
      end: (param) => {
        if (param.distanceX && param.distanceX > 80) {
          scrollTabs("prev");
        } else if (param.distanceX && param.distanceX < 80) {
          scrollTabs("next");
        }
      },
      touchstartOptions: { passive: true },
      touchmoveOptions: { passive: true }
    });
    const [startGhostTimer] = hook.useTimer(100);
    const tabRef = vue.ref(null);
    const isOnlyTab = vue.computed(() => wrapProps == null);
    const tabSize = vue.computed(
      () => wrapProps == null ? props$1.size : wrapProps.size
    );
    const tabType = vue.computed(
      () => wrapProps == null ? props$1.type : wrapProps.type
    );
    const tabProps = vue.computed(() => {
      return common.pick(props$1, props.tabPropKeys);
    });
    const ctxMenuDropdownRef = vue.ref(null);
    const ctxMenuDropdownItems = vue.shallowRef([]);
    const ctxMenuDropdownVirtualRef = vue.ref();
    const updateModelValue = (name) => {
      emit("update:modelValue", name);
    };
    const handleContextmenu = (e) => {
      if (!props$1.contextMenu) {
        return;
      }
      const el = e.target;
      if (el && (el.classList.contains("is-icon-close") || el.classList.contains("el-tabs__nav") || el.classList.contains("el-tabs__item"))) {
        e.preventDefault();
      }
    };
    const handleTabClick = (pane, e) => {
      emit("tabClick", pane, e);
    };
    const handleTabChange = (name) => {
      emit("tabChange", name);
    };
    const handleTabRemove = (name) => {
      emit("tabRemove", name);
    };
    const handleTabAdd = () => {
      emit("tabAdd");
    };
    const handleEdit = (name, action) => {
      emit("edit", name, action);
    };
    const handleItemClick = (item, tabName, e) => {
      if (props$1.handleClick) {
        e.stopPropagation();
      }
      emit("tabItemClick", {
        item,
        name: item ? item.name : tabName,
        active: props$1.modelValue
      });
    };
    const handleItemCtxMenuVisible = (visible) => {
      if (visible) {
        emit(
          "tabContextOpen",
          ctxMenuDropdownRef.value,
          contextMenuTabItem,
          contextMenuTabName
        );
      }
    };
    const handleItemCtxMenuClick = (command) => {
      if (contextMenuTabItem != null || contextMenuTabName != null) {
        emit("tabContextMenu", {
          command,
          item: contextMenuTabItem,
          name: contextMenuTabItem ? contextMenuTabItem.name : contextMenuTabName,
          active: props$1.modelValue
        });
      }
    };
    const getContextMenus = (item, tabName) => {
      if (typeof props$1.contextMenus === "function") {
        return props$1.contextMenus(item, tabName);
      }
      return props$1.contextMenus;
    };
    const hideAllDropdown = () => {
      if (ctxMenuDropdownRef.value) {
        ctxMenuDropdownRef.value.handleClose();
      }
    };
    const showItemContextMenu = (item, tabName, itemEl) => {
      if (contextMenuTabItem != null && contextMenuTabItem === item || contextMenuTabName != null && contextMenuTabName === tabName) {
        return;
      }
      hideAllDropdown();
      vue.nextTick(() => {
        contextMenuTabItem = item;
        contextMenuTabName = tabName;
        ctxMenuDropdownItems.value = getContextMenus(item, tabName) || [];
        ctxMenuDropdownVirtualRef.value = itemEl;
        if (props$1.contextMenu && ctxMenuDropdownItems.value.length) {
          vue.nextTick(() => {
            ctxMenuDropdownRef.value && ctxMenuDropdownRef.value.handleOpen();
          });
        }
      });
    };
    const handleItemContextmenu = (item, tabName, e) => {
      const itemEl = e.currentTarget;
      if (!props$1.contextMenu) {
        return;
      }
      if (ctxMenuDropdownVirtualRef.value === itemEl) {
        ctxMenuDropdownItems.value = getContextMenus(item, tabName) || [];
        return;
      }
      e.preventDefault();
      showItemContextMenu(item, tabName, itemEl);
    };
    const getHeaderEl = () => {
      const tabEl = tabRef.value ? tabRef.value.$el : void 0;
      return tabEl ? tabEl.querySelector(".el-tabs__header") : void 0;
    };
    const getNavEl = () => {
      const headerEl = getHeaderEl();
      return headerEl ? headerEl.querySelector(".el-tabs__nav") : void 0;
    };
    const updateActiveBar = () => {
      const el = getNavEl();
      if (el) {
        const bar = el.querySelector(".el-tabs__active-bar");
        if (bar) {
          bar.style.width = "0px";
        }
      }
    };
    const scrollTabs = (direction, done) => {
      const tabEl = getHeaderEl();
      if (tabEl && !scrollWaiting.value) {
        const el = tabEl.querySelector(`.el-tabs__nav-${direction}`);
        if (el && !el.classList.contains("is-disabled")) {
          startScrollTimer();
          done && done();
          el.click();
        }
      }
    };
    const checkSortGhostTab = () => {
      const navEl = getNavEl();
      if (navEl == null) {
        return;
      }
      if (currentSortItemId == null) {
        const el2 = navEl.querySelector(".el-tabs__item.sortable-ghost");
        if (el2 != null) {
          el2.classList.remove("sortable-ghost");
        }
        return;
      }
      const el = navEl.querySelector(`.el-tabs__item[id="${currentSortItemId}"]`);
      if (el != null) {
        el.classList.add("sortable-ghost");
      }
    };
    const bindDragSort = () => {
      unbindDragSort();
      const navEl = getNavEl();
      if (!props$1.sortable || !navEl) {
        return;
      }
      sortableIns = new SortableJs(navEl, {
        draggable: ".el-tabs__item",
        delay: 150,
        onUpdate: ({ oldDraggableIndex, newDraggableIndex }) => {
          if (typeof oldDraggableIndex === "number" && typeof newDraggableIndex === "number") {
            const data = [...props$1.items];
            data.splice(
              newDraggableIndex,
              0,
              data.splice(oldDraggableIndex, 1)[0]
            );
            emit("tabSortChange", data);
          }
        },
        onStart: (e) => {
          currentSortItemId = e.item.getAttribute("id");
          checkSortGhostTab();
          startGhostTimer(() => {
            checkSortGhostTab();
          });
        },
        onEnd: () => {
          currentSortItemId = null;
          checkSortGhostTab();
        },
        onChange: () => {
          checkSortGhostTab();
          startGhostTimer(() => {
            checkSortGhostTab();
          });
        },
        onMove: () => {
          checkSortGhostTab();
          startGhostTimer(() => {
            checkSortGhostTab();
          });
        },
        setData: () => {
        }
      });
    };
    const unbindDragSort = () => {
      sortableIns && sortableIns.destroy();
      sortableIns = null;
      currentSortItemId = null;
    };
    const initMousewheelEvent = () => {
      const el = getHeaderEl();
      if (el != null) {
        unbindMousewheel(el);
        if (props$1.mousewheel) {
          bindMousewheel(el);
        }
      }
    };
    const initTouchEvent = () => {
      const el = getHeaderEl();
      if (el != null) {
        unbindTouchEvent(el);
        if (!props$1.sortable) {
          bindTouchEvent(el);
        }
      }
    };
    if (wrapProps && wrapProps.setTabMethods) {
      wrapProps.setTabMethods({
        triggerTabItemClick: handleItemClick,
        triggerItemContextMenu: handleItemContextmenu
      });
    }
    vue.onMounted(() => {
      initMousewheelEvent();
      initTouchEvent();
      bindDragSort();
    });
    vue.onBeforeUnmount(() => {
      if (wrapProps && wrapProps.setTabMethods) {
        wrapProps.setTabMethods({
          triggerTabItemClick: void 0,
          triggerItemContextMenu: void 0
        });
      }
      contextMenuTabItem = null;
      contextMenuTabName = null;
      const el = getHeaderEl();
      if (el != null) {
        unbindMousewheel(el);
        unbindTouchEvent(el);
      }
      unbindDragSort();
    });
    vue.watch(
      () => props$1.sortable,
      () => {
        bindDragSort();
        initTouchEvent();
      }
    );
    vue.watch(
      () => props$1.mousewheel,
      () => {
        initMousewheelEvent();
      }
    );
    vue.watch(
      () => props$1.contextMenus,
      (ctxMenus) => {
        if (Array.isArray(ctxMenus) && ctxMenuDropdownItems.value !== ctxMenus) {
          ctxMenuDropdownItems.value = ctxMenus;
        }
      },
      { deep: true }
    );
    __expose({
      tabRef,
      ctxMenuDropdownRef,
      hideAllDropdown,
      updateActiveBar,
      scrollTabs
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTabs), vue.mergeProps(tabProps.value, {
        ref_key: "tabRef",
        ref: tabRef,
        type: tabType.value === "card" || tabType.value === "border-card" ? tabType.value : void 0,
        class: ["ele-tabs", [
          { "ele-tabs-wrap": isOnlyTab.value },
          { "is-small": tabSize.value === "small" },
          { "is-large": tabSize.value === "large" },
          { "is-default": !tabType.value || tabType.value === "default" },
          { "is-plain": tabType.value === "plain" },
          { "is-simple": tabType.value === "simple" },
          { "is-indicator": tabType.value === "indicator" },
          { "is-button": tabType.value === "button" },
          { "is-tag": tabType.value === "tag" },
          { "is-center": _ctx.center },
          { "is-sortable": _ctx.sortable },
          { "is-flex-table": _ctx.flexTable && _ctx.flexTable !== "auto" },
          { "is-flex-auto-table": _ctx.flexTable === "auto" }
        ]],
        "onUpdate:modelValue": updateModelValue,
        onTabClick: handleTabClick,
        onTabChange: handleTabChange,
        onTabRemove: handleTabRemove,
        onTabAdd: handleTabAdd,
        onEdit: handleEdit,
        onContextmenu: handleContextmenu
      }), vue.createSlots({
        default: vue.withCtx(() => [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.items, (item, index) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTabPane), vue.mergeProps({
              key: [
                index,
                item.name,
                item.label,
                !!item.closable,
                !!item.disabled,
                !!item.lazy
              ].join("-")
            }, { ref_for: true }, vue.unref(common.omit)(item, ["slot", "meta"])), vue.createSlots({
              label: vue.withCtx(() => [
                vue.createElementVNode("div", {
                  class: "ele-tab-title",
                  onClick: (e) => handleItemClick(item, void 0, e),
                  onContextmenu: (e) => handleItemContextmenu(item, void 0, e)
                }, [
                  vue.renderSlot(_ctx.$slots, "label", {
                    item,
                    label: item.label,
                    active: _ctx.modelValue
                  }, () => [
                    vue.createTextVNode(vue.toDisplayString(item.label), 1)
                  ])
                ], 40, _hoisted_1),
                tabType.value === "simple" || tabType.value === "indicator" ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                  _cache[0] || (_cache[0] = vue.createElementVNode("div", { class: "ele-tab-corner-left" }, null, -1)),
                  _cache[1] || (_cache[1] = vue.createElementVNode("div", { class: "ele-tab-corner-right" }, null, -1))
                ], 64)) : vue.createCommentVNode("", true)
              ]),
              _: 2
            }, [
              item.name && _ctx.$slots[item.slot || item.name] ? {
                name: "default",
                fn: vue.withCtx(() => [
                  vue.renderSlot(_ctx.$slots, item.slot || item.name, { item })
                ]),
                key: "0"
              } : void 0
            ]), 1040);
          }), 128)),
          _ctx.contextMenu ? (vue.openBlock(), vue.createBlock(EleDropdown, vue.mergeProps(
            {
              key: 0,
              triggerKeys: [],
              persistent: false,
              validateEvent: false,
              placement: "bottom-start",
              popperClass: "ele-tab-popup",
              popperOptions: {
                modifiers: [{ name: "offset", options: { offset: [0, 8] } }]
              }
            },
            !_ctx.contextMenu || typeof _ctx.contextMenu == "boolean" ? {} : _ctx.contextMenu,
            {
              ref_key: "ctxMenuDropdownRef",
              ref: ctxMenuDropdownRef,
              componentType: "pro",
              preventContextmenu: true,
              trigger: "contextmenu",
              virtualTriggering: true,
              virtualRef: ctxMenuDropdownVirtualRef.value,
              disabled: !ctxMenuDropdownItems.value.length,
              items: ctxMenuDropdownItems.value,
              onCommand: handleItemCtxMenuClick,
              onVisibleChange: handleItemCtxMenuVisible
            }
          ), null, 16, ["virtualRef", "disabled", "items"])) : vue.createCommentVNode("", true)
        ]),
        _: 2
      }, [
        _ctx.$slots["add-icon"] ? {
          name: "add-icon",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "add-icon")
          ]),
          key: "0"
        } : _ctx.$slots.addIcon ? {
          name: "addIcon",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "addIcon")
          ]),
          key: "1"
        } : void 0
      ]), 1040, ["type", "class"]);
    };
  }
});
module.exports = _sfc_main;
