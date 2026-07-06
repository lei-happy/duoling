<!-- 经营主体选择器（各业务表单归属选择 / 列表筛选复用） -->
<template>
  <el-select
    :model-value="modelValue ?? void 0"
    :placeholder="placeholder"
    :clearable="clearable"
    :disabled="disabled"
    filterable
    style="width: 100%"
    @update:model-value="onChange"
  >
    <el-option
      v-for="item in options"
      :key="item.id"
      :label="optionLabel(item)"
      :value="item.id"
    />
  </el-select>
</template>

<script lang="ts" setup>
  import { ref, watch, onMounted } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { listBusinessEntityOptions } from '@/api/system/business-entity';
  import type { BusinessEntityOption } from '@/api/system/business-entity/model';

  defineOptions({ name: 'BusinessEntitySelect' });

  const props = withDefaults(
    defineProps<{
      modelValue?: number | null;
      placeholder?: string;
      clearable?: boolean;
      disabled?: boolean;
      /** 无值时是否自动选中默认主体 */
      autoDefault?: boolean;
    }>(),
    {
      placeholder: '请选择经营主体',
      clearable: true,
      disabled: false,
      autoDefault: false
    }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: number): void;
    (e: 'change', value?: number, item?: BusinessEntityOption): void;
  }>();

  const options = ref<BusinessEntityOption[]>([]);

  const optionLabel = (item: BusinessEntityOption) =>
    item.shortName
      ? `${item.entityName}（${item.shortName}）`
      : item.entityName;

  const onChange = (value?: number) => {
    emit('update:modelValue', value);
    emit(
      'change',
      value,
      options.value.find((o) => o.id === value)
    );
  };

  const loadOptions = async () => {
    try {
      options.value = await listBusinessEntityOptions();
      if (
        props.autoDefault &&
        (props.modelValue == null || props.modelValue === void 0)
      ) {
        const def =
          options.value.find((o) => o.isDefault === 1) || options.value[0];
        if (def) {
          onChange(def.id);
        }
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  watch(
    () => props.autoDefault,
    () => {
      if (
        props.autoDefault &&
        props.modelValue == null &&
        options.value.length
      ) {
        const def =
          options.value.find((o) => o.isDefault === 1) || options.value[0];
        if (def) {
          onChange(def.id);
        }
      }
    }
  );

  onMounted(loadOptions);
</script>
