"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const CoverInput = require("./cover-input");
const CoverTextarea = require("./cover-textarea");
const CoverSelect = require("./cover-select");
const CoverMultipleSelect = require("./cover-multiple-select");
const CoverRadio = require("./cover-radio");
const CoverRadioButton = require("./cover-radio-button");
const CoverCheckbox = require("./cover-checkbox");
const CoverCheckboxButton = require("./cover-checkbox-button");
const CoverDate = require("./cover-date");
const CoverDatetime = require("./cover-datetime");
const CoverDaterange = require("./cover-daterange");
const CoverDatetimerange = require("./cover-datetimerange");
const CoverTime = require("./cover-time");
const CoverTimerange = require("./cover-timerange");
const CoverTimeSelect = require("./cover-time-select");
const CoverSwitch = require("./cover-switch");
const CoverInputNumber = require("./cover-input-number");
const CoverAutocomplete = require("./cover-autocomplete");
const CoverMention = require("./cover-mention");
const CoverCascader = require("./cover-cascader");
const CoverMultipleCascader = require("./cover-multiple-cascader");
const CoverRate = require("./cover-rate");
const CoverTransfer = require("./cover-transfer");
const CoverColorPicker = require("./cover-color-picker");
const CoverSlider = require("./cover-slider");
const CoverSliderRange = require("./cover-slider-range");
const CoverTreeSelect = require("./cover-tree-select");
const CoverTreeMultipleSelect = require("./cover-tree-multiple-select");
const CoverVirtualTreeSelect = require("./cover-virtual-tree-select");
const CoverVirtualTreeMultipleSelect = require("./cover-virtual-tree-multiple-select");
const CoverTableSelect = require("./cover-table-select");
const CoverTableMultipleSelect = require("./cover-table-multiple-select");
const CoverCheckCard = require("./cover-check-card");
const CoverMultipleCheckCard = require("./cover-multiple-check-card");
const CoverEditTag = require("./cover-edit-tag");
const CoverText = require("./cover-text");
const CoverLabel = require("./cover-label");
const CoverDivider = require("./cover-divider");
const CoverButton = require("./cover-button");
const CoverIcon = require("./cover-icon");
const CoverImage = require("./cover-image");
const CoverAlert = require("./cover-alert");
const CoverSteps = require("./cover-steps");
const CoverProTable = require("./cover-pro-table");
const CoverCard = require("./cover-card");
const CoverTable = require("./cover-table");
const CoverTabs = require("./cover-tabs");
const CoverRow = require("./cover-row");
const CoverCollapse = require("./cover-collapse");
const CoverCarousel = require("./cover-carousel");
const CoverDescriptions = require("./cover-descriptions");
const CoverDiv = require("./cover-div");
const covers = {
  input: vue.markRaw(CoverInput),
  textarea: vue.markRaw(CoverTextarea),
  select: vue.markRaw(CoverSelect),
  multipleSelect: vue.markRaw(CoverMultipleSelect),
  radio: vue.markRaw(CoverRadio),
  radioButton: vue.markRaw(CoverRadioButton),
  checkbox: vue.markRaw(CoverCheckbox),
  checkboxButton: vue.markRaw(CoverCheckboxButton),
  date: vue.markRaw(CoverDate),
  datetime: vue.markRaw(CoverDatetime),
  daterange: vue.markRaw(CoverDaterange),
  datetimerange: vue.markRaw(CoverDatetimerange),
  time: vue.markRaw(CoverTime),
  timerange: vue.markRaw(CoverTimerange),
  timeSelect: vue.markRaw(CoverTimeSelect),
  switch: vue.markRaw(CoverSwitch),
  inputNumber: vue.markRaw(CoverInputNumber),
  autocomplete: vue.markRaw(CoverAutocomplete),
  mention: vue.markRaw(CoverMention),
  cascader: vue.markRaw(CoverCascader),
  multipleCascader: vue.markRaw(CoverMultipleCascader),
  rate: vue.markRaw(CoverRate),
  transfer: vue.markRaw(CoverTransfer),
  colorPicker: vue.markRaw(CoverColorPicker),
  slider: vue.markRaw(CoverSlider),
  sliderRange: vue.markRaw(CoverSliderRange),
  treeSelect: vue.markRaw(CoverTreeSelect),
  treeMultipleSelect: vue.markRaw(CoverTreeMultipleSelect),
  virtualTreeSelect: vue.markRaw(CoverVirtualTreeSelect),
  virtualTreeMultipleSelect: vue.markRaw(CoverVirtualTreeMultipleSelect),
  tableSelect: vue.markRaw(CoverTableSelect),
  tableMultipleSelect: vue.markRaw(CoverTableMultipleSelect),
  checkCard: vue.markRaw(CoverCheckCard),
  multipleCheckCard: vue.markRaw(CoverMultipleCheckCard),
  editTag: vue.markRaw(CoverEditTag),
  text: vue.markRaw(CoverText),
  label: vue.markRaw(CoverLabel),
  divider: vue.markRaw(CoverDivider),
  button: vue.markRaw(CoverButton),
  icon: vue.markRaw(CoverIcon),
  image: vue.markRaw(CoverImage),
  alert: vue.markRaw(CoverAlert),
  steps: vue.markRaw(CoverSteps),
  proTable: vue.markRaw(CoverProTable),
  card: vue.markRaw(CoverCard),
  table: vue.markRaw(CoverTable),
  tabs: vue.markRaw(CoverTabs),
  row: vue.markRaw(CoverRow),
  collapse: vue.markRaw(CoverCollapse),
  carousel: vue.markRaw(CoverCarousel),
  descriptions: vue.markRaw(CoverDescriptions),
  div: vue.markRaw(CoverDiv)
};
exports.covers = covers;
