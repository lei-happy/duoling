<!-- 省市区级联选择 -->
<template>
  <template v-if="component === 'text'">
    <span v-if="typeof valueLabels === 'string'">{{ valueLabels }}</span>
    <el-space v-else :wrap="true">
      <el-tag
        v-for="label in valueLabels"
        :key="label"
        :disable-transitions="true"
        size="small"
        type="info"
      >
        {{ label }}
      </el-tag>
    </el-space>
  </template>
  <el-cascader
    v-else
    ref="cascaderRef"
    :size="size"
    :disabled="disabled"
    :clearable="clearable"
    v-model="model"
    :options="cascaderData"
    :filterable="filterable"
    :placeholder="placeholder"
    :props="regionCascaderProps"
    popper-class="ele-popper-higher"
    :collapse-tags="collapseTags"
    :max-collapse-tags="maxCollapseTags"
    :collapse-tags-tooltip="collapseTagsTooltip"
    :showAllLevels="showAllLevels"
    :separator="separator"
    :teleported="teleported"
    class="ele-fluid"
  />
</template>

<script lang="ts" setup>
  import { ref, computed, reactive, watch } from 'vue';
  import type {
    ElCascaderProps,
    ElCascaderInstance
  } from 'ele-admin-plus/es/ele-app/el';
  import type { CascaderProps } from 'element-plus';
  import type { RegionsData } from './util';
  import { useRegionsData, filterData, getValueLabel } from './util';

  defineOptions({ name: 'RegionsSelect' });

  const props = withDefaults(
    defineProps<{
      /** 自定义省市区数据 */
      options?: RegionsData[];
      /** 选中值对应的字段名 */
      valueField?: 'value' | 'label';
      /** 类型, 省市选择或省选择 */
      type?: 'provinceCity' | 'province';
      /** 是否多选 */
      multiple?: boolean;
      /** 组件类型 */
      component?: 'text' | 'cascader';
      /** 提示文本 */
      placeholder?: string;
      /** 是否禁用 */
      disabled?: boolean;
      /** 是否可清除 */
      clearable?: boolean;
      /** 是否可搜索 */
      filterable?: boolean;
      /** 级联面板属性 */
      cascaderProps?: ElCascaderProps;
      /** 多选是否折叠标签 */
      collapseTags?: boolean;
      /** 多选最大显示标签数量 */
      maxCollapseTags?: number;
      /** 多选标签折叠时是否显示提示 */
      collapseTagsTooltip?: boolean;
      /** 显示所有选中路径 */
      showAllLevels?: boolean;
      /** 路径分隔符 */
      separator?: string;
      /** 下拉框是否插入body */
      teleported?: boolean;
      /** 尺寸 */
      size?: 'small' | 'default' | 'large';
    }>(),
    {
      clearable: true,
      filterable: true,
      collapseTags: true,
      maxCollapseTags: 5,
      showAllLevels: true,
      teleported: true
    }
  );

  /** 选中值 */
  const model = defineModel<string[] | string[][]>({ type: Array });

  /** 省市区数据 */
  const regionsData = useRegionsData();

  /** 级联选择器实例 */
  const cascaderRef = ref<ElCascaderInstance>(null);

  /** 级联选择器级联面板属性 */
  const regionCascaderProps = reactive<CascaderProps>({
    ...(props.cascaderProps || {}),
    multiple: props.multiple || !!props.cascaderProps?.multiple
  });

  /** 级联选择器数据 */
  const cascaderData = computed<any>(() => {
    const data = props.options ?? regionsData.value ?? [];
    return filterData(data, props.type, props.valueField);
  });

  /** 选中值对应的文本 */
  const valueLabels = computed<string | string[]>(() => {
    const separator = ' / ';
    const values = model.value;
    if (values && values.length && Array.isArray(values[0])) {
      const result: string[] = [];
      (values as Array<string[]>).forEach((v) => {
        const labels = getValueLabel(v, cascaderData.value);
        result.push(labels.join(separator));
      });
      return result;
    }
    const labels = getValueLabel(values as string[], cascaderData.value);
    return labels.join(separator);
  });

  /** 同步级联选择器级联面板属性 */
  watch(
    () => props.cascaderProps,
    (cascaderProps) => {
      const cProps = cascaderProps || {};
      [
        'expandTrigger',
        'checkStrictly',
        'emitPath',
        'lazy',
        'lazyLoad',
        'value',
        'label',
        'children',
        'disabled',
        'leaf',
        'hoverThreshold'
      ].forEach((k) => {
        if (regionCascaderProps[k] == null && cProps[k] == null) {
          return;
        }
        if (regionCascaderProps[k] !== cProps[k]) {
          regionCascaderProps[k] = cProps[k];
        }
      });
      if (props.multiple) {
        if (!regionCascaderProps.multiple) {
          regionCascaderProps.multiple = true;
        }
      } else if (!!regionCascaderProps.multiple !== !!cProps.multiple) {
        regionCascaderProps.multiple = cProps.multiple;
      }
    },
    {
      immediate: true,
      deep: true
    }
  );

  defineExpose({
    cascaderRef,
    getCheckedNodes: (leafOnly?: boolean) => {
      return cascaderRef.value?.getCheckedNodes?.(!!leafOnly);
    }
  });
</script>
