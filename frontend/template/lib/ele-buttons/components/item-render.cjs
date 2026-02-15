"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const util = require("../../ele-dropdown-provider/util");
const util$1 = require("../../ele-popconfirm-provider/util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ItemRender" },
  __name: "item-render",
  props: {
    /** 按钮数据 */
    item: {
      type: Object,
      required: true
    },
    /** 是否显示分割线 */
    divider: [Boolean, Object],
    /** 组件类型 */
    type: String,
    /** 是否增加包裹类名 */
    wrapClass: Boolean,
    /** 文案 */
    lang: {
      type: Object,
      required: true
    }
  },
  emits: {
    itemClick: (_command, _e) => true
  },
  setup(__props, { emit: __emit }) {
    const presetIcon = {
      search: index.SearchOutlined,
      reset: index.SyncOutlined,
      add: index.PlusOutlined,
      delBatch: index.DeleteOutlined,
      edit: index.EditOutlined,
      del: index.DeleteOutlined,
      import: index.UploadOutlined,
      export: index.DownloadOutlined,
      upload: index.UploadOutlined,
      download: index.DownloadOutlined,
      expand: index.ColumnHeightOutlined,
      fold: index.VerticalAlignMiddleOutlined,
      searchExpand: index.ArrowDown,
      searchFold: index.ArrowUp,
      detail: index.EyeOutlined
    };
    const dangerLinkPreset = ["del", "delBatch"];
    const dangerBtnPreset = ["del", "delBatch"];
    const warningBtnPreset = ["edit"];
    const defaultBtnPreset = [
      "reset",
      "import",
      "export",
      "expand",
      "fold",
      "detail",
      "more",
      "cancel"
    ];
    const props = __props;
    const emit = __emit;
    const dropdown = util.useDropdown();
    const popconfirm = util$1.usePopconfirm();
    const getItemTitle = (item, lang) => {
      if (item.title != null) {
        return item.title;
      }
      if (!item.preset) {
        return;
      }
      return lang[item.preset];
    };
    const getItemIcon = (item) => {
      if (item.icon != null) {
        return item.icon;
      }
      if (!item.preset) {
        return;
      }
      return presetIcon[item.preset];
    };
    const title = vue.computed(() => {
      return getItemTitle(props.item, props.lang);
    });
    const icon = vue.computed(() => {
      return getItemIcon(props.item);
    });
    const linkType = vue.computed(() => {
      const preset = props.item.preset;
      if (preset && dangerLinkPreset.includes(preset)) {
        return "danger";
      }
      return "primary";
    });
    const btnType = vue.computed(() => {
      const preset = props.item.preset;
      if (preset) {
        if (dangerBtnPreset.includes(preset)) {
          return "danger";
        }
        if (warningBtnPreset.includes(preset)) {
          return "warning";
        }
        if (defaultBtnPreset.includes(preset)) {
          return "default";
        }
      }
      return "primary";
    });
    const triggerItemClick = (command, e) => {
      emit("itemClick", command, e);
    };
    const handleDropdownCommand = (command) => {
      triggerItemClick(command);
    };
    const handleOpenDropdown = (e, item) => {
      if (!item.dropdownItems || !item.dropdownItems.length || !dropdown || !dropdown.openDropdown) {
        return;
      }
      dropdown.openDropdown(
        e.currentTarget,
        common.mapTree(item.dropdownItems, (d) => {
          return {
            ...d,
            title: getItemTitle(d, props.lang),
            icon: getItemIcon(d)
          };
        }),
        {
          iconSize: "small",
          onCommand: handleDropdownCommand,
          popperOptions: { strategy: "fixed" },
          ...item.dropdownProps || {},
          trigger: "hover"
        }
      );
    };
    const handleOpenPopconfirm = (e, item) => {
      if (!item.popconfirmProps) {
        return;
      }
      if (!popconfirm || !popconfirm.openPopconfirm) {
        const onConfirm = item.popconfirmProps.onConfirm;
        onConfirm && onConfirm(e);
        return;
      }
      popconfirm.openPopconfirm(e.currentTarget, {
        popperOptions: { strategy: "fixed" },
        ...item.popconfirmProps || {},
        trigger: "click"
      });
    };
    const handleItemClick = (e, item) => {
      if (item.popconfirmProps) {
        handleOpenPopconfirm(e, item);
      }
      item.onClick && item.onClick(e);
      triggerItemClick(item.command, e);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        __props.divider ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElDivider), vue.mergeProps({
          key: 0,
          direction: "vertical",
          class: "ele-buttons-divider"
        }, typeof __props.divider === "object" ? __props.divider : {}), null, 16)) : vue.createCommentVNode("", true),
        (__props.item.type ?? __props.type) === "link" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElLink), vue.mergeProps({
          key: 1,
          underline: "never",
          type: linkType.value,
          icon: icon.value,
          class: ["ele-buttons-item ele-buttons-link", {
            "ele-buttons-icon-link": !!icon.value,
            "ele-buttons-wrap": __props.wrapClass
          }]
        }, __props.item.props || {}, {
          onClick: _cache[0] || (_cache[0] = (e) => handleItemClick(e, __props.item)),
          onMouseenter: _cache[1] || (_cache[1] = (e) => handleOpenDropdown(e, __props.item))
        }), {
          default: vue.withCtx(() => [
            vue.createElementVNode("span", null, vue.toDisplayString(title.value), 1),
            __props.item.dropdownItems && __props.item.dropdownItems.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
              key: 0,
              class: "ele-buttons-arrow"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.ArrowDown))
              ]),
              _: 1
            })) : vue.createCommentVNode("", true)
          ]),
          _: 1
        }, 16, ["type", "icon", "class"])) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), vue.mergeProps({
          key: 2,
          type: btnType.value,
          icon: icon.value,
          class: ["ele-buttons-item ele-buttons-btn", {
            "ele-buttons-icon-btn": !!icon.value,
            "ele-buttons-wrap": __props.wrapClass
          }]
        }, __props.item.props || {}, {
          onClick: _cache[2] || (_cache[2] = (e) => handleItemClick(e, __props.item)),
          onMouseenter: _cache[3] || (_cache[3] = (e) => handleOpenDropdown(e, __props.item))
        }), {
          default: vue.withCtx(() => [
            vue.createElementVNode("span", null, vue.toDisplayString(title.value), 1),
            __props.item.dropdownItems && __props.item.dropdownItems.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
              key: 0,
              class: "ele-buttons-arrow"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.ArrowDown))
              ]),
              _: 1
            })) : vue.createCommentVNode("", true)
          ]),
          _: 1
        }, 16, ["type", "icon", "class"]))
      ], 64);
    };
  }
});
module.exports = _sfc_main;
