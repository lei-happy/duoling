<!--
  选地区，绑的是 biz_region 主键

  发布运力要传 `fromRegionId` / `toRegionIds`，后端据此解析省市与行政区划代码。
  所以这里不能用 `RegionsSelect`（它绑的是静态区划名/编码），必须走企业自己的
  地区库导航树，取到 `regionId`。

  只到市一级：省市足够找车的人判断是否顺路，让用户点到区县只是增加操作。
-->
<template>
  <el-cascader
    class="ele-fluid"
    :model-value="selected"
    :options="tree"
    :props="cascaderProps"
    :placeholder="placeholder"
    :loading="loading"
    :clearable="true"
    :filterable="true"
    :collapse-tags="multiple"
    :collapse-tags-tooltip="multiple"
    :max-collapse-tags="3"
    @update:model-value="onChange"
  />
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref, watch } from 'vue';
  import type { CascaderProps } from 'element-plus';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { RegionNavNode } from '@/api/basic-data/region/model';

  const props = withDefaults(
    defineProps<{
      /** 单选时是 regionId，多选时是 regionId 数组 */
      modelValue?: number | number[] | null;
      multiple?: boolean;
      placeholder?: string;
    }>(),
    { multiple: false, placeholder: '请选择' }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value: number | number[] | null): void;
    (e: 'change'): void;
  }>();

  const loading = ref(false);
  const tree = ref<RegionNavNode[]>([]);

  const cascaderProps = computed<CascaderProps>(() => ({
    value: 'regionId',
    label: 'name',
    children: 'children',
    emitPath: false,
    // 只选到省也算有效：跑「发浙江方向」的车不必指定到市
    checkStrictly: true,
    multiple: props.multiple
  }));

  const selected = computed(() =>
    props.multiple
      ? ((props.modelValue as number[] | null) ?? [])
      : ((props.modelValue as number | null) ?? null)
  );

  const onChange = (val: any) => {
    if (props.multiple) {
      emit('update:modelValue', Array.isArray(val) ? val.flat() : []);
    } else {
      emit('update:modelValue', (Array.isArray(val) ? val[0] : val) ?? null);
    }
    emit('change');
  };

  const load = async () => {
    if (tree.value.length) {
      return;
    }
    loading.value = true;
    try {
      tree.value = (await getRegionNavTree()) ?? [];
    } catch {
      // 地区树拿不到时留空，由外层表单的必填校验兜住
      tree.value = [];
    } finally {
      loading.value = false;
    }
  };

  watch(() => props.modelValue, load);

  onMounted(load);
</script>
