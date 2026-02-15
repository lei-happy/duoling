"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const EleTabWrap = require("../../ele-tab-wrap/index");
const EleTabTool = require("../../ele-tab-tool/index");
const EleTabs = require("../../ele-tabs/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "LayoutTabs" },
  __name: "layout-tabs",
  props: {
    /** 页签数据 */
    tabs: Array,
    /** 页签选中 */
    active: String,
    /** 是否需要固定的主页页签 */
    fixedHome: Boolean,
    /** 主页路由地址 */
    homePath: String,
    /** 当前路由是否是主页 */
    isHome: Boolean,
    /** 页签风格 */
    tabStyle: String,
    /** 是否支持右键菜单 */
    tabContextMenu: [Boolean, Object],
    /** 右键菜单 */
    tabContextMenus: [Array, Function],
    /** 是否支持拖动排序 */
    tabSortable: Boolean
  },
  emits: {
    tabClick: (_option) => true,
    tabRemove: (_name) => true,
    tabContextMenu: (_option) => true,
    tabSortChange: (_data) => true
  },
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const handleTabItemClick = (option) => {
      emit("tabClick", option);
    };
    const handleTabRemove = (name) => {
      emit("tabRemove", name);
    };
    const handleTabContextMenu = (option) => {
      emit("tabContextMenu", option);
    };
    const handleTabSortChange = (data) => {
      emit("tabSortChange", data);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleTabWrap, {
        type: __props.tabStyle,
        class: "ele-admin-tabs"
      }, {
        default: vue.withCtx(() => [
          __props.fixedHome ? (vue.openBlock(), vue.createBlock(EleTabTool, {
            key: 0,
            tab: true,
            active: __props.isHome,
            tabName: __props.homePath
          }, {
            default: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "tabHome", { active: __props.active }, () => [
                vue.createVNode(vue.unref(elementPlus.ElIcon), {
                  class: "ele-tab-icon",
                  style: { verticalAlign: "-2.4px" }
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.HomeOutlined), { style: { transform: "scale(1.08)" } })
                  ]),
                  _: 1
                })
              ])
            ]),
            _: 3
          }, 8, ["active", "tabName"])) : vue.createCommentVNode("", true),
          __props.tabs ? (vue.openBlock(), vue.createBlock(EleTabs, {
            key: 1,
            items: __props.tabs,
            modelValue: __props.active,
            sortable: __props.tabSortable,
            contextMenu: __props.tabContextMenu,
            contextMenus: __props.tabContextMenus,
            mousewheel: true,
            handleClick: true,
            onTabRemove: handleTabRemove,
            onTabItemClick: handleTabItemClick,
            onTabContextMenu: handleTabContextMenu,
            onTabSortChange: handleTabSortChange
          }, vue.createSlots({ _: 2 }, [
            _ctx.$slots.tabTitle ? {
              name: "label",
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, "tabTitle", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ]),
              key: "0"
            } : void 0
          ]), 1032, ["items", "modelValue", "sortable", "contextMenu", "contextMenus"])) : vue.createCommentVNode("", true),
          vue.renderSlot(_ctx.$slots, "tabExtra", { active: __props.active })
        ]),
        _: 3
      }, 8, ["type"]);
    };
  }
});
module.exports = _sfc_main;
