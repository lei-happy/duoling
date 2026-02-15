import { markRaw } from 'vue';
import type { ComponentItem } from 'ele-admin-plus/es/ele-pro-form-builder/types';
import { defaultComponentData as componentData } from 'ele-admin-plus/es/ele-pro-form-builder/util';
import {
  codeTips,
  vIfCodeTips
} from 'ele-admin-plus/es/ele-pro-form-builder/components/component-data';
import CoverDictCheckbox from './covers/cover-dict-checkbox.vue';
import CoverDictMultipleSelect from './covers/cover-dict-multiple-select.vue';
import CoverDictRadio from './covers/cover-dict-radio.vue';
import CoverDictSelect from './covers/cover-dict-select.vue';
import CoverEditor from './covers/cover-editor.vue';
import CoverFileUpload from './covers/cover-file-upload.vue';
import CoverIconSelect from './covers/cover-icon-select.vue';
import CoverImageUpload from './covers/cover-image-upload.vue';
import CoverMultipleRegions from './covers/cover-multiple-regions.vue';
import CoverRegions from './covers/cover-regions.vue';

/**
 * 自定义的组件
 */
const additionalItems: ComponentItem[] = [
  {
    type: 'iconSelect',
    name: '图标选择',
    cover: markRaw(CoverIconSelect),
    presetProps: { popperWidth: 414, popperHeight: 260 },
    defaultProps: {},
    initialProps: {
      popperWidth: 480,
      popperHeight: 388,
      filterable: 'popper',
      gridStyle: { gridTemplateColumns: 'repeat(6, 1fr)' }
    },
    reservedProps: {},
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'input'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '占位文本',
        prop: 'props.placeholder',
        type: 'input'
      },
      {
        label: '清除按钮',
        prop: 'props.clearable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '事件设置',
        prop: 'groupEventsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '选中值改变',
        prop: 'props.onChange',
        type: 'proFormBuilderEventEdit',
        props: {
          title: '设置 change 事件',
          codeTips,
          codePlaceholder: '(value) => {\n\n}'
        }
      },
      {
        label: '下拉框出现/隐藏',
        prop: 'props.onVisibleChange',
        type: 'proFormBuilderEventEdit',
        props: {
          title: '设置 visibleChange 事件',
          codeTips,
          codePlaceholder: '(visible) => {\n\n}'
        }
      },
      {
        label: '清空按钮点击',
        prop: 'props.onClear',
        type: 'proFormBuilderEventEdit',
        props: {
          title: '设置 clear 事件',
          codeTips,
          codePlaceholder: '() => {\n\n}'
        }
      },
      {
        label: '失去焦点',
        prop: 'props.onBlur',
        type: 'proFormBuilderEventEdit',
        props: {
          title: '设置 blur 事件',
          codeTips,
          codePlaceholder: '(enent) => {\n\n}'
        }
      },
      {
        label: '获得焦点',
        prop: 'props.onFocus',
        type: 'proFormBuilderEventEdit',
        props: {
          title: '设置 focus 事件',
          codeTips,
          codePlaceholder: '(enent) => {\n\n}'
        }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'EleIconSelect',
    componentImport: `import IconSelect from '@/components/IconSelect/index.vue';`
  },
  {
    type: 'regions',
    name: '省市区选择',
    cover: markRaw(CoverRegions),
    presetProps: {
      type: 'default',
      valueField: 'value',
      clearable: true,
      filterable: true,
      separator: '/',
      showAllLevels: true,
      cascaderProps: { expandTrigger: 'click' }
    },
    defaultProps: {},
    initialProps: { placeholder: '' },
    reservedProps: {},
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'editTag'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '占位文本',
        prop: 'props.placeholder',
        type: 'input'
      },
      {
        label: '清除按钮',
        prop: 'props.clearable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否可搜索',
        prop: 'props.filterable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '类型',
        prop: 'props.type',
        type: 'checkCard',
        props: {
          items: [
            { value: 'default', label: '省市区选择' },
            { value: 'provinceCity', label: '省市选择' },
            { value: 'province', label: '省选择' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card is-loose'
        }
      },
      {
        label: '值类型',
        prop: 'props.valueField',
        type: 'checkCard',
        props: {
          items: [
            { value: 'value', label: '区号' },
            { value: 'label', label: '名称' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '显示选中值完整路径',
        prop: 'props.showAllLevels',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '选项分隔符',
        prop: 'props.separator',
        type: 'input'
      },
      {
        label: '父子节点不关联',
        prop: 'props.cascaderProps.checkStrictly',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '次级菜单展开方式',
        prop: 'props.cascaderProps.expandTrigger',
        type: 'checkCard',
        props: {
          items: [
            { label: '点击', value: 'click' },
            { label: '鼠标移入', value: 'hover' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card is-loose'
        }
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'RegionsSelect',
    componentImport: `import RegionsSelect from '@/components/RegionsSelect/index.vue';`
  },
  {
    type: 'multipleRegions',
    name: '省市区多选',
    cover: markRaw(CoverMultipleRegions),
    presetProps: {
      type: 'default',
      valueField: 'value',
      clearable: true,
      filterable: true,
      separator: '/',
      showAllLevels: true,
      collapseTags: true,
      maxCollapseTags: 5,
      cascaderProps: { expandTrigger: 'click' }
    },
    defaultProps: {},
    initialProps: { placeholder: '' },
    reservedProps: { multiple: true },
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'proFormBuilderJsonInput',
        props: { placeholder: '输入 JSON 格式' }
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '占位文本',
        prop: 'props.placeholder',
        type: 'input'
      },
      {
        label: '清除按钮',
        prop: 'props.clearable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否可搜索',
        prop: 'props.filterable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '类型',
        prop: 'props.type',
        type: 'checkCard',
        props: {
          items: [
            { value: 'default', label: '省市区选择' },
            { value: 'provinceCity', label: '省市选择' },
            { value: 'province', label: '省选择' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card is-loose'
        }
      },
      {
        label: '值类型',
        prop: 'props.valueField',
        type: 'checkCard',
        props: {
          items: [
            { value: 'value', label: '区号' },
            { value: 'label', label: '名称' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '显示选中值完整路径',
        prop: 'props.showAllLevels',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '选项分隔符',
        prop: 'props.separator',
        type: 'input'
      },
      {
        label: '父子节点不关联',
        prop: 'props.cascaderProps.checkStrictly',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '次级菜单展开方式',
        prop: 'props.cascaderProps.expandTrigger',
        type: 'checkCard',
        props: {
          items: [
            { label: '点击', value: 'click' },
            { label: '鼠标移入', value: 'hover' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card is-loose'
        }
      },
      {
        label: '折叠显示 Tag',
        prop: 'props.collapseTags',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '最大显示 Tag 数量',
        prop: 'props.maxCollapseTags',
        type: 'inputNumber',
        props: { min: 1, step: 1, stepStrictly: true }
      },
      {
        label: '悬浮显示折叠的 Tag',
        prop: 'props.collapseTagsTooltip',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'RegionsSelect',
    componentImport: `import RegionsSelect from '@/components/RegionsSelect/index.vue';`
  },
  {
    type: 'imageUpload',
    name: '图片上传',
    cover: markRaw(CoverImageUpload),
    presetProps: { sortable: true, drag: true, fileLimit: 100 },
    defaultProps: {},
    initialProps: { limit: 3 },
    reservedProps: {},
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'textarea'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '是否只读',
        prop: 'props.readonly',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '最大上传数量',
        prop: 'props.limit',
        type: 'inputNumber',
        props: { min: 1, step: 1, stepStrictly: true }
      },
      {
        label: '文件大小限制',
        prop: 'props.fileLimit',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '可多选文件',
        prop: 'props.multiple',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '可拖拽上传',
        prop: 'props.drag',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '可拖拽排序',
        prop: 'props.sortable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '图片适应模式',
        prop: 'props.imageProps.fit',
        type: 'checkCard',
        props: {
          items: [
            { value: 'fill', label: 'fill' },
            { value: 'contain', label: 'contain' },
            { value: 'cover', label: 'cover' },
            { value: 'none', label: 'none' },
            { value: 'scale-down', label: 'scale-down' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card is-loose'
        }
      },
      {
        label: '图片项样式',
        prop: 'props.itemStyle',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '上传按钮样式',
        prop: 'props.buttonStyle',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'ImageUpload',
    componentImport: `import ImageUpload from '@/components/ImageUpload/index.vue';`
  },
  {
    type: 'fileUpload',
    name: '附件上传',
    cover: markRaw(CoverFileUpload),
    presetProps: { sortable: true, drag: true, fileLimit: 100 },
    defaultProps: {},
    initialProps: { limit: 6 },
    reservedProps: {},
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'textarea'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '是否只读',
        prop: 'props.readonly',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '最大上传数量',
        prop: 'props.limit',
        type: 'inputNumber',
        props: { min: 1, step: 1, stepStrictly: true }
      },
      {
        label: '文件大小限制',
        prop: 'props.fileLimit',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '可多选文件',
        prop: 'props.multiple',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '可拖拽上传',
        prop: 'props.drag',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '可拖拽排序',
        prop: 'props.sortable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '文件项样式',
        prop: 'props.itemStyle',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '上传按钮样式',
        prop: 'props.buttonStyle',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'FileUpload',
    componentImport: `import FileUpload from '@/components/FileUpload/index.vue';`
  },
  {
    type: 'dictRadio',
    name: '字典单选',
    cover: markRaw(CoverDictRadio),
    presetProps: {},
    defaultProps: {},
    initialProps: { code: 'sex' },
    reservedProps: { type: 'radio' },
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'input'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '字典类型值',
        prop: 'props.code',
        type: 'input'
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'DictData'
  },
  {
    type: 'dictCheckbox',
    name: '字典多选',
    cover: markRaw(CoverDictCheckbox),
    presetProps: {},
    defaultProps: {},
    initialProps: { code: 'sex' },
    reservedProps: { type: 'checkbox' },
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'editTag'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '字典类型值',
        prop: 'props.code',
        type: 'input'
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'DictData'
  },
  {
    type: 'dictSelect',
    name: '字典下拉',
    cover: markRaw(CoverDictSelect),
    presetProps: { clearable: true },
    defaultProps: {},
    initialProps: { code: 'sex' },
    reservedProps: { type: 'select' },
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'input'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '占位文本',
        prop: 'props.placeholder',
        type: 'input'
      },
      {
        label: '清除按钮',
        prop: 'props.clearable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否可搜索',
        prop: 'props.filterable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '字典类型值',
        prop: 'props.code',
        type: 'input'
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'DictData'
  },
  {
    type: 'dictMultipleSelect',
    name: '字典下拉多选',
    cover: markRaw(CoverDictMultipleSelect),
    presetProps: { clearable: true },
    defaultProps: {},
    initialProps: { code: 'sex' },
    reservedProps: { type: 'multipleSelect' },
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'editTag'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '占位文本',
        prop: 'props.placeholder',
        type: 'input'
      },
      {
        label: '清除按钮',
        prop: 'props.clearable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '是否可搜索',
        prop: 'props.filterable',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '字典类型值',
        prop: 'props.code',
        type: 'input'
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'DictData'
  },
  {
    type: 'editor',
    name: '富文本',
    cover: markRaw(CoverEditor),
    presetProps: {},
    defaultProps: {},
    initialProps: { init: { height: 380 } },
    reservedProps: {},
    configForm: [
      {
        label: '基础配置',
        prop: 'groupBasicLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件类型',
        prop: 'type',
        type: 'proFormBuilderTypeEdit'
      },
      {
        label: '字段名称',
        prop: 'label',
        type: 'input'
      },
      {
        label: '字段属性',
        prop: 'prop',
        type: 'input'
      },
      {
        label: '是否必填',
        prop: 'required',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '必填校验信息',
        prop: 'requiredMessage',
        type: 'input'
      },
      {
        label: '初始值',
        prop: 'initValue',
        type: 'textarea'
      },
      {
        label: '标签宽度',
        prop: 'itemProps.labelWidth',
        type: 'inputNumber',
        props: { min: 0 }
      },
      {
        label: '标签位置',
        prop: 'itemProps.labelPosition',
        type: 'checkCard',
        props: {
          items: [
            { value: 'left', label: '左对齐' },
            { value: 'right', label: '右对齐' },
            { value: 'top', label: '顶部' }
          ],
          class: 'ele-pro-form-builder-props-options-check-card'
        }
      },
      {
        label: '组件属性',
        prop: 'groupPropsLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '是否禁用',
        prop: 'props.disabled',
        type: 'switch',
        props: { activeValue: true, inactiveValue: false }
      },
      {
        label: '样式设置',
        prop: 'groupStylesLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '组件样式',
        prop: 'props.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '组件类名',
        prop: 'props.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '表单项样式',
        prop: 'itemProps.style',
        type: 'proFormBuilderStyleEdit'
      },
      {
        label: '表单项类名',
        prop: 'itemProps.class',
        type: 'proFormBuilderStyleEdit',
        props: { isClass: true }
      },
      {
        label: '高级设置',
        prop: 'groupAdvancedLabel',
        type: 'label',
        props: { class: 'ele-pro-form-builder-props-group-label' }
      },
      {
        label: '显示条件',
        prop: 'vIf',
        type: 'proFormBuilderIfEdit',
        props: {
          title: '设置显示条件',
          codeTips: vIfCodeTips
        }
      },
      {
        label: '开发者选项',
        prop: '__sourceCode',
        type: 'proFormBuilderSourceEdit',
        props: { title: '编辑源码' }
      }
    ],
    componentName: 'TinymceEditor',
    componentImport: `import TinymceEditor from '@/components/TinymceEditor/index.vue';`
  }
];

/**
 * 表单组件库数据
 */
export const defaultComponentData = componentData.map(
  (groupItem, groupIndex) => ({
    ...groupItem,
    items: (groupIndex !== 0
      ? groupItem.items
      : [
          ...groupItem.items.slice(0, groupItem.items.length - 1),
          ...additionalItems, // 插入自定义的组件数据
          groupItem.items[groupItem.items.length - 1]
        ]
    ).map((item) => ({
      ...item,
      initialProps:
        // 图标组件添加时设置默认值
        item.type === 'icon'
          ? { ...item.initialProps, name: 'IconProUserOutlined' }
          : item.initialProps
    }))
  })
);
