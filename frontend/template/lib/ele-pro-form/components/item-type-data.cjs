"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const elementPlus = require("element-plus");
const EleIcon = require("../../ele-icon/index");
const EleText = require("../../ele-text/index");
const EleAlert = require("../../ele-alert/index");
const EleSteps = require("../../ele-steps/index");
const EleProTable = require("../../ele-pro-table/index");
const EleCard = require("../../ele-card/index");
const EleTabs = require("../../ele-tabs/index");
const EleTable = require("../../ele-table/index");
const EleAdminLayout = require("../../ele-admin-layout/index");
const EleTreeSelect = require("../../ele-tree-select/index");
const EleTableSelect = require("../../ele-table-select/index");
const EleCheckCard = require("../../ele-check-card/index");
const EleEditTag = require("../../ele-edit-tag/index");
const EleSelect = require("../../ele-select/index");
const EleCascader = require("../../ele-cascader/index");
const EleRadioGroup = require("../../ele-radio-group/index");
const EleCheckboxGroup = require("../../ele-checkbox-group/index");
const EleSelectTree = require("../../ele-select-tree/index");
const EleTransfer = require("../../ele-transfer/index");
const EleMention = require("../../ele-mention/index");
const EleAutocomplete = require("../../ele-autocomplete/index");
const defaultItemTypeData = [
  {
    type: "label",
    component: vue.markRaw(EleText),
    isContainer: true,
    sortDisabled: true,
    renderLabelText: true
  },
  {
    type: "divider",
    component: vue.markRaw(elementPlus.ElDivider),
    isContainer: true,
    sortDisabled: true,
    renderLabelText: true
  },
  {
    type: "button",
    component: vue.markRaw(elementPlus.ElButton),
    isContainer: true,
    sortDisabled: true,
    renderLabelText: true,
    defaultProps: () => ({
      type: "primary"
    })
  },
  {
    type: "icon",
    component: vue.markRaw(EleIcon),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "image",
    component: vue.markRaw(elementPlus.ElImage),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "alert",
    component: vue.markRaw(EleAlert),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "steps",
    component: vue.markRaw(EleSteps),
    isContainer: true,
    sortDisabled: true,
    defaultProps: ({ modelValue }) => ({
      active: modelValue ?? 0
    })
  },
  {
    type: "proTable",
    component: vue.markRaw(EleProTable),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "card",
    component: vue.markRaw(EleCard),
    isContainer: true,
    defaultProps: () => ({
      bordered: true
    })
  },
  {
    type: "tabs",
    component: vue.markRaw(EleTabs),
    isContainer: true,
    defaultProps: ({ item, modelValue }) => ({
      type: "border-card",
      modelValue: modelValue ?? item.children?.[0]?.prop
    }),
    reservedProps: ({ item, isShowFormItem }) => ({
      items: (item.children || []).filter((c) => isShowFormItem(c)).map((c) => ({
        name: c.props?.name ?? c.prop,
        label: c.props?.label ?? c.label,
        disabled: c.props?.disabled,
        closable: c.props?.closable,
        lazy: c.props?.lazy,
        slot: "itemContent",
        meta: c
      }))
    }),
    reservedSlots: ({ renderChildren }) => ({
      itemContent: (slotProps) => renderChildren(slotProps?.item?.meta, false, true),
      default: () => void 0
    })
  },
  {
    type: "tabPane",
    component: "div",
    isContainer: true,
    containerSelectable: true
  },
  {
    type: "table",
    component: vue.markRaw(EleTable),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "tableRow",
    component: "tr",
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "tableCell",
    component: "td",
    isContainer: true,
    containerSelectable: true
  },
  {
    type: "collapse",
    component: vue.markRaw(elementPlus.ElCollapse),
    isContainer: true,
    sortDisabled: true,
    defaultProps: ({ item, modelValue }) => ({
      modelValue: modelValue ?? (item.props?.accordion ? item.children?.[0]?.props?.name ?? item.children?.[0]?.prop : [])
    }),
    reservedProps: ({ updateModelValue }) => ({
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "collapseItem",
    component: vue.markRaw(elementPlus.ElCollapseItem),
    isContainer: true,
    containerSelectable: true
  },
  {
    type: "carousel",
    component: vue.markRaw(elementPlus.ElCarousel),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "carouselItem",
    component: vue.markRaw(elementPlus.ElCarouselItem),
    isContainer: true,
    containerSelectable: true
  },
  {
    type: "descriptions",
    component: vue.markRaw(elementPlus.ElDescriptions),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "descriptionsItem",
    component: vue.markRaw(elementPlus.ElDescriptionsItem),
    isContainer: true,
    containerSelectable: true
  },
  {
    type: "row",
    component: vue.markRaw(elementPlus.ElRow),
    isContainer: true,
    sortDisabled: true
  },
  {
    type: "col",
    component: vue.markRaw(elementPlus.ElCol),
    isContainer: true,
    containerSelectable: true
  },
  {
    type: "adminLayout",
    component: vue.markRaw(EleAdminLayout),
    isContainer: true
  },
  {
    type: "div",
    component: "div",
    isContainer: true,
    sortDisabled: true,
    renderLabelText: true
  },
  {
    type: "input",
    component: vue.markRaw(elementPlus.ElInput),
    defaultProps: () => ({
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    }),
    requiredTrigger: "blur"
  },
  {
    type: "textarea",
    component: vue.markRaw(elementPlus.ElInput),
    defaultProps: () => ({
      rows: 4
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      type: "textarea",
      modelValue,
      "onUpdate:modelValue": updateModelValue
    }),
    requiredTrigger: "blur"
  },
  {
    type: "select",
    component: vue.markRaw(EleSelect),
    defaultProps: () => ({
      class: "ele-fluid",
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "multipleSelect",
    component: vue.markRaw(EleSelect),
    defaultProps: () => ({
      class: "ele-fluid",
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      multiple: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "radio",
    component: vue.markRaw(EleRadioGroup),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "radioButton",
    component: vue.markRaw(EleRadioGroup),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      type: "button",
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "checkbox",
    component: vue.markRaw(EleCheckboxGroup),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "checkboxButton",
    component: vue.markRaw(EleCheckboxGroup),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      type: "button",
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "date",
    component: vue.markRaw(elementPlus.ElDatePicker),
    defaultProps: () => ({
      class: "ele-fluid",
      valueFormat: "YYYY-MM-DD"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "datetime",
    component: vue.markRaw(elementPlus.ElDatePicker),
    defaultProps: () => ({
      class: "ele-fluid",
      valueFormat: "YYYY-MM-DD HH:mm:ss"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      type: "datetime",
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "daterange",
    component: vue.markRaw(elementPlus.ElDatePicker),
    defaultProps: () => ({
      class: "ele-fluid",
      valueFormat: "YYYY-MM-DD",
      rangeSeparator: "-",
      unlinkPanels: true,
      type: "daterange"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "datetimerange",
    component: vue.markRaw(elementPlus.ElDatePicker),
    defaultProps: () => ({
      class: "ele-fluid",
      valueFormat: "YYYY-MM-DD HH:mm:ss",
      rangeSeparator: "-",
      unlinkPanels: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      type: "datetimerange",
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "time",
    component: vue.markRaw(elementPlus.ElTimePicker),
    defaultProps: () => ({
      class: "ele-fluid",
      valueFormat: "HH:mm:ss"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "timerange",
    component: vue.markRaw(elementPlus.ElTimePicker),
    defaultProps: () => ({
      class: "ele-fluid",
      valueFormat: "HH:mm:ss",
      rangeSeparator: "-"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      isRange: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "timeSelect",
    component: vue.markRaw(elementPlus.ElTimeSelect),
    defaultProps: () => ({
      class: "ele-fluid"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "switch",
    component: vue.markRaw(elementPlus.ElSwitch),
    defaultProps: () => ({
      activeValue: 1,
      inactiveValue: 0
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "inputNumber",
    component: vue.markRaw(elementPlus.ElInputNumber),
    defaultProps: () => ({
      class: "ele-fluid",
      controlsPosition: "right"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "autocomplete",
    component: vue.markRaw(EleAutocomplete),
    defaultProps: () => ({
      class: "ele-fluid"
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "cascader",
    component: vue.markRaw(EleCascader),
    defaultProps: () => ({
      class: "ele-fluid",
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "multipleCascader",
    component: vue.markRaw(EleCascader),
    defaultProps: () => ({
      class: "ele-fluid",
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      multiple: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "rate",
    component: vue.markRaw(elementPlus.ElRate),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "slider",
    component: vue.markRaw(elementPlus.ElSlider),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "sliderRange",
    component: vue.markRaw(elementPlus.ElSlider),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      range: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "mention",
    component: vue.markRaw(EleMention),
    defaultProps: () => ({
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "colorPicker",
    component: vue.markRaw(elementPlus.ElColorPicker),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "transfer",
    component: vue.markRaw(EleTransfer),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "treeSelect",
    component: vue.markRaw(EleSelectTree),
    defaultProps: () => ({
      class: "ele-fluid",
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "treeMultipleSelect",
    component: vue.markRaw(EleSelectTree),
    defaultProps: () => ({
      class: "ele-fluid",
      clearable: true,
      showCheckbox: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      multiple: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "virtualTreeSelect",
    component: vue.markRaw(EleTreeSelect),
    defaultProps: () => ({
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "virtualTreeMultipleSelect",
    component: vue.markRaw(EleTreeSelect),
    defaultProps: () => ({
      clearable: true,
      maxTagCount: 1
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      multiple: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "tableSelect",
    component: vue.markRaw(EleTableSelect),
    defaultProps: () => ({
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "tableMultipleSelect",
    component: vue.markRaw(EleTableSelect),
    defaultProps: () => ({
      clearable: true
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      multiple: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "checkCard",
    component: vue.markRaw(EleCheckCard),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "multipleCheckCard",
    component: vue.markRaw(EleCheckCard),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      multiple: true,
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "editTag",
    component: vue.markRaw(EleEditTag),
    defaultProps: () => ({
      type: "info",
      style: { marginTop: "4px" },
      itemStyle: { margin: "0 4px 4px 0" },
      buttonStyle: { marginBottom: "4px" },
      inputTagStyle: { marginBottom: "4px" }
    }),
    reservedProps: ({ modelValue, updateModelValue }) => ({
      modelValue,
      "onUpdate:modelValue": updateModelValue
    })
  },
  {
    type: "text",
    component: vue.markRaw(EleText),
    reservedSlots: ({ modelValue }) => ({
      default: () => modelValue
    })
  }
];
exports.defaultItemTypeData = defaultItemTypeData;
