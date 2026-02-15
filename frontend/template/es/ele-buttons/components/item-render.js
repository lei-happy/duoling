import { defineComponent, computed, createElementBlock, openBlock, Fragment, createBlock, createCommentVNode, unref, mergeProps, withCtx, createElementVNode, toDisplayString, createVNode } from "vue";
import { ElDivider, ElLink, ElIcon, ElButton } from "element-plus";
import { ArrowDown, EyeOutlined, ArrowUp, VerticalAlignMiddleOutlined, ColumnHeightOutlined, DownloadOutlined, UploadOutlined, DeleteOutlined, EditOutlined, PlusOutlined, SyncOutlined, SearchOutlined } from "../../icons/index";
import { mapTree } from "../../utils/common";
import { useDropdown } from "../../ele-dropdown-provider/util";
import { usePopconfirm } from "../../ele-popconfirm-provider/util";
const _sfc_main = /* @__PURE__ */ defineComponent({
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
      search: SearchOutlined,
      reset: SyncOutlined,
      add: PlusOutlined,
      delBatch: DeleteOutlined,
      edit: EditOutlined,
      del: DeleteOutlined,
      import: UploadOutlined,
      export: DownloadOutlined,
      upload: UploadOutlined,
      download: DownloadOutlined,
      expand: ColumnHeightOutlined,
      fold: VerticalAlignMiddleOutlined,
      searchExpand: ArrowDown,
      searchFold: ArrowUp,
      detail: EyeOutlined
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
    const dropdown = useDropdown();
    const popconfirm = usePopconfirm();
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
    const title = computed(() => {
      return getItemTitle(props.item, props.lang);
    });
    const icon = computed(() => {
      return getItemIcon(props.item);
    });
    const linkType = computed(() => {
      const preset = props.item.preset;
      if (preset && dangerLinkPreset.includes(preset)) {
        return "danger";
      }
      return "primary";
    });
    const btnType = computed(() => {
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
        mapTree(item.dropdownItems, (d) => {
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
      return openBlock(), createElementBlock(Fragment, null, [
        __props.divider ? (openBlock(), createBlock(unref(ElDivider), mergeProps({
          key: 0,
          direction: "vertical",
          class: "ele-buttons-divider"
        }, typeof __props.divider === "object" ? __props.divider : {}), null, 16)) : createCommentVNode("", true),
        (__props.item.type ?? __props.type) === "link" ? (openBlock(), createBlock(unref(ElLink), mergeProps({
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
          default: withCtx(() => [
            createElementVNode("span", null, toDisplayString(title.value), 1),
            __props.item.dropdownItems && __props.item.dropdownItems.length ? (openBlock(), createBlock(unref(ElIcon), {
              key: 0,
              class: "ele-buttons-arrow"
            }, {
              default: withCtx(() => [
                createVNode(unref(ArrowDown))
              ]),
              _: 1
            })) : createCommentVNode("", true)
          ]),
          _: 1
        }, 16, ["type", "icon", "class"])) : (openBlock(), createBlock(unref(ElButton), mergeProps({
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
          default: withCtx(() => [
            createElementVNode("span", null, toDisplayString(title.value), 1),
            __props.item.dropdownItems && __props.item.dropdownItems.length ? (openBlock(), createBlock(unref(ElIcon), {
              key: 0,
              class: "ele-buttons-arrow"
            }, {
              default: withCtx(() => [
                createVNode(unref(ArrowDown))
              ]),
              _: 1
            })) : createCommentVNode("", true)
          ]),
          _: 1
        }, 16, ["type", "icon", "class"]))
      ], 64);
    };
  }
});
export {
  _sfc_main as default
};
