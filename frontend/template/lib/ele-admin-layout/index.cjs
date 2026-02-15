"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const hook = require("../utils/hook");
const EleMenus = require("../ele-menus/index");
const EleBreadcrumb = require("../ele-breadcrumb/index");
const EleBacktop = require("../ele-backtop/index");
const LayoutSkeleton = require("./components/layout-skeleton");
const LayoutTabs = require("./components/layout-tabs");
const props = require("./props");
const _hoisted_1 = ["src"];
const _hoisted_2 = {
  key: 1,
  class: "ele-admin-tools"
};
const _hoisted_3 = {
  key: 2,
  class: "ele-admin-breadcrumb"
};
const _hoisted_4 = {
  key: 5,
  class: "ele-admin-tools"
};
const _hoisted_5 = ["src"];
const _hoisted_6 = ["src"];
const _hoisted_7 = ["data-id"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleAdminLayout" },
  __name: "index",
  props: props.adminLayoutProps,
  emits: props.adminLayoutEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const tabSlots = ["tabTitle", "tabExtra", "tabHome"];
    const ownSlots = [
      "logo",
      "logoTitle",
      "left",
      "right",
      "center",
      "breadcrumb",
      "top",
      "bottom",
      "boxTop",
      "boxBottom",
      "body",
      ...tabSlots
    ];
    const props$1 = __props;
    const emit = __emit;
    const [startDisableTransitionTimer] = hook.useTimer(100);
    const [startSidebarMenuTimer, stopSidebarMenuTimer] = hook.useTimer(420);
    const [startSideboxMenuTimer, stopSideboxMenuTimer] = hook.useTimer(420);
    const [startHeaderHoverTimer, stopHeaderHoverTimer] = hook.useTimer(300);
    let isHeaderhover = false;
    const sidebarMenuRef = vue.shallowRef(null);
    const sideboxMenuRef = vue.shallowRef(null);
    const contentRef = vue.shallowRef(null);
    const modalsRef = vue.shallowRef(null);
    const isDisableTransition = vue.shallowRef(false);
    const layoutHeight = vue.computed(
      () => typeof props$1.height === "number" ? `${props$1.height}px` : props$1.height
    );
    const isFixedHeader = vue.computed(
      () => !props$1.fixedBody && props$1.fixedHeader
    );
    const isFixedSidebar = vue.computed(
      () => !props$1.fixedBody && props$1.fixedSidebar
    );
    const isTopLayout = vue.computed(() => props$1.layout === "top");
    const isSideLayout = vue.computed(() => props$1.layout === "side");
    const isBoxSidebar = vue.computed(() => props$1.sidebarLayout === "box");
    const isMixSidebar = vue.computed(
      () => !isTopLayout.value && (props$1.sidebarLayout === "mix" || isBoxSidebar.value)
    );
    const isMobile = vue.computed(() => props$1.mobile && !isTopLayout.value);
    const isHeaderLogo = vue.computed(
      () => (props$1.logoInHeader || isTopLayout.value) && !isSideLayout.value && !isMobile.value
    );
    const showHeaderMenus = vue.computed(
      () => isTopLayout.value || props$1.layout === "mix"
    );
    const showHeaderTabs = vue.computed(() => props$1.tabBar === "header");
    const isDarkHeader = vue.computed(() => props$1.headerStyle === "dark");
    const isPrimaryHeader = vue.computed(
      () => props$1.headerStyle === "primary"
    );
    const isButtonTab = vue.computed(() => props$1.tabStyle === "button");
    const isDarkSidebar = vue.computed(() => props$1.sidebarStyle === "dark");
    const isDarkMixSidebar = vue.computed(
      () => props$1.mixSidebarStyle == null ? isMixSidebar.value && !isHeaderLogo.value && isDarkSidebar.value && (isDarkHeader.value || isPrimaryHeader.value) : props$1.mixSidebarStyle === "dark"
    );
    const isGhostHeader = vue.computed(
      () => !isDarkHeader.value && !isPrimaryHeader.value && showHeaderTabs.value && isButtonTab.value
    );
    const isGhostSidebar = vue.computed(
      () => isGhostHeader.value && !isDarkSidebar.value
    );
    const isCollapseSidebar = vue.computed(
      () => !isMobile.value && props$1.collapse
    );
    const isCollapseMobile = vue.computed(
      () => isMobile.value && props$1.collapse
    );
    const getContentEl = () => {
      return contentRef.value;
    };
    const getModalsEl = () => {
      return modalsRef.value;
    };
    const getBodyWrapperEl = () => {
      const contentEl = getContentEl();
      return contentEl?.parentElement;
    };
    const sidebarScrollToActive = () => {
      stopSidebarMenuTimer();
      if (!(props$1.fixedBody || props$1.fixedSidebar) || !props$1.menuScrollToActive || sidebarMenuRef.value == null || isCollapseMobile.value || isMixSidebar.value && isCollapseSidebar.value) {
        return;
      }
      startSidebarMenuTimer(() => {
        sidebarMenuRef.value && sidebarMenuRef.value.scrollToActive();
      });
    };
    const sideboxScrollToActive = () => {
      stopSideboxMenuTimer();
      if (!(props$1.fixedBody || props$1.fixedSidebar) || !props$1.menuScrollToActive || sideboxMenuRef.value == null || isCollapseMobile.value) {
        return;
      }
      startSideboxMenuTimer(() => {
        sideboxMenuRef.value && sideboxMenuRef.value.scrollToActive();
      });
    };
    const updateCollapse = (value) => {
      const collapse = !props$1.collapse;
      if (collapse !== props$1.collapse) {
        emit("update:collapse", collapse);
      }
    };
    const handleLogoClick = (e) => {
      emit("logoClick", e);
    };
    const handleHeadMenuOpen = (index, indexPath) => {
      emit("headMenuOpen", index, indexPath);
    };
    const handleHeadMenuClose = (index, indexPath) => {
      emit("headMenuClose", index, indexPath);
    };
    const handleHeadMenuItemClick = (item, e, type) => {
      emit("headMenuItemClick", item, e, type);
    };
    const handleHeadMenuItemMouseenter = (item, e) => {
      emit("headMenuItemMouseenter", item, e);
      handleHeadMouseenter(e);
    };
    const handleHeadMenuItemMouseleave = (item, e) => {
      emit("headMenuItemMouseleave", item, e);
      handleHeadMouseleave(e);
    };
    const handleHeadMouseenter = (e) => {
      stopHeaderHoverTimer();
      if (!isHeaderhover) {
        isHeaderhover = true;
        emit("headMouseenter", e);
      }
    };
    const handleHeadMouseleave = (e) => {
      startHeaderHoverTimer(() => {
        isHeaderhover = false;
        emit("headMouseleave", e);
      });
    };
    const handleBoxMenuItemClick = (item, e, type) => {
      emit("boxMenuItemClick", item, e, type);
    };
    const handleBoxMenuItemMouseenter = (item, e) => {
      emit("boxMenuItemMouseenter", item, e);
    };
    const handleBoxMenuItemMouseleave = (item, e) => {
      emit("boxMenuItemMouseleave", item, e);
    };
    const handleBoxMouseEnter = (e) => {
      emit("boxMouseenter", e);
    };
    const handleBoxMouseLeave = (e) => {
      emit("boxMouseleave", e);
    };
    const handleSideMenuOpen = (index, indexPath) => {
      emit("sideMenuOpen", index, indexPath);
    };
    const handleSideMenuClose = (index, indexPath) => {
      emit("sideMenuClose", index, indexPath);
    };
    const handleSideMenuItemClick = (item, e, type) => {
      emit("sideMenuItemClick", item, e, type);
    };
    const handleSideMouseEnter = (e) => {
      emit("sideMouseenter", e);
    };
    const handleSideMouseLeave = (e) => {
      emit("sideMouseleave", e);
    };
    const handleTabClick = (option) => {
      emit("tabClick", option);
    };
    const handleTabRemove = (name, closeable) => {
      if (closeable == null || closeable) {
        emit("tabRemove", name);
      }
    };
    const handleTabContextMenu = (option) => {
      emit("tabContextMenu", option);
    };
    const handleTabSortChange = (data) => {
      emit("tabSortChange", data);
    };
    const layoutProvide = vue.shallowReactive({
      layout: props$1.layout,
      maximized: props$1.maximized,
      fixedHeader: isFixedHeader.value,
      fixedBody: props$1.fixedBody,
      modalsEl: null,
      getModalsEl,
      getBodyWrapperEl
    });
    vue.provide(props.LAYOUT_KEY, layoutProvide);
    vue.watch(
      [
        () => props$1.layout,
        () => props$1.sidebarLayout,
        () => props$1.fixedSidebar,
        () => props$1.fixedBody,
        () => props$1.logoInHeader,
        () => props$1.maximized,
        isFixedHeader,
        isMobile
      ],
      () => {
        isDisableTransition.value = true;
        startDisableTransitionTimer(() => {
          isDisableTransition.value = false;
        });
        if (layoutProvide.layout !== props$1.layout) {
          layoutProvide.layout = props$1.layout;
        }
        if (layoutProvide.maximized !== props$1.maximized) {
          layoutProvide.maximized = props$1.maximized;
        }
        if (layoutProvide.fixedHeader !== isFixedHeader.value) {
          layoutProvide.fixedHeader = isFixedHeader.value;
        }
        if (layoutProvide.fixedBody !== props$1.fixedBody) {
          layoutProvide.fixedBody = props$1.fixedBody;
        }
      }
    );
    vue.watch([() => props$1.sidebarActive, () => props$1.collapse], () => {
      vue.nextTick(() => {
        sidebarScrollToActive();
      });
    });
    vue.watch([() => props$1.sideboxActive, () => props$1.compact], () => {
      vue.nextTick(() => {
        sideboxScrollToActive();
      });
    });
    vue.onMounted(() => {
      sideboxScrollToActive();
      sidebarScrollToActive();
      const modalsEl = getModalsEl();
      layoutProvide.modalsEl = modalsEl;
      const contentEl = getContentEl();
      if (contentEl != null && modalsEl != null) {
        emit("contentMounted", contentEl, modalsEl);
      }
    });
    __expose({
      sidebarMenuRef,
      sideboxMenuRef,
      getContentEl
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(LayoutSkeleton, {
        isHeaderLogo: isHeaderLogo.value,
        class: vue.normalizeClass([
          { "is-fixed-body": _ctx.fixedBody },
          { "is-transition-disabled": isDisableTransition.value },
          { "is-maximized": _ctx.maximized },
          { "is-expanded": _ctx.maximized === "expanded" },
          { "is-mobile": isMobile.value },
          { "is-collapse": isCollapseMobile.value }
        ]),
        style: vue.normalizeStyle({
          minHeight: layoutHeight.value,
          height: _ctx.fixedBody ? layoutHeight.value : void 0
        })
      }, {
        head: vue.withCtx(() => [
          !isSideLayout.value ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            class: vue.normalizeClass(["ele-admin-header", [
              { "is-dark": isDarkHeader.value },
              { "is-primary": isPrimaryHeader.value },
              { "is-ghost": isGhostHeader.value },
              { "show-divider": _ctx.tabBar && !showHeaderTabs.value && !isButtonTab.value },
              { "is-fixed": isFixedHeader.value }
            ]]),
            style: vue.normalizeStyle(_ctx.headerCustomStyle),
            onMouseenter: handleHeadMouseenter,
            onMouseleave: handleHeadMouseleave
          }, [
            isHeaderLogo.value && (_ctx.logoSrc || _ctx.logoTitle || _ctx.$slots.logo || _ctx.$slots.logoTitle) ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-admin-logo",
              style: vue.normalizeStyle(_ctx.logoStyle),
              onClick: handleLogoClick
            }, [
              _ctx.logoSrc || _ctx.$slots.logo ? vue.renderSlot(_ctx.$slots, "logo", { key: 0 }, () => [
                vue.createElementVNode("img", { src: _ctx.logoSrc }, null, 8, _hoisted_1)
              ]) : vue.createCommentVNode("", true),
              _ctx.logoTitle || _ctx.$slots.logoTitle ? vue.renderSlot(_ctx.$slots, "logoTitle", { key: 1 }, () => [
                vue.createElementVNode("h1", null, vue.toDisplayString(_ctx.logoTitle), 1)
              ]) : vue.createCommentVNode("", true)
            ], 4)) : vue.createCommentVNode("", true),
            _ctx.$slots.left ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
              vue.renderSlot(_ctx.$slots, "left")
            ])) : vue.createCommentVNode("", true),
            _ctx.breadcrumb ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_3, [
              vue.renderSlot(_ctx.$slots, "breadcrumb", {}, () => [
                _ctx.levels && _ctx.levels.length ? (vue.openBlock(), vue.createBlock(EleBreadcrumb, vue.mergeProps({ key: 0 }, _ctx.breadcrumb === true ? {} : _ctx.breadcrumb, { items: _ctx.levels }), null, 16, ["items"])) : vue.createCommentVNode("", true)
              ])
            ])) : vue.createCommentVNode("", true),
            vue.renderSlot(_ctx.$slots, "center"),
            !showHeaderTabs.value || showHeaderMenus.value ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 3,
              class: "ele-admin-menus",
              style: vue.normalizeStyle(_ctx.headerMenusStyle)
            }, [
              showHeaderMenus.value && _ctx.headerMenus ? (vue.openBlock(), vue.createBlock(EleMenus, vue.mergeProps({
                key: 0,
                mode: "horizontal",
                theme: isDarkHeader.value || isPrimaryHeader.value ? "dark" : "light",
                popupTheme: isDarkHeader.value ? "dark" : "light",
                defaultActive: _ctx.headerActive
              }, _ctx.headerMenuProps || {}, {
                items: _ctx.headerMenus,
                onOpen: handleHeadMenuOpen,
                onClose: handleHeadMenuClose,
                onItemClick: handleHeadMenuItemClick,
                onItemMouseenter: handleHeadMenuItemMouseenter,
                onItemMouseleave: handleHeadMenuItemMouseleave
              }), vue.createSlots({ _: 2 }, [
                _ctx.headerIconSlot && !ownSlots.includes(_ctx.headerIconSlot) && _ctx.$slots[_ctx.headerIconSlot] ? {
                  name: "icon",
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, _ctx.headerIconSlot, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ]),
                  key: "0"
                } : void 0,
                _ctx.headerTitleSlot && !ownSlots.includes(_ctx.headerTitleSlot) && _ctx.$slots[_ctx.headerTitleSlot] ? {
                  name: "title",
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, _ctx.headerTitleSlot, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ]),
                  key: "1"
                } : void 0
              ]), 1040, ["theme", "popupTheme", "defaultActive", "items"])) : vue.createCommentVNode("", true)
            ], 4)) : vue.createCommentVNode("", true),
            showHeaderTabs.value ? (vue.openBlock(), vue.createBlock(LayoutTabs, {
              key: 4,
              tabs: _ctx.tabs,
              active: _ctx.tabActive,
              fixedHome: _ctx.fixedHome,
              homePath: _ctx.homePath,
              isHome: _ctx.isHome,
              tabStyle: _ctx.tabStyle,
              tabContextMenu: _ctx.tabContextMenu,
              tabContextMenus: _ctx.tabContextMenus,
              tabSortable: _ctx.tabSortable,
              class: vue.normalizeClass([{ "is-fixed-home": _ctx.fixedHome }]),
              style: vue.normalizeStyle(_ctx.tabsCustomStyle),
              onTabClick: handleTabClick,
              onTabRemove: handleTabRemove,
              onTabContextMenu: handleTabContextMenu,
              onTabSortChange: handleTabSortChange
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter(
                (k) => tabSlots.includes(k)
              ), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["tabs", "active", "fixedHome", "homePath", "isHome", "tabStyle", "tabContextMenu", "tabContextMenus", "tabSortable", "class", "style"])) : vue.createCommentVNode("", true),
            _ctx.$slots.right ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_4, [
              vue.renderSlot(_ctx.$slots, "right")
            ])) : vue.createCommentVNode("", true)
          ], 38)) : vue.createCommentVNode("", true)
        ]),
        side: vue.withCtx(() => [
          !isTopLayout.value ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            class: vue.normalizeClass(["ele-admin-side", [
              { "is-fixed": isFixedSidebar.value },
              { "show-placeholder": isFixedSidebar.value && isHeaderLogo.value },
              { "is-collapse": !isMobile.value && !isBoxSidebar.value && isCollapseSidebar.value },
              { "is-mix": !isMobile.value && !isBoxSidebar.value && isMixSidebar.value },
              { "is-compact": !isMobile.value && _ctx.compact },
              { "is-box": !isMobile.value && isBoxSidebar.value }
            ]]),
            style: vue.normalizeStyle([
              { height: isFixedSidebar.value ? layoutHeight.value : void 0 },
              _ctx.sideCustomStyle
            ])
          }, [
            isMixSidebar.value ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: vue.normalizeClass(["ele-admin-sidebox", [
                { "is-dark": isDarkSidebar.value },
                { "is-ghost": isGhostSidebar.value },
                { "show-divider": !isCollapseSidebar.value && !isBoxSidebar.value },
                { "is-compact": _ctx.compact }
              ]]),
              style: vue.normalizeStyle(_ctx.sideboxCustomStyle),
              onMouseenter: handleBoxMouseEnter,
              onMouseleave: handleBoxMouseLeave
            }, [
              !isHeaderLogo.value && (_ctx.logoSrc || _ctx.$slots.logo) ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 0,
                class: "ele-admin-logo",
                style: vue.normalizeStyle(_ctx.logoStyle),
                onClick: handleLogoClick
              }, [
                vue.renderSlot(_ctx.$slots, "logo", {}, () => [
                  vue.createElementVNode("img", { src: _ctx.logoSrc }, null, 8, _hoisted_5)
                ])
              ], 4)) : vue.createCommentVNode("", true),
              vue.renderSlot(_ctx.$slots, "boxTop"),
              vue.createVNode(vue.unref(elementPlus.ElScrollbar), {
                class: "ele-admin-menus",
                style: vue.normalizeStyle(_ctx.sideboxMenusStyle)
              }, {
                default: vue.withCtx(() => [
                  _ctx.sideboxMenus ? (vue.openBlock(), vue.createBlock(EleMenus, vue.mergeProps({
                    key: 0,
                    ref_key: "sideboxMenuRef",
                    ref: sideboxMenuRef,
                    mode: "compact",
                    uniqueOpened: true,
                    collapseTransition: false,
                    theme: _ctx.sidebarStyle,
                    defaultActive: _ctx.sideboxActive,
                    collapse: _ctx.compact
                  }, _ctx.sideboxMenuProps || {}, {
                    items: _ctx.sideboxMenus,
                    onItemClick: handleBoxMenuItemClick,
                    onItemMouseenter: handleBoxMenuItemMouseenter,
                    onItemMouseleave: handleBoxMenuItemMouseleave
                  }), vue.createSlots({ _: 2 }, [
                    _ctx.sideboxIconSlot && !ownSlots.includes(_ctx.sideboxIconSlot) && _ctx.$slots[_ctx.sideboxIconSlot] ? {
                      name: "icon",
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, _ctx.sideboxIconSlot, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ]),
                      key: "0"
                    } : void 0,
                    _ctx.sideboxTitleSlot && !ownSlots.includes(_ctx.sideboxTitleSlot) && _ctx.$slots[_ctx.sideboxTitleSlot] ? {
                      name: "title",
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, _ctx.sideboxTitleSlot, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ]),
                      key: "1"
                    } : void 0
                  ]), 1040, ["theme", "defaultActive", "collapse", "items"])) : vue.createCommentVNode("", true)
                ]),
                _: 3
              }, 8, ["style"]),
              vue.renderSlot(_ctx.$slots, "boxBottom")
            ], 38)) : vue.createCommentVNode("", true),
            !isBoxSidebar.value ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 1,
              class: vue.normalizeClass(["ele-admin-sidebar", [
                { "is-dark": isMixSidebar.value ? isDarkMixSidebar.value : isDarkSidebar.value },
                { "is-ghost": isGhostSidebar.value },
                { "is-mix": isMixSidebar.value },
                { "is-collapse": isCollapseSidebar.value },
                {
                  "show-divider": isMixSidebar.value && isDarkMixSidebar.value && isDarkSidebar.value
                }
              ]]),
              style: vue.normalizeStyle(_ctx.sidebarCustomStyle),
              onMouseenter: handleSideMouseEnter,
              onMouseleave: handleSideMouseLeave
            }, [
              isMixSidebar.value ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                !isHeaderLogo.value && (_ctx.logoTitle || _ctx.$slots.logoTitle) ? (vue.openBlock(), vue.createElementBlock("div", {
                  key: 0,
                  class: "ele-admin-logo-title",
                  style: vue.normalizeStyle(_ctx.logoTitleStyle)
                }, [
                  vue.renderSlot(_ctx.$slots, "logoTitle", {}, () => [
                    vue.createElementVNode("h1", null, vue.toDisplayString(_ctx.logoTitle), 1)
                  ])
                ], 4)) : vue.createCommentVNode("", true)
              ], 64)) : !isHeaderLogo.value && (_ctx.logoSrc || _ctx.logoTitle || _ctx.$slots.logo || _ctx.$slots.logoTitle) ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 1,
                class: "ele-admin-logo",
                style: vue.normalizeStyle(_ctx.logoStyle),
                onClick: handleLogoClick
              }, [
                _ctx.logoSrc || _ctx.$slots.logo ? vue.renderSlot(_ctx.$slots, "logo", { key: 0 }, () => [
                  vue.createElementVNode("img", { src: _ctx.logoSrc }, null, 8, _hoisted_6)
                ]) : vue.createCommentVNode("", true),
                _ctx.logoTitle || _ctx.$slots.logoTitle ? vue.renderSlot(_ctx.$slots, "logoTitle", { key: 1 }, () => [
                  vue.createElementVNode("h1", null, vue.toDisplayString(_ctx.logoTitle), 1)
                ]) : vue.createCommentVNode("", true)
              ], 4)) : vue.createCommentVNode("", true),
              vue.renderSlot(_ctx.$slots, "top"),
              vue.createVNode(vue.unref(elementPlus.ElScrollbar), {
                class: "ele-admin-menus",
                style: vue.normalizeStyle(_ctx.sidebarMenusStyle)
              }, {
                default: vue.withCtx(() => [
                  _ctx.sidebarMenus ? (vue.openBlock(), vue.createBlock(EleMenus, vue.mergeProps({
                    key: 0,
                    ref_key: "sidebarMenuRef",
                    ref: sidebarMenuRef,
                    uniqueOpened: true,
                    collapseTransition: false,
                    theme: isMixSidebar.value ? isDarkMixSidebar.value ? "dark" : void 0 : _ctx.sidebarStyle,
                    defaultActive: _ctx.sidebarActive,
                    collapse: isMixSidebar.value ? false : isCollapseSidebar.value
                  }, _ctx.sidebarMenuProps || {}, {
                    items: _ctx.sidebarMenus,
                    onOpen: handleSideMenuOpen,
                    onClose: handleSideMenuClose,
                    onItemClick: handleSideMenuItemClick
                  }), vue.createSlots({ _: 2 }, [
                    _ctx.sidebarIconSlot && !ownSlots.includes(_ctx.sidebarIconSlot) && _ctx.$slots[_ctx.sidebarIconSlot] ? {
                      name: "icon",
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, _ctx.sidebarIconSlot, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ]),
                      key: "0"
                    } : void 0,
                    _ctx.sidebarTitleSlot && !ownSlots.includes(_ctx.sidebarTitleSlot) && _ctx.$slots[_ctx.sidebarTitleSlot] ? {
                      name: "title",
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, _ctx.sidebarTitleSlot, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ]),
                      key: "1"
                    } : void 0
                  ]), 1040, ["theme", "defaultActive", "collapse", "items"])) : vue.createCommentVNode("", true)
                ]),
                _: 3
              }, 8, ["style"]),
              vue.renderSlot(_ctx.$slots, "bottom")
            ], 38)) : vue.createCommentVNode("", true)
          ], 6)) : vue.createCommentVNode("", true)
        ]),
        tabs: vue.withCtx(({ param }) => [
          _ctx.tabBar && !showHeaderTabs.value ? (vue.openBlock(), vue.createBlock(LayoutTabs, {
            key: 0,
            tabs: _ctx.tabs,
            active: _ctx.tabActive,
            fixedHome: _ctx.fixedHome,
            homePath: _ctx.homePath,
            isHome: _ctx.isHome,
            tabStyle: _ctx.tabStyle,
            tabContextMenu: _ctx.tabContextMenu,
            tabContextMenus: _ctx.tabContextMenus,
            tabSortable: _ctx.tabSortable,
            class: vue.normalizeClass([
              { "is-fixed-home": _ctx.fixedHome },
              { "is-fixed": isFixedHeader.value },
              { "is-fixed-top": isFixedHeader.value && (isSideLayout.value || _ctx.maximized) }
            ]),
            style: vue.normalizeStyle(_ctx.tabsCustomStyle),
            onTabClick: handleTabClick,
            onTabRemove: (name) => handleTabRemove(name, !!param?.label),
            onTabContextMenu: handleTabContextMenu,
            onTabSortChange: handleTabSortChange
          }, vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter(
              (k) => tabSlots.includes(k)
            ), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1032, ["tabs", "active", "fixedHome", "homePath", "isHome", "tabStyle", "tabContextMenu", "tabContextMenus", "tabSortable", "class", "style", "onTabRemove"])) : vue.createCommentVNode("", true)
        ]),
        body: vue.withCtx(({ param }) => [
          vue.createElementVNode("div", {
            ref_key: "contentRef",
            ref: contentRef,
            class: "ele-admin-content",
            style: vue.normalizeStyle(_ctx.contentCustomStyle)
          }, [
            vue.renderSlot(_ctx.$slots, "default")
          ], 4),
          vue.renderSlot(_ctx.$slots, "body"),
          _ctx.backTop ? (vue.openBlock(), vue.createBlock(EleBacktop, vue.mergeProps({
            key: 0,
            target: _ctx.fixedBody && contentRef.value ? contentRef.value : void 0,
            style: _ctx.fixedBody ? { position: "absolute" } : void 0
          }, _ctx.backTop === true ? {} : _ctx.backTop), null, 16, ["target", "style"])) : vue.createCommentVNode("", true),
          vue.createElementVNode("div", {
            ref_key: "modalsRef",
            ref: modalsRef,
            class: "ele-admin-modals",
            "data-id": param?.key
          }, null, 8, _hoisted_7)
        ]),
        default: vue.withCtx(() => [
          vue.createElementVNode("div", {
            class: "ele-admin-mask",
            onClick: _cache[0] || (_cache[0] = ($event) => updateCollapse())
          })
        ]),
        _: 3
      }, 8, ["isHeaderLogo", "class", "style"]);
    };
  }
});
module.exports = _sfc_main;
