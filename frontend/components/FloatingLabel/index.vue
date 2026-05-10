<!-- 浮动标签输入框组件 -->
<template>
  <div 
    class="floating-label-wrapper"
    :class="{
      'is-focused': isFocused,
      'has-value': hasValue,
      'is-disabled': disabled,
      'is-date-picker': type === 'date',
      'is-select': type === 'select',
      'is-cascader': type === 'cascader'
    }"
  >
    <el-input
      v-if="type === 'input'"
      ref="inputRef"
      v-model="model"
      :clearable="clearable"
      :disabled="disabled"
      :maxlength="maxlength"
      :show-word-limit="showWordLimit"
      :type="inputType"
      @focus="handleFocus"
      @blur="handleBlur"
      @clear="handleClear"
    />
    
    <el-date-picker
      v-else-if="type === 'date'"
      ref="datePickerRef"
      v-model="model"
      :type="dateType"
      :clearable="clearable"
      :disabled="disabled"
      :unlink-panels="unlinkPanels"
      :range-separator="rangeSeparator"
      :value-format="valueFormat"
      :format="format"
      :start-placeholder="startPlaceholder"
      :end-placeholder="endPlaceholder"
      class="ele-fluid"
      @focus="handleFocus"
      @blur="handleBlur"
      @clear="handleClear"
    />

    <el-cascader
      v-else-if="type === 'cascader'"
      ref="cascaderRef"
      v-model="model"
      :options="cascaderOptionsList"
      :props="cascaderOptionProps"
      :clearable="clearable"
      :disabled="disabled"
      :filterable="cascaderFilterable"
      class="ele-fluid"
      @focus="handleFocus"
      @blur="handleBlur"
      @visible-change="handleCascaderVisible"
      @change="$emit('change', $event)"
    />

    <el-select
      v-else-if="type === 'select'"
      ref="selectRef"
      v-model="model"
      :clearable="clearable"
      :disabled="disabled"
      :multiple="multiple"
      :collapse-tags="collapseTags"
      :collapse-tags-tooltip="collapseTagsTooltip"
      :filterable="filterable"
      :filter-method="filterMethod"
      :remote="remote"
      :remote-method="remoteMethod"
      :loading="loading"
      :teleported="teleported"
      class="ele-fluid"
      @focus="handleFocus"
      @blur="handleBlur"
      @clear="handleClear"
      @visible-change="handleVisibleChange"
      @change="$emit('change', $event)"
    >
      <slot></slot>
    </el-select>

    <label class="floating-label" @click="handleLabelClick">
      {{ displayLabel }}
    </label>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import type { CascaderProps, InputInstance } from 'element-plus';

  defineOptions({ name: 'FloatingLabel' });

  /** 需要自动去除的前缀列表 */
  const LABEL_PREFIXES = ['请输入', '请选择', '请填写', '请选择或输入'];

  const props = withDefaults(
    defineProps<{
      /** 标签文本（初始状态显示） */
      label: string;
      /** 激活状态的标签文本（可选，不传则自动从 label 提取） */
      floatedLabel?: string;
      /** 组件类型 */
      type?: 'input' | 'date' | 'select' | 'cascader';
      /** 是否禁用 */
      disabled?: boolean;
      /** 是否可清除 */
      clearable?: boolean;
      /** 输入框类型 */
      inputType?: 'text' | 'textarea' | 'password' | 'number';
      /** 最大长度 */
      maxlength?: number;
      /** 是否显示字数统计 */
      showWordLimit?: boolean;
      /** 日期选择器类型 */
      dateType?: 'date' | 'datetime' | 'datetimerange' | 'daterange' | 'month' | 'monthrange';
      /** 日期范围是否独立面板 */
      unlinkPanels?: boolean;
      /** 日期范围分隔符 */
      rangeSeparator?: string;
      /** 日期格式化（绑定值格式） */
      valueFormat?: string;
      /** 显示格式（输入框中显示的格式） */
      format?: string;
      /** 日期范围开始占位符 */
      startPlaceholder?: string;
      /** 日期范围结束占位符 */
      endPlaceholder?: string;
      /** 下拉选择器是否多选 */
      multiple?: boolean;
      /** 多选时是否折叠标签 */
      collapseTags?: boolean;
      /** 多选折叠时是否显示tooltip */
      collapseTagsTooltip?: boolean;
      /** 下拉选择器是否可搜索 */
      filterable?: boolean;
      /** 下拉选择器是否远程搜索 */
      remote?: boolean;
      /** 远程搜索方法 */
      remoteMethod?: (query: string) => void;
      /** 本地可搜索时的自定义过滤方法（与 filterable 联用） */
      filterMethod?: (query: string) => void;
      /** 远程搜索加载状态 */
      loading?: boolean;
      /** 下拉选择器是否插入body */
      teleported?: boolean;
      /** 级联选项（type=cascader） */
      cascaderOptions?: any[];
      /** 透传给 el-cascader 的 props（如 value/label/children、emitPath 等） */
      cascaderOptionProps?: CascaderProps;
      /** 级联是否可筛选 */
      cascaderFilterable?: boolean;
    }>(),
    {
      type: 'input',
      clearable: true,
      inputType: 'text',
      dateType: 'date',
      rangeSeparator: '-',
      multiple: false,
      collapseTags: true,
      collapseTagsTooltip: true,
      filterable: false,
      remote: false,
      loading: false,
      teleported: true,
      cascaderFilterable: true
    }
  );

  /** 事件定义 */
  const emit = defineEmits<{
    (e: 'visible-change', visible: boolean): void;
    (e: 'change', value: any): void;
  }>();

  /** 绑定值 */
  const model = defineModel<any>();

  const cascaderOptionsList = computed(() => props.cascaderOptions ?? []);

  /** 输入框引用 */
  const inputRef = ref<InputInstance>();
  const datePickerRef = ref<any>();
  const selectRef = ref<any>();
  const cascaderRef = ref<any>();

  /** 是否聚焦 */
  const isFocused = ref(false);

  /** 是否有值 */
  const hasValue = computed(() => {
    const value = model.value;
    if (value == null || value === '') {
      return false;
    }
    if (Array.isArray(value)) {
      return value.length > 0 && value.every(v => v != null && v !== '');
    }
    return true;
  });

  /** 激活状态的标签文本（去除前缀） */
  const activeLabel = computed(() => {
    // 如果明确指定了 floatedLabel，优先使用
    if (props.floatedLabel) {
      return props.floatedLabel;
    }
    // 否则自动去除常见前缀
    let text = props.label;
    for (const prefix of LABEL_PREFIXES) {
      if (text.startsWith(prefix)) {
        return text.substring(prefix.length);
      }
    }
    return text;
  });

  /** 根据状态显示的标签文本 */
  const displayLabel = computed(() => {
    // 激活状态（聚焦或有值）时显示简化的标签
    if (isFocused.value || hasValue.value) {
      return activeLabel.value;
    }
    // 初始状态显示完整的 label
    return props.label;
  });

  /** 聚焦事件 */
  const handleFocus = () => {
    isFocused.value = true;
  };

  /** 失焦事件 */
  const handleBlur = () => {
    isFocused.value = false;
  };

  /** 清除事件 */
  const handleClear = () => {
    isFocused.value = false;
  };

  /** 下拉框显示/隐藏事件 */
  const handleVisibleChange = (visible: boolean) => {
    isFocused.value = visible;
    // 向外透传事件，支持懒加载等场景
    emit('visible-change', visible);
  };

  const handleCascaderVisible = (visible: boolean) => {
    isFocused.value = visible;
    emit('visible-change', visible);
  };

  /** 标签点击事件 */
  const handleLabelClick = () => {
    if (props.disabled) {
      return;
    }
    if (props.type === 'input') {
      inputRef.value?.focus();
    } else if (props.type === 'date') {
      datePickerRef.value?.focus();
    } else if (props.type === 'select') {
      selectRef.value?.focus();
    } else if (props.type === 'cascader') {
      cascaderRef.value?.focus?.();
    }
  };
</script>

<style scoped lang="scss">
.floating-label-wrapper {
  position: relative;
  width: 100%;

  .floating-label {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--el-text-color-placeholder);
    font-size: 14px;
    pointer-events: none;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    background-color: transparent;
    padding: 0;
    white-space: nowrap;
    z-index: 1;
    cursor: text;
    line-height: 1;
  }

  // 日期选择器的标签位置需要避开左侧图标
  &.is-date-picker .floating-label {
    left: 34px; // 日期图标宽度约30px，加上间距
  }

  // 聚焦或有值时的标签样式
  &.is-focused .floating-label,
  &.has-value .floating-label {
    top: 0;
    left: 8px;
    font-size: 12px;
    color: var(--el-color-primary);
    transform: translateY(-50%);
    background-color: var(--el-fill-color-blank);
    padding: 2px 4px;
    z-index: 2;
  }

  // 有值但未聚焦：标签再弱一档，贴近占位符层次，与输入正文区分更明显
  &.has-value:not(.is-focused) .floating-label {
    color: var(--el-text-color-placeholder);
  }

  // 禁用状态
  &.is-disabled .floating-label {
    color: var(--el-text-color-disabled);
    cursor: not-allowed;
  }

  // 隐藏原生的 placeholder
  :deep(.el-input__inner::placeholder),
  :deep(.el-range-input::placeholder) {
    opacity: 0;
  }

  // 下拉选择器：只在未选中时隐藏 placeholder
  &:not(.has-value) :deep(.el-select__placeholder) {
    opacity: 0;
  }

  // 聚焦或有值时显示原生 placeholder（用于日期范围的提示）
  &.is-focused :deep(.el-range-input::placeholder) {
    opacity: 1;
  }

  // 确保日期选择器的输入框占满宽度
  :deep(.el-date-editor) {
    width: 100%;
  }

  // 调整范围选择器的样式
  :deep(.el-range-editor) {
    width: 100%;
  }

  // 确保下拉选择器占满宽度
  :deep(.el-select) {
    width: 100%;
  }

  :deep(.el-cascader) {
    width: 100%;
  }

  &.is-cascader:not(.has-value) :deep(.el-input__inner::placeholder) {
    opacity: 0;
  }

  // 聚焦时保持细边框，避免默认的加粗效果
  :deep(.el-input__wrapper:focus-within),
  :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px var(--el-color-primary) inset !important;
  }

  :deep(.el-select__wrapper:focus-within),
  :deep(.el-select__wrapper.is-focused) {
    box-shadow: 0 0 0 1px var(--el-color-primary) inset !important;
  }

  :deep(.el-range-editor.is-active) {
    box-shadow: 0 0 0 1px var(--el-color-primary) inset !important;
  }
}
</style>

