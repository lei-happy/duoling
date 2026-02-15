"use strict";
const vue = require("vue");
const vueRouter = require("vue-router");
const index = require("../icons/index");
const hook = require("../utils/hook");
const common = require("../utils/common");
const EleModalRender = require("../ele-modal-render/index");
const util = require("../ele-modal-render/util");
const IframeGroup = require("./components/iframe-group");
const util$1 = require("./util");
const props = require("./props");
const EleAdminLayout = require("../ele-admin-layout/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleProLayout" },
  __name: "index",
  props: props.proLayoutProps,
  emits: props.proLayoutEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { currentRoute, push } = vueRouter.useRouter();
    const {
      modals,
      openModal,
      closeModal,
      closeAllModal,
      removeModal,
      updateModalVisible,
      updateModalProps
    } = util.useModalRenderProvider();
    const [startTimer, stopTimer] = hook.useTimer(() => props$1.menuHoverTimeout);
    const state = { navData: [], sideData: [], boxData: [] };
    const layoutRef = vue.ref(null);
    const menuData = vue.shallowRef([]);
    const navData = vue.shallowRef([]);
    const navActive = vue.ref();
    const sideData = vue.shallowRef([]);
    const sideActive = vue.ref();
    const boxData = vue.shallowRef([]);
    const boxActive = vue.ref();
    const tabData = vue.shallowRef([]);
    const tabActive = vue.ref();
    const levelData = vue.shallowRef([]);
    const mobile = vue.ref(false);
    const homeMenuPath = vue.ref();
    const isHome = vue.ref(false);
    const hideHeader = vue.ref(false);
    const hideSidebar = vue.ref(false);
    const hideSidebox = vue.ref(false);
    const hideTabs = vue.ref(false);
    const hideFooter = vue.ref(false);
    const computedNavigation = () => {
      let nav = "default";
      if (hideHeader.value) {
        nav = "side";
      } else if (hideSidebar.value && hideSidebox.value) {
        nav = "top";
      } else if (props$1.layout === "top" || props$1.layout === "mix") {
        nav = props$1.layout;
      }
      if (mobile.value && (nav === "top" || nav === "mix")) {
        nav = "default";
      }
      return nav;
    };
    const computedSideNavigation = () => {
      if (!hideSidebox.value && hideSidebar.value) {
        return "box";
      }
      return props$1.sidebarLayout === "mix" ? "mix" : "default";
    };
    const navigation = vue.ref(computedNavigation());
    const sideNavigation = vue.ref(computedSideNavigation());
    const layoutHeaders = vue.computed(() => {
      const navRoute = props$1.navTrigger !== "click" && props$1.navTrigger !== "hover";
      return util$1.getMenuItems(navData.value, navRoute);
    });
    const layoutSidebars = vue.computed(() => {
      const menuRoute = props$1.itemTrigger !== "click" && props$1.itemTrigger !== "hover";
      return util$1.getMenuItems(sideData.value, menuRoute);
    });
    const layoutSideboxs = vue.computed(() => {
      const boxRoute = props$1.boxTrigger !== "click" && props$1.boxTrigger !== "hover";
      return util$1.getMenuItems(boxData.value, boxRoute);
    });
    const layoutTabs = vue.computed(() => {
      const data = props$1.fixedHome ? tabData.value.filter((t) => !t.home) : tabData.value;
      const onlyOne = !props$1.fixedHome && data.length === 1;
      return data.map((d) => {
        return {
          name: d.key,
          label: d.title,
          closable: onlyOne && d.home ? false : d.closable,
          meta: {
            path: d.path,
            fullPath: d.fullPath,
            home: d.home,
            components: d.components,
            refresh: d.refresh,
            ...d.meta || {}
          }
        };
      });
    });
    const layoutLevels = vue.computed(() => {
      const data = [];
      if (!isHome.value) {
        const to = homeMenuPath.value;
        const is = { transform: "scale(1.13)", transformOrigin: "8px -2px" };
        data.push({
          key: to,
          to,
          icon: vue.markRaw(index.HomeOutlined),
          iconStyle: is
        });
      }
      levelData.value.forEach((d) => {
        data.push({ key: d.path, title: d.title });
      });
      return data;
    });
    const routeLayout = vue.computed(() => {
      if (navigation.value !== "top" && navigation.value !== "side" && !layoutSidebars.value.length && !layoutSideboxs.value.length) {
        return "top";
      }
      return navigation.value;
    });
    const routeSideType = vue.computed(() => {
      if (sideNavigation.value === "mix" && !layoutSidebars.value.length) {
        return "box";
      }
      return sideNavigation.value;
    });
    const isBoxSide = vue.computed(() => routeSideType.value === "box");
    const routeTabBar = vue.computed(() => {
      return hideTabs.value ? false : props$1.tabBar;
    });
    const routeMaximized = vue.computed(() => {
      const max = props$1.maximized;
      if (hideHeader.value && hideSidebar.value && hideSidebox.value && !max) {
        return true;
      }
      return max === true && props$1.expanded ? "expanded" : max;
    });
    const sidebar = vue.computed(() => {
      return routeLayout.value !== "top" && !isBoxSide.value || mobile.value;
    });
    const breadcrumbProps = vue.computed(() => {
      if (!props$1.breadcrumb || props$1.breadcrumbSeparator == null) {
        return props$1.breadcrumb;
      }
      if (props$1.breadcrumb === true) {
        return { separator: props$1.breadcrumbSeparator };
      }
      return { separator: props$1.breadcrumbSeparator, ...props$1.breadcrumb };
    });
    const backTopProps = vue.computed(() => {
      const backTop = props$1.backTop;
      const r = props$1.backTopRight;
      const b = props$1.backTopBottom;
      const vh = props$1.backTopVisibilityHeight;
      const t = props$1.backTopTarget;
      if (!backTop || vh == null && r == null && b == null && t == null) {
        return backTop;
      }
      const prop = backTop === true ? {} : { ...backTop };
      if (vh != null && prop.visibilityHeight == null) {
        prop.visibilityHeight = vh;
      }
      if (r != null && prop.right == null) {
        prop.right = r;
      }
      if (b != null && prop.bottom == null) {
        prop.bottom = b;
      }
      if (t != null && prop.target == null) {
        prop.target = t;
      }
      return prop;
    });
    const navMenuProps = vue.computed(() => {
      const mProps = props$1.headerMenuProps;
      const e = props$1.ellipsis;
      const ep = props$1.ellipsisProps;
      const mt = props$1.menuTrigger;
      const mtet = props$1.menuTextEllipsisTooltip;
      if (e == null && ep == null && mt == null && mtet == null) {
        return mProps;
      }
      const prop = mProps == null ? {} : { ...mProps };
      if (e != null && prop.ellipsis == null) {
        prop.ellipsis = e;
      }
      if (ep != null && prop.ellipsisProps == null) {
        prop.ellipsisProps = ep;
      }
      if (mt != null && prop.menuTrigger == null) {
        prop.menuTrigger = mt;
      }
      if (mtet != null && prop.textEllipsisTooltip == null) {
        prop.textEllipsisTooltip = mtet;
      }
      return prop;
    });
    const sideMenuProps = vue.computed(() => {
      const mProps = props$1.sidebarMenuProps;
      const s = props$1.sidebarOpeneds;
      const u = props$1.uniqueOpened;
      const c = props$1.colorfulIcon;
      const t = props$1.tooltipEffect;
      const mtet = props$1.menuTextEllipsisTooltip;
      if (s == null && u == null && c == null && t == null && mtet == null) {
        return mProps;
      }
      const prop = mProps == null ? {} : { ...mProps };
      if (s != null && prop.defaultOpeneds == null) {
        prop.defaultOpeneds = s;
      }
      if (u != null && prop.uniqueOpened == null) {
        prop.uniqueOpened = u;
      }
      if (c != null && prop.colorful == null) {
        prop.colorful = c;
      }
      if (t != null && prop.popperEffect == null) {
        prop.popperEffect = t;
      }
      if (mtet != null && prop.textEllipsisTooltip == null) {
        prop.textEllipsisTooltip = mtet;
      }
      return prop;
    });
    const boxMenuProps = vue.computed(() => {
      const mProps = props$1.sideboxMenuProps;
      const ci = props$1.colorfulIcon;
      const te = props$1.tooltipEffect;
      const mtet = props$1.menuTextEllipsisTooltip;
      if (ci == null && te == null && mtet == null) {
        return mProps;
      }
      const prop = mProps == null ? {} : { ...mProps };
      if (ci != null && prop.popupColorful == null) {
        prop.popupColorful = ci;
      }
      if (te != null && prop.popperEffect == null) {
        prop.popperEffect = te;
      }
      if (mtet != null && prop.textEllipsisTooltip == null) {
        prop.textEllipsisTooltip = mtet;
      }
      return prop;
    });
    const updateNavigation = () => {
      const value = computedNavigation();
      if (navigation.value !== value) {
        navigation.value = value;
        return true;
      }
    };
    const updateSideNavigation = () => {
      const value = computedSideNavigation();
      if (sideNavigation.value !== value) {
        sideNavigation.value = value;
        return true;
      }
    };
    const resetMenuState = () => {
      if (!state.isHover) {
        return;
      }
      startTimer(() => {
        state.isHover = false;
        const isMixSide = sideNavigation.value === "mix" || sideNavigation.value === "box";
        if (navActive.value !== state.navActive) {
          navActive.value = state.navActive;
          if (isMixSide) {
            boxData.value = state.boxData;
          } else {
            sideData.value = state.sideData;
          }
        }
        if (isMixSide && boxActive.value !== state.boxActive) {
          boxActive.value = state.boxActive;
          sideData.value = state.sideData;
        }
      });
    };
    const updateCollapse = (collapse) => {
      if (collapse !== props$1.collapse) {
        emit("update:collapse", collapse);
      }
    };
    const updateMaximized = (maximized) => {
      if (maximized !== props$1.maximized) {
        emit("update:maximized", maximized);
      }
    };
    const handleLogoClick = (e) => {
      emit("logoClick", isHome.value, e);
    };
    const handleHeadMenuOpen = (index2, indexPath) => {
      emit("headMenuOpen", index2, indexPath);
    };
    const handleHeadMenuClose = (index2, indexPath) => {
      emit("headMenuClose", index2, indexPath);
    };
    const handleHeadMenuItemClick = (item, e, type) => {
      const path = item.index;
      const trigger = props$1.navTrigger;
      if (!path || trigger !== "click" && trigger !== "hover") {
        return;
      }
      if (common.isExternalLink(path)) {
        e.stopPropagation();
        if (props$1.beforeClick && props$1.beforeClick(item, e) === false) {
          return;
        }
        if (type === "parent" || type === "group") {
          return;
        }
        window.open(path);
        return;
      }
      const childMenus = util$1.getActiveChilds(navData.value, path, "tempChildren");
      const isChild = !childMenus.some((d) => !d.meta?.hide);
      if (trigger !== "click" && !isChild) {
        e.stopPropagation();
        return;
      }
      if (props$1.beforeClick && props$1.beforeClick(item, e) === false) {
        return;
      }
      if (type === "parent" || type === "group") {
        return;
      }
      if (isChild && path !== vue.unref(currentRoute).fullPath) {
        push(path);
        return;
      }
      e.stopPropagation();
      if (navActive.value !== path) {
        navActive.value = path;
        const isMixSide = sideNavigation.value === "mix" || sideNavigation.value === "box";
        const isCollapse = sideNavigation.value === "box" || props$1.collapse && !mobile.value;
        if (!isMixSide) {
          sideData.value = childMenus;
          return;
        }
        boxData.value = childMenus.map((d) => {
          return {
            ...d,
            children: isCollapse ? d.children : void 0,
            tempChildren: d.children
          };
        });
      }
    };
    const handleHeadMenuItemMouseenter = (item, e) => {
      if (navigation.value !== "mix") {
        return;
      }
      stopTimer();
      const path = item.index;
      const trigger = props$1.navTrigger;
      if (trigger !== "hover" || !path) {
        return;
      }
      if (!common.isExternalLink(path) && props$1.beforeClick && props$1.beforeClick(item, e) === false) {
        return;
      }
      const temp = util$1.getActiveChilds(navData.value, path, "tempChildren");
      if (navActive.value !== path) {
        state.isHover = true;
        navActive.value = temp.some((d) => !d.meta?.hide) ? path : void 0;
        const isMixSide = sideNavigation.value === "mix" || sideNavigation.value === "box";
        if (!isMixSide) {
          sideData.value = temp;
          return;
        }
        boxData.value = temp.map((d) => {
          return {
            ...d,
            children: props$1.collapse ? d.children : void 0,
            tempChildren: d.children
          };
        });
      }
    };
    const handleHeadMouseenter = () => {
      stopTimer();
    };
    const handleHeadMouseleave = () => {
      resetMenuState();
    };
    const handleBoxMenuItemClick = (item, e, type) => {
      const path = item.index;
      const trigger = props$1.boxTrigger;
      if (!path || trigger !== "click" && trigger !== "hover") {
        return;
      }
      if (common.isExternalLink(path)) {
        e.stopPropagation();
        if (props$1.beforeClick && props$1.beforeClick(item, e) === false) {
          return;
        }
        if (type === "parent" || type === "group") {
          return;
        }
        window.open(path);
        return;
      }
      if (props$1.collapse) {
        if (props$1.beforeClick && props$1.beforeClick(item, e) === false) {
          return;
        }
        if (type === "parent" || type === "group") {
          return;
        }
        if (path !== vue.unref(currentRoute).fullPath) {
          push(path);
        }
        return;
      }
      const childMenus = util$1.getActiveChilds(boxData.value, path, "tempChildren");
      const isChild = !childMenus.some((d) => !d.meta?.hide);
      if (trigger !== "click" && !isChild) {
        e.stopPropagation();
        return;
      }
      if (props$1.beforeClick && props$1.beforeClick(item, e) === false) {
        return;
      }
      if (type === "parent" || type === "group") {
        return;
      }
      if (isChild && path !== vue.unref(currentRoute).fullPath) {
        push(path);
        return;
      }
      e.stopPropagation();
      if (boxActive.value !== path) {
        boxActive.value = path;
        sideData.value = childMenus;
      }
    };
    const handleBoxMenuItemMouseenter = (item, e) => {
      if (props$1.collapse) {
        return;
      }
      stopTimer();
      const path = item.index;
      const trigger = props$1.boxTrigger;
      if (trigger !== "hover" || !path) {
        return;
      }
      if (!common.isExternalLink(path) && props$1.beforeClick && props$1.beforeClick(item, e) === false) {
        return;
      }
      const temp = util$1.getActiveChilds(boxData.value, path, "tempChildren");
      if (boxActive.value !== path) {
        state.isHover = true;
        boxActive.value = temp.some((d) => !d.meta?.hide) ? path : void 0;
        sideData.value = temp;
      }
    };
    const handleBoxMouseEnter = () => {
      stopTimer();
    };
    const handleBoxMouseLeave = () => {
      resetMenuState();
    };
    const handleSideMenuOpen = (index2, indexPath) => {
      emit("sideMenuOpen", index2, indexPath);
    };
    const handleSideMenuClose = (index2, indexPath) => {
      emit("sideMenuClose", index2, indexPath);
    };
    const handleSideMenuItemClick = (item, e, type) => {
      const path = item.index;
      const trigger = props$1.itemTrigger;
      if (!path || trigger !== "click" && trigger !== "hover") {
        return;
      }
      if (props$1.beforeClick && props$1.beforeClick(item, e) === false) {
        return;
      }
      if (type === "parent" || type === "group") {
        return;
      }
      if (common.isExternalLink(path)) {
        e.stopPropagation();
        window.open(path);
        return;
      }
      sideActive.value = path;
      if (path !== vue.unref(currentRoute).fullPath) {
        push(path);
      }
    };
    const handleSideMouseEnter = () => {
      stopTimer();
    };
    const handleSideMouseLeave = () => {
      resetMenuState();
    };
    const handleTabClick = (option) => {
      const key = option.name;
      const item = util$1.findTabByKey(key, props$1.tabs);
      const opt = { key, item, active: tabActive.value };
      emit("tabClick", opt);
    };
    const handleTabRemove = (key) => {
      const item = util$1.findTabByKey(key, props$1.tabs);
      const opt = { key, item, active: tabActive.value };
      emit("tabRemove", opt);
    };
    const handleTabContextMenu = (option) => {
      const opt = {
        key: option.name,
        item: util$1.findTabByKey(option.name, props$1.tabs),
        active: tabActive.value,
        command: option.command
      };
      emit("tabContextMenu", opt);
    };
    const handleTabSortChange = (data) => {
      const result = data.map((d) => {
        return util$1.findTabByKey(d.name, props$1.tabs);
      });
      if (props$1.fixedHome && props$1.tabs != null) {
        const homeTab = props$1.tabs.find((t) => t.home);
        if (homeTab) {
          result.unshift(homeTab);
        }
      }
      emit("tabSortChange", result);
    };
    const getContentElem = () => {
      if (!layoutRef.value) {
        return null;
      }
      return layoutRef.value.getContentEl();
    };
    const handleRouteChange = (route) => {
      const { path, meta } = route;
      hideFooter.value = !!meta.hideFooter;
      const contentEl = getContentElem();
      if (props$1.autoScrollTop && contentEl) {
        contentEl.scrollTop = 0;
      }
      if (props$1.redirectPath && path.startsWith(props$1.redirectPath)) {
        return;
      }
      hideSidebar.value = !!meta.hideSidebar;
      hideSidebox.value = props$1.sidebarLayout === "mix" ? !!meta.hideSidebox : true;
      hideHeader.value = !!meta.hideHeader;
      hideTabs.value = !!meta.hideTabs;
      const navigationIsChanged = updateNavigation();
      const sideNavigationIsChanged = updateSideNavigation();
      const { active, title, matched, activeOther } = util$1.getRouteMatched(
        route,
        menuData.value
      );
      levelData.value = util$1.getMatchedLevels(
        matched,
        activeOther,
        route,
        menuData.value,
        tabData.value
      );
      const t = util$1.getRouteTab(route, tabData.value, homeMenuPath.value, title);
      isHome.value = t.home;
      tabActive.value = t.key;
      emit("tabAdd", t);
      if (!navigationIsChanged && !sideNavigationIsChanged) {
        updateMenuActive(active, matched);
        if (navigation.value === "mix" || sideNavigation.value === "mix" || sideNavigation.value === "box") {
          splitMenuData();
        }
      }
      if (mobile.value) {
        updateCollapse(true);
      }
    };
    const updateMenuActive = (active, matched) => {
      const [active1, active2] = matched?.length ? [matched[0].path, (matched[1] ?? matched[0]).path] : [];
      if (navigation.value === "top") {
        navActive.value = active;
        boxActive.value = void 0;
      } else if (navigation.value === "mix") {
        navActive.value = active1;
        boxActive.value = active2;
      } else {
        navActive.value = void 0;
        boxActive.value = active1;
      }
      sideActive.value = active;
      state.navActive = navActive.value;
      state.boxActive = boxActive.value;
      state.sideActive = sideActive.value;
    };
    const splitMenuData = () => {
      const isTopNav = navigation.value === "top";
      const isMixNav = navigation.value === "mix";
      const isMixSide = sideNavigation.value === "mix" || sideNavigation.value === "box";
      const isCollapse = sideNavigation.value === "box" || props$1.collapse && !mobile.value;
      if (!menuData.value?.length) {
        navData.value = [];
        boxData.value = [];
        sideData.value = [];
      } else if (isTopNav) {
        navData.value = menuData.value;
        boxData.value = [];
        sideData.value = [];
      } else if (isMixNav) {
        navData.value = menuData.value.map((d) => {
          return { ...d, children: void 0, tempChildren: d.children };
        });
        const childMenus = util$1.getActiveChilds(menuData.value, navActive.value);
        if (!childMenus.length) {
          boxData.value = [];
          sideData.value = [];
        } else if (isMixSide) {
          boxData.value = childMenus.map((d) => {
            return {
              ...d,
              children: isCollapse ? d.children : void 0,
              tempChildren: d.children
            };
          });
          sideData.value = util$1.getActiveChilds(childMenus, boxActive.value);
        } else {
          boxData.value = [];
          sideData.value = childMenus;
        }
      } else {
        navData.value = [];
        if (isMixSide) {
          boxData.value = menuData.value.map((d) => {
            return {
              ...d,
              children: isCollapse ? d.children : void 0,
              tempChildren: d.children
            };
          });
          sideData.value = util$1.getActiveChilds(menuData.value, boxActive.value);
        } else {
          boxData.value = [];
          sideData.value = menuData.value;
        }
      }
      state.navData = navData.value;
      state.boxData = boxData.value;
      state.sideData = sideData.value;
    };
    const updateMenuData = () => {
      let home;
      menuData.value = common.mapTree(props$1.menus, (item) => {
        if (!home && !item.children?.length) {
          home = item;
        }
        const title = routeI18n(item.path, item) || item.meta?.title;
        return { ...item, meta: { ...item.meta, title } };
      });
      splitMenuData();
      homeMenuPath.value = props$1.homePath || home?.path || "/";
    };
    const updateTabData = () => {
      if (!props$1.tabs) {
        tabData.value = [];
        return;
      }
      tabData.value = props$1.tabs.map((item) => {
        const m = util$1.findMenuByPath(item.path, menuData.value);
        return {
          ...item,
          title: routeI18n(item.path, m, item) || item.title
        };
      });
    };
    const updateLevelData = () => {
      levelData.value = levelData.value.map((item) => {
        const t = util$1.findTabByPath(item.path, tabData.value);
        const m = util$1.findMenuByPath(item.path, menuData.value);
        const title = t?.title || m?.meta?.title || routeI18n(item.path, m, t, item);
        return { ...item, title: title || item.title };
      });
    };
    const routeI18n = (path, menu, tab, level) => {
      if (props$1.i18n && path) {
        return props$1.i18n({
          locale: props$1.locale,
          path,
          menu,
          tab,
          level
        });
      }
    };
    vue.watch(
      () => props$1.menus,
      () => {
        updateMenuData();
      },
      { deep: true }
    );
    vue.watch(
      () => props$1.tabs,
      () => {
        updateTabData();
        updateLevelData();
      },
      { deep: true }
    );
    vue.watch([() => props$1.layout, mobile], () => {
      updateNavigation();
    });
    vue.watch(
      () => props$1.sidebarLayout,
      () => {
        updateSideNavigation();
      }
    );
    vue.watch([navigation, sideNavigation], () => {
      const route = vue.unref(currentRoute);
      const { active, matched } = util$1.getRouteMatched(route, menuData.value);
      updateMenuActive(active, matched);
      splitMenuData();
    });
    vue.watch(
      () => props$1.collapse,
      () => {
        if (sideNavigation.value === "mix" && !mobile.value) {
          if (props$1.collapse) {
            boxData.value = boxData.value.map((d) => {
              return { ...d, children: d.tempChildren };
            });
          } else {
            boxData.value = boxData.value.map((d) => {
              return { ...d, children: void 0 };
            });
          }
          state.boxData = boxData.value;
        }
      }
    );
    vue.watch(
      () => props$1.locale,
      () => {
        updateMenuData();
        updateTabData();
        updateLevelData();
      },
      { immediate: true }
    );
    vue.watch(
      currentRoute,
      (route) => {
        handleRouteChange(vue.unref(route));
      },
      { immediate: true }
    );
    const layoutProvide = vue.shallowReactive({
      keepAlive: props$1.tabBar && props$1.keepAlive,
      responsive: props$1.responsive
    });
    vue.provide(props.PRO_LAYOUT_KEY, layoutProvide);
    vue.watch([() => props$1.tabBar, () => props$1.keepAlive], () => {
      layoutProvide.keepAlive = props$1.tabBar && props$1.keepAlive;
    });
    const [media, startMedia, stopMedia] = hook.useMediaQuery(hook.mobileMediaQuery, () => {
      const isMobile = props$1.responsive ? media.matches : false;
      if (mobile.value !== isMobile) {
        mobile.value = isMobile;
        updateCollapse(mobile.value);
      }
    });
    vue.watch(
      () => props$1.responsive,
      () => {
        layoutProvide.responsive = props$1.responsive;
        if (props$1.responsive) {
          startMedia();
        } else {
          stopMedia();
        }
      },
      { immediate: true }
    );
    hook.useWindowListener("keydown", (e) => {
      if (e.keyCode === 27 && props$1.compressOnEsc && props$1.maximized) {
        e.stopPropagation();
        updateMaximized(false);
      }
    });
    const handleResize = () => {
      const el = getContentElem();
      if (el) {
        const clientWidth = el.clientWidth || 0;
        const limitedWidth = 1120;
        const maxWidth = clientWidth > limitedWidth ? limitedWidth : clientWidth;
        const width = props$1.fluid ? clientWidth : maxWidth;
        const height = el.clientHeight;
        if (width !== state.contentWidth || height !== state.contentHeight) {
          state.contentWidth = width;
          state.contentHeight = height;
          emit("bodySizeChange", { width, height, mobile: mobile.value });
        }
      }
    };
    hook.useWindowListener(common.debounce(() => handleResize(), 500));
    const [startBodyResizeTimer] = hook.useTimer(600);
    vue.watch([() => props$1.collapse, () => props$1.compact], () => {
      startBodyResizeTimer(() => {
        handleResize();
      });
    });
    vue.watch(
      [
        routeLayout,
        routeSideType,
        routeTabBar,
        routeMaximized,
        () => props$1.fluid
      ],
      () => {
        vue.nextTick(() => {
          handleResize();
        });
      }
    );
    vue.onMounted(() => {
      handleResize();
    });
    __expose({
      layoutRef,
      // 弹窗操作
      openModal,
      closeModal,
      closeAllModal,
      updateModalProps
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleAdminLayout, {
        ref_key: "layoutRef",
        ref: layoutRef,
        height: _ctx.height,
        headerMenus: layoutHeaders.value,
        headerActive: navActive.value,
        sidebarMenus: layoutSidebars.value,
        sidebarActive: sideActive.value,
        sideboxMenus: layoutSideboxs.value,
        sideboxActive: isBoxSide.value || _ctx.collapse && !mobile.value ? sideActive.value : boxActive.value,
        tabs: layoutTabs.value,
        tabActive: tabActive.value,
        levels: layoutLevels.value,
        collapse: _ctx.collapse,
        compact: _ctx.compact,
        maximized: routeMaximized.value,
        tabBar: routeTabBar.value,
        breadcrumb: breadcrumbProps.value,
        backTop: backTopProps.value,
        headerMenuProps: navMenuProps.value,
        sidebarMenuProps: sideMenuProps.value,
        sideboxMenuProps: boxMenuProps.value,
        layout: routeLayout.value,
        sidebarLayout: routeSideType.value,
        headerStyle: _ctx.headerStyle,
        sidebarStyle: _ctx.sidebarStyle,
        mixSidebarStyle: _ctx.mixSidebarStyle,
        tabStyle: _ctx.tabStyle,
        fixedHeader: _ctx.fixedHeader,
        fixedSidebar: _ctx.fixedSidebar,
        fixedBody: _ctx.fixedBody,
        logoInHeader: _ctx.logoInHeader,
        fixedHome: _ctx.fixedHome,
        homePath: homeMenuPath.value,
        isHome: isHome.value,
        tabContextMenu: _ctx.tabContextMenu,
        tabContextMenus: _ctx.tabContextMenus,
        tabSortable: _ctx.tabSortable,
        headerTitleSlot: _ctx.headerTitleSlot,
        headerIconSlot: _ctx.headerIconSlot,
        sidebarTitleSlot: _ctx.sidebarTitleSlot,
        sidebarIconSlot: _ctx.sidebarIconSlot,
        sideboxTitleSlot: _ctx.sideboxTitleSlot,
        sideboxIconSlot: _ctx.sideboxIconSlot,
        headerCustomStyle: _ctx.headerCustomStyle,
        sidebarCustomStyle: _ctx.sidebarCustomStyle,
        sideboxCustomStyle: _ctx.sideboxCustomStyle,
        sideCustomStyle: _ctx.sideCustomStyle,
        tabsCustomStyle: _ctx.tabsCustomStyle,
        contentCustomStyle: _ctx.contentCustomStyle,
        logoStyle: _ctx.logoStyle,
        logoTitleStyle: _ctx.logoTitleStyle,
        headerMenusStyle: _ctx.headerMenusStyle,
        sidebarMenusStyle: _ctx.sidebarMenusStyle,
        sideboxMenusStyle: _ctx.sideboxMenusStyle,
        logoSrc: _ctx.logoSrc,
        logoTitle: _ctx.logoTitle,
        menuScrollToActive: _ctx.menuScrollToActive,
        mobile: mobile.value,
        class: vue.normalizeClass(["ele-pro-layout", { "ele-admin-limited": !_ctx.fluid }]),
        "onUpdate:collapse": updateCollapse,
        onLogoClick: handleLogoClick,
        onHeadMenuOpen: handleHeadMenuOpen,
        onHeadMenuClose: handleHeadMenuClose,
        onHeadMenuItemClick: handleHeadMenuItemClick,
        onHeadMenuItemMouseenter: handleHeadMenuItemMouseenter,
        onHeadMouseenter: handleHeadMouseenter,
        onHeadMouseleave: handleHeadMouseleave,
        onBoxMenuItemClick: handleBoxMenuItemClick,
        onBoxMenuItemMouseenter: handleBoxMenuItemMouseenter,
        onBoxMouseenter: handleBoxMouseEnter,
        onBoxMouseleave: handleBoxMouseLeave,
        onSideMenuOpen: handleSideMenuOpen,
        onSideMenuClose: handleSideMenuClose,
        onSideMenuItemClick: handleSideMenuItemClick,
        onSideMouseenter: handleSideMouseEnter,
        onSideMouseleave: handleSideMouseLeave,
        onTabClick: handleTabClick,
        onTabRemove: handleTabRemove,
        onTabContextMenu: handleTabContextMenu,
        onTabSortChange: handleTabSortChange
      }, vue.createSlots({
        body: vue.withCtx(() => [
          _ctx.tabBar && _ctx.keepAlive ? (vue.openBlock(), vue.createBlock(IframeGroup, {
            key: 0,
            keepAlive: _ctx.keepAlive,
            transitionName: _ctx.transitionName,
            transitionDelay: _ctx.transitionDelay,
            tabData: tabData.value,
            tabActive: tabActive.value
          }, null, 8, ["keepAlive", "transitionName", "transitionDelay", "tabData", "tabActive"])) : vue.createCommentVNode("", true),
          vue.createVNode(vue.unref(EleModalRender), {
            modals: vue.unref(modals),
            onRemoveItem: vue.unref(removeModal),
            onUpdateItemVisible: vue.unref(updateModalVisible),
            onUpdateItemProps: vue.unref(updateModalProps)
          }, null, 8, ["modals", "onRemoveItem", "onUpdateItemVisible", "onUpdateItemProps"])
        ]),
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "default"),
          !hideFooter.value ? vue.renderSlot(_ctx.$slots, "footer", { key: 0 }) : vue.createCommentVNode("", true)
        ]),
        _: 2
      }, [
        _ctx.$slots.logo ? {
          name: "logo",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "logo", {
              collapse: _ctx.collapse,
              sidebar: sidebar.value
            })
          ]),
          key: "0"
        } : void 0,
        _ctx.$slots.logoTitle ? {
          name: "logoTitle",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "logoTitle", {
              collapse: _ctx.collapse,
              sidebar: sidebar.value
            })
          ]),
          key: "1"
        } : void 0,
        _ctx.$slots.breadcrumb ? {
          name: "breadcrumb",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "breadcrumb", {
              levels: levelData.value,
              isHome: isHome.value,
              homePath: homeMenuPath.value,
              sidebar: sidebar.value
            })
          ]),
          key: "2"
        } : void 0,
        _ctx.$slots.left ? {
          name: "left",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "left", { sidebar: sidebar.value })
          ]),
          key: "3"
        } : void 0,
        _ctx.$slots.center ? {
          name: "center",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "center", { sidebar: sidebar.value })
          ]),
          key: "4"
        } : void 0,
        _ctx.$slots.right ? {
          name: "right",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "right", { sidebar: sidebar.value })
          ]),
          key: "5"
        } : void 0,
        vue.renderList(Object.keys(_ctx.$slots).filter(
          (k) => ![
            "default",
            "logo",
            "logoTitle",
            "breadcrumb",
            "left",
            "center",
            "right",
            "footer",
            "body"
          ].includes(k)
        ), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1032, ["height", "headerMenus", "headerActive", "sidebarMenus", "sidebarActive", "sideboxMenus", "sideboxActive", "tabs", "tabActive", "levels", "collapse", "compact", "maximized", "tabBar", "breadcrumb", "backTop", "headerMenuProps", "sidebarMenuProps", "sideboxMenuProps", "layout", "sidebarLayout", "headerStyle", "sidebarStyle", "mixSidebarStyle", "tabStyle", "fixedHeader", "fixedSidebar", "fixedBody", "logoInHeader", "fixedHome", "homePath", "isHome", "tabContextMenu", "tabContextMenus", "tabSortable", "headerTitleSlot", "headerIconSlot", "sidebarTitleSlot", "sidebarIconSlot", "sideboxTitleSlot", "sideboxIconSlot", "headerCustomStyle", "sidebarCustomStyle", "sideboxCustomStyle", "sideCustomStyle", "tabsCustomStyle", "contentCustomStyle", "logoStyle", "logoTitleStyle", "headerMenusStyle", "sidebarMenusStyle", "sideboxMenusStyle", "logoSrc", "logoTitle", "menuScrollToActive", "mobile", "class"]);
    };
  }
});
module.exports = _sfc_main;
