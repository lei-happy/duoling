"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const common = require("../utils/common");
const EleTooltip = require("../ele-tooltip/index");
const MenuItems = require("./components/menu-items");
const util = require("./util");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleMenus" },
  __name: "index",
  props: props.menusProps,
  emits: props.menusEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const isWebkit = navigator?.userAgent?.includes?.("WebKit");
    const menuRef = vue.ref(null);
    const ellipsisRef = vue.ref(null);
    const sliceIndex = vue.ref(-1);
    const menuItems = vue.shallowRef([]);
    const moreMenuItems = vue.shallowRef([]);
    const tooltipVirtualRef = vue.ref();
    const tooltipContent = vue.ref("");
    const tooltipVisible = vue.ref(false);
    const isHorizontal = vue.computed(() => props$1.mode === "horizontal");
    const isCompact = vue.computed(() => props$1.mode === "compact");
    const collapseTooltipDisabled = vue.computed(
      () => isCompact.value ? !props$1.collapse : props$1.tooltipDisabled
    );
    const menuProps = vue.computed(
      () => common.pick(props$1, props.menuPropKeys)
    );
    const open = (index2) => {
      if (menuRef.value) {
        menuRef.value.open(index2);
      }
    };
    const close = (index2) => {
      if (menuRef.value) {
        menuRef.value.open(index2);
      }
    };
    const updateActiveIndex = (index2) => {
      if (menuRef.value) {
        menuRef.value.updateActiveIndex(index2);
      }
    };
    const hideTooltip = () => {
      tooltipVisible.value = false;
    };
    const triggerTooltip = (e) => {
      if (props$1.textEllipsisTooltip) {
        const itemEl = e.currentTarget?.parentNode;
        if (itemEl) {
          const titleEl = itemEl.querySelector(".ele-menu-title");
          const text = titleEl?.innerText;
          if (text && common.contentIsEllipsis(titleEl, "horizontal")) {
            tooltipVirtualRef.value = itemEl;
            tooltipContent.value = text;
            tooltipVisible.value = true;
            return;
          }
        }
      }
      hideTooltip();
    };
    const handleOpen = (index2, indexPath) => {
      emit("open", index2, indexPath);
    };
    const handleClose = (index2, indexPath) => {
      emit("close", index2, indexPath);
    };
    const handleSelect = (index2, indexPath, item, routerResult) => {
      emit("select", index2, indexPath, item, routerResult);
    };
    const handleItemClick = (item, e, type) => {
      emit("itemClick", item, e, type);
    };
    const handleItemMouseenter = (item, e) => {
      triggerTooltip(e);
      emit("itemMouseenter", item, e);
    };
    const handleItemMouseleave = (item, e) => {
      hideTooltip();
      emit("itemMouseleave", item, e);
    };
    const handleParentMouseenter = (item, e) => {
      triggerTooltip(e);
      emit("parentMouseenter", item, e);
    };
    const handleParentMouseleave = (item, e) => {
      hideTooltip();
      emit("parentMouseleave", item, e);
    };
    const scrollToActive = () => {
      const menuEl = menuRef.value?.$el;
      if (menuEl) {
        const el = menuEl.querySelector(".el-menu-item.is-active") || menuEl.querySelector(".el-sub-menu.is-active");
        if (el) {
          if (typeof el["scrollIntoViewIfNeeded"] === "function") {
            el.scrollIntoViewIfNeeded(true);
          } else {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }
      }
    };
    const { observe, unobserve, computedEllipsis } = util.useMenuEllipsis({
      getMenuEl: () => menuRef.value?.$el,
      getMoreEl: () => ellipsisRef.value?.$el,
      onEllipsis: (index2) => {
        if (sliceIndex.value !== index2) {
          sliceIndex.value = index2;
        }
      }
    });
    vue.onMounted(() => {
      if (props$1.ellipsis && isHorizontal.value && menuRef.value?.$el) {
        computedEllipsis();
        observe();
      }
    });
    vue.watch(
      [
        () => props$1.ellipsis,
        isHorizontal,
        () => menuRef.value?.$el,
        () => props$1.items
      ],
      () => {
        if (props$1.ellipsis && isHorizontal.value && menuRef.value?.$el) {
          observe();
          return;
        }
        unobserve();
        sliceIndex.value = -1;
      }
    );
    vue.watch(
      [() => props$1.items, sliceIndex, isHorizontal],
      () => {
        const { items, moreItems } = util.getMenuItems(
          props$1.items,
          sliceIndex.value,
          isHorizontal.value
        );
        menuItems.value = items;
        moreMenuItems.value = moreItems;
      },
      {
        immediate: true,
        deep: true
      }
    );
    __expose({
      menuRef,
      ellipsisRef,
      open,
      close,
      updateActiveIndex,
      scrollToActive
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElMenu), vue.mergeProps(menuProps.value, {
        ref_key: "menuRef",
        ref: menuRef,
        ellipsis: false,
        mode: isCompact.value ? "vertical" : _ctx.mode,
        collapse: isCompact.value ? true : _ctx.collapse,
        class: ["ele-menu", [
          { "ele-menu-dark": _ctx.theme === "dark" },
          { "is-night": _ctx.theme === "dark" },
          { "ele-menu-colorful": _ctx.colorful },
          { "is-colorful": _ctx.colorful },
          { "is-compact": isCompact.value },
          { "is-compact-collapse": isCompact.value && _ctx.collapse }
        ]],
        onOpen: handleOpen,
        onClose: handleClose,
        onSelect: handleSelect
      }), {
        default: vue.withCtx(() => [
          menuItems.value && menuItems.value.length ? (vue.openBlock(), vue.createBlock(MenuItems, {
            key: 0,
            items: menuItems.value,
            first: true,
            tipDisabled: collapseTooltipDisabled.value,
            parentIsGroup: false,
            theme: _ctx.theme,
            popTheme: _ctx.popupTheme,
            colorful: _ctx.colorful,
            popupColorful: _ctx.popupColorful,
            firstPopClass: _ctx.firstPopperClass,
            webkit: vue.unref(isWebkit),
            onItemClick: handleItemClick,
            onItemMouseenter: handleItemMouseenter,
            onItemMouseleave: handleItemMouseleave,
            onParentMouseenter: handleParentMouseenter,
            onParentMouseleave: handleParentMouseleave
          }, vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1032, ["items", "tipDisabled", "theme", "popTheme", "colorful", "popupColorful", "firstPopClass", "webkit"])) : vue.createCommentVNode("", true),
          moreMenuItems.value && moreMenuItems.value.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElSubMenu), vue.mergeProps({
            key: "sub-menu-more",
            teleported: true
          }, _ctx.ellipsisProps || {}, {
            ref_key: "ellipsisRef",
            ref: ellipsisRef,
            index: "sub-menu-more",
            popperClass: vue.unref(util.getPopperClass)(
              _ctx.ellipsisProps?.popperClass,
              _ctx.theme,
              _ctx.popupTheme,
              _ctx.colorful,
              _ctx.popupColorful,
              _ctx.firstPopperClass,
              true,
              vue.unref(isWebkit)
            ),
            class: "ele-sub-menu-ellipsis"
          }), {
            title: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.guardReactiveProps(_ctx.ellipsisProps?.iconProps || {})), {
                default: vue.withCtx(() => [
                  (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.ellipsisProps?.icon ?? vue.unref(index.EllipsisOutlined)), {
                    style: vue.normalizeStyle(_ctx.ellipsisProps?.iconStyle)
                  }, null, 8, ["style"]))
                ]),
                _: 1
              }, 16)
            ]),
            default: vue.withCtx(() => [
              vue.createVNode(MenuItems, {
                items: moreMenuItems.value,
                first: false,
                tipDisabled: collapseTooltipDisabled.value,
                parentIsGroup: false,
                theme: _ctx.theme,
                popTheme: _ctx.popupTheme,
                colorful: _ctx.colorful,
                popupColorful: _ctx.popupColorful,
                firstPopClass: _ctx.firstPopperClass,
                webkit: vue.unref(isWebkit),
                onItemClick: handleItemClick,
                onItemMouseenter: handleItemMouseenter,
                onItemMouseleave: handleItemMouseleave,
                onParentMouseenter: handleParentMouseenter,
                onParentMouseleave: handleParentMouseleave
              }, vue.createSlots({ _: 2 }, [
                vue.renderList(Object.keys(_ctx.$slots), (name) => {
                  return {
                    name,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                    ])
                  };
                })
              ]), 1032, ["items", "tipDisabled", "theme", "popTheme", "colorful", "popupColorful", "firstPopClass", "webkit"])
            ]),
            _: 3
          }, 16, ["popperClass"])) : vue.createCommentVNode("", true),
          _ctx.textEllipsisTooltip ? (vue.openBlock(), vue.createBlock(EleTooltip, vue.mergeProps({
            key: 2,
            trigger: "click",
            placement: "right",
            fallbackPlacements: [
              "top-end",
              "top",
              "top-start",
              "bottom-end",
              "bottom",
              "bottom-start",
              "left"
            ],
            persistent: false,
            enterable: false,
            triggerKeys: []
          }, _ctx.textEllipsisTooltip === true ? {} : _ctx.textEllipsisTooltip, {
            virtualTriggering: true,
            virtualRef: tooltipVirtualRef.value,
            content: tooltipContent.value,
            visible: tooltipVisible.value
          }), null, 16, ["virtualRef", "content", "visible"])) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 16, ["mode", "collapse", "class"]);
    };
  }
});
module.exports = _sfc_main;
