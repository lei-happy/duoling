<template>
  <el-form
    class="generic-config-form"
    label-position="top"
    :model="{}"
    @submit.prevent
  >
    <el-form-item
      v-for="item in items"
      :key="item.configKey"
      :label="getConfigFieldLabel(item)"
    >
      <template v-if="item.valueType === 'enum'">
        <el-radio-group
          :model-value="item.configValue"
          @update:model-value="(val: string) => emitChange(item, val)"
        >
          <el-radio
            v-for="opt in getEnumOptions(item.configKey)"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </el-radio>
        </el-radio-group>
      </template>
      <template v-else-if="item.valueType === 'number'">
        <el-input-number
          :model-value="Number(item.configValue)"
          @update:model-value="(val: number) => emitChange(item, String(val))"
        />
      </template>
      <template v-else-if="item.valueType === 'boolean'">
        <el-switch
          :model-value="item.configValue === 'true'"
          @update:model-value="(val: boolean) => emitChange(item, String(val))"
        />
      </template>
      <template v-else>
        <el-input
          :model-value="item.configValue"
          style="max-width: 360px"
          @update:model-value="(val: string) => emitChange(item, val)"
        />
      </template>
      <div v-if="item.defaultValue" class="config-default">
        默认值：{{ getEnumDisplayLabel(item.configKey, item.defaultValue) }}
      </div>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
  import type { SystemConfig } from '@/api/system/config/model';
  import {
    getConfigFieldLabel,
    getEnumDisplayLabel,
    getEnumOptions
  } from '@/views/enterprise/config/constants';

  defineOptions({ name: 'GenericGroupSettings' });

  defineProps<{
    items: SystemConfig[];
  }>();

  const emit = defineEmits<{
    (e: 'config-change', item: SystemConfig, val: string): void;
  }>();

  const emitChange = (item: SystemConfig, val: string) => {
    emit('config-change', item, val);
  };
</script>

<style scoped>
  .generic-config-form :deep(.el-form-item__label) {
    padding-left: 0;
    margin-bottom: 4px;
    justify-content: flex-start;
  }

  .config-default {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    margin-top: 4px;
  }
</style>
