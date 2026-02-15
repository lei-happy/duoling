"use strict";
const vue = require("vue");
const VueDraggable = require("vuedraggable");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const receiver = require("../ele-config-provider/receiver");
const EleImageViewer = require("../ele-image-viewer/index");
const index = require("../icons/index");
const ListItem = require("./components/list-item");
const props = require("./props");
const _hoisted_1 = { class: "ele-upload-hidden" };
const _hoisted_2 = ["accept"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleUploadList" },
  __name: "index",
  props: props.uploadListProps,
  emits: props.uploadListEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const ownSlots = ["default", "icon"];
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("upload", props2);
    const previewVisible = vue.ref(false);
    const previewImages = vue.ref([]);
    const previewCurrentIndex = vue.ref(0);
    const imageObjectUrls = vue.ref([]);
    const uploadInputRef = vue.ref(null);
    let editItem = null;
    const uploadEnable = vue.computed(() => {
      return !props2.readonly && !(typeof props2.limit === "number" && props2.limit > 0 && props2.modelValue != null && props2.modelValue.length >= props2.limit);
    });
    const buildItem = (file) => {
      return {
        key: `ele${common.uuid(16, 10)}${String(Date.now())}`,
        name: file.name,
        status: void 0,
        progress: 0,
        file
      };
    };
    const getItemImageUrl = (item, file) => {
      if (item && item.url) {
        return item.url;
      }
      const itemFile = item?.file;
      if (itemFile != null && itemFile.type.startsWith("image")) {
        const t = imageObjectUrls.value.find((d) => d.file === itemFile);
        if (t != null) {
          return t.url;
        }
        const url = URL.createObjectURL(itemFile);
        imageObjectUrls.value.push({ file: itemFile, url });
        return url;
      }
    };
    const previewItem = (item) => {
      if (props2.beforePreview && props2.beforePreview(item) === false) {
        return;
      }
      if (props2.modelValue != null) {
        const data = [];
        props2.modelValue.forEach((d) => {
          const url = getItemImageUrl(d);
          if (url && d.thumbnail !== false) {
            data.push({ item: d, url });
          }
        });
        const index2 = data.findIndex((t) => t.item.key === item.key);
        if (index2 !== -1) {
          const urls = data.map((d) => d.url);
          openImagePreview(urls, index2);
        }
      }
    };
    const openImagePreview = (urls, index2) => {
      previewImages.value = urls;
      previewCurrentIndex.value = index2;
      previewVisible.value = true;
    };
    const updateModelValue = (value) => {
      emit("update:modelValue", value);
    };
    const handleUpload = (file) => {
      if (uploadEnable.value && !props2.disabled) {
        const item = buildItem(file);
        emit("upload", item);
      }
      return false;
    };
    const handleItemClick = (item) => {
      if (props2.preview) {
        previewItem(item);
      }
      emit("itemClick", item);
    };
    const handleItemRemove = (item) => {
      emit("remove", item);
    };
    const handleItemEdit = (item) => {
      if (props2.beforeItemEdit && props2.beforeItemEdit(item) === false) {
        return;
      }
      const $input = uploadInputRef.value;
      if ($input != null) {
        editItem = item;
        $input.value = "";
        $input && $input.click();
      }
    };
    const handleItemPreview = (item) => {
      previewItem(item);
      emit("preview", item);
    };
    const handleItemRetry = (item) => {
      emit("retry", item);
    };
    const handleInputChange = (e) => {
      const file = e.target.files?.[0];
      if (file != null && editItem != null) {
        const result = { item: editItem, newItem: buildItem(file) };
        editItem = null;
        emit("editUpload", result);
      }
    };
    const handleUploadClick = (e) => {
      if (props2.beforeUploadClick && props2.beforeUploadClick(e) === false) {
        e.stopPropagation();
        e.preventDefault();
      }
    };
    const clearImageObjectUrls = () => {
      const temp = imageObjectUrls.value;
      imageObjectUrls.value = [];
      temp.forEach((item) => {
        URL.revokeObjectURL(item.url);
      });
    };
    vue.watch(
      () => props2.modelValue,
      () => {
        if (props2.modelValue == null) {
          clearImageObjectUrls();
          return;
        }
        const urls = [];
        props2.modelValue.forEach((item) => {
          const url = getItemImageUrl(item);
          if (url) {
            urls.push(url);
          }
        });
        for (let i = imageObjectUrls.value.length - 1; i >= 0; i--) {
          const url = imageObjectUrls.value[i].url;
          if (!urls.includes(url)) {
            imageObjectUrls.value.splice(i, 1);
            URL.revokeObjectURL(url);
          }
        }
      },
      {
        immediate: true,
        deep: true
      }
    );
    vue.onBeforeUnmount(() => {
      clearImageObjectUrls();
    });
    __expose({
      openImagePreview
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(VueDraggable), vue.mergeProps({
        itemKey: "key",
        animation: 300,
        setData: () => void 0,
        handle: ".ele-upload-handle",
        class: ["ele-upload-list", [
          { "is-file-list": _ctx.listType === "file" },
          { "is-disabled": _ctx.disabled }
        ]]
      }, !_ctx.sortable || _ctx.sortable === true ? {} : _ctx.sortable, {
        modelValue: _ctx.modelValue || [],
        "onUpdate:modelValue": updateModelValue
      }), {
        item: vue.withCtx(({ element }) => [
          vue.createVNode(ListItem, {
            item: element,
            readonly: _ctx.readonly,
            disabled: _ctx.disabled,
            sortable: _ctx.sortable && !_ctx.readonly && !_ctx.disabled && _ctx.limit !== 1,
            imageProps: _ctx.imageProps,
            progressProps: _ctx.progressProps,
            imageObjectUrls: imageObjectUrls.value,
            tools: _ctx.tools,
            listType: _ctx.listType,
            locale: vue.unref(lang),
            style: vue.normalizeStyle(_ctx.itemStyle),
            onItemClick: handleItemClick,
            onRemove: handleItemRemove,
            onEdit: handleItemEdit,
            onPreview: handleItemPreview,
            onRetry: handleItemRetry
          }, vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter(
              (k) => !ownSlots.includes(k)
            ), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1032, ["item", "readonly", "disabled", "sortable", "imageProps", "progressProps", "imageObjectUrls", "tools", "listType", "locale", "style"])
        ]),
        footer: vue.withCtx(() => [
          uploadEnable.value && _ctx.buttonStyle !== false ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            style: vue.normalizeStyle(typeof _ctx.buttonStyle === "boolean" ? void 0 : _ctx.buttonStyle),
            class: "ele-upload-item ele-upload-button"
          }, [
            vue.createVNode(vue.unref(elementPlus.ElUpload), {
              action: "",
              drag: _ctx.drag,
              accept: _ctx.accept,
              multiple: _ctx.multiple,
              disabled: _ctx.disabled,
              showFileList: false,
              beforeUpload: handleUpload
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", {
                  class: "ele-upload-button-inner",
                  onClick: handleUploadClick
                }, [
                  vue.renderSlot(_ctx.$slots, "icon", {}, () => [
                    vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-upload-icon" }, {
                      default: vue.withCtx(() => [
                        vue.createVNode(vue.unref(index.PlusOutlined))
                      ]),
                      _: 1
                    })
                  ])
                ])
              ]),
              _: 3
            }, 8, ["drag", "accept", "multiple", "disabled"])
          ], 4)) : vue.createCommentVNode("", true),
          vue.createElementVNode("div", _hoisted_1, [
            _ctx.tools ? (vue.openBlock(), vue.createElementBlock("input", {
              key: 0,
              ref_key: "uploadInputRef",
              ref: uploadInputRef,
              type: "file",
              accept: _ctx.accept,
              class: "ele-upload-input",
              onChange: handleInputChange
            }, null, 40, _hoisted_2)) : vue.createCommentVNode("", true),
            vue.createVNode(EleImageViewer, vue.mergeProps({ infinite: false }, _ctx.previewProps || {}, {
              modelValue: previewVisible.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => previewVisible.value = $event),
              urlList: previewImages.value,
              initialIndex: previewCurrentIndex.value
            }), null, 16, ["modelValue", "urlList", "initialIndex"])
          ]),
          vue.renderSlot(_ctx.$slots, "extra")
        ]),
        _: 3
      }, 16, ["class", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
