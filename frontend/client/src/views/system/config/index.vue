<template>
  <ele-page>
    <ele-card
      v-for="group in groups"
      :key="group.name"
      :header="group.label"
      :body-style="{ padding: '16px 24px' }"
      style="margin-bottom: 16px"
    >
      <el-form label-width="180px" :model="{}" @submit.prevent>
        <el-form-item
          v-for="item in group.items"
          :key="item.configKey"
          :label="item.description || item.configKey"
        >
          <template v-if="item.valueType === 'enum'">
            <el-radio-group
              :model-value="item.configValue"
              @update:model-value="(val: string) => handleChange(item, val)"
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
              @update:model-value="(val: number) => handleChange(item, String(val))"
            />
          </template>
          <template v-else-if="item.valueType === 'boolean'">
            <el-switch
              :model-value="item.configValue === 'true'"
              @update:model-value="(val: boolean) => handleChange(item, String(val))"
            />
          </template>
          <template v-else>
            <el-input
              :model-value="item.configValue"
              style="max-width: 360px"
              @update:model-value="(val: string) => handleChange(item, val)"
            />
          </template>
          <div v-if="item.defaultValue" class="config-default">
            默认值：{{ getDisplayLabel(item.configKey, item.defaultValue) }}
          </div>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card v-if="!groups.length && !loading" :body-style="{ padding: '40px' }">
      <el-empty description="暂无配置项" />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { listConfigs, updateConfig } from '@/api/system/config';
  import type { SystemConfig } from '@/api/system/config/model';

  defineOptions({ name: 'SystemConfig' });

  const loading = ref(false);
  const configs = ref<SystemConfig[]>([]);

  const ENUM_OPTIONS: Record<string, { value: string; label: string }[]> = {
    'waybill.freight_calc_mode': [
      { value: 'auto_required', label: '强制自动计费' },
      { value: 'auto_preferred', label: '优先自动，允许手动' },
      { value: 'manual_only', label: '仅手动填写' }
    ]
  };

  const GROUP_LABELS: Record<string, string> = {
    waybill: '运单设置'
  };

  const getEnumOptions = (key: string) => {
    return ENUM_OPTIONS[key] || [];
  };

  const getDisplayLabel = (key: string, value: string) => {
    const opts = ENUM_OPTIONS[key];
    if (opts) {
      const opt = opts.find((o) => o.value === value);
      if (opt) return opt.label;
    }
    return value;
  };

  const groups = computed(() => {
    const map = new Map<string, SystemConfig[]>();
    for (const c of configs.value) {
      const g = c.configGroup || 'default';
      if (!map.has(g)) map.set(g, []);
      map.get(g)!.push(c);
    }
    return Array.from(map.entries()).map(([name, items]) => ({
      name,
      label: GROUP_LABELS[name] || name,
      items
    }));
  });

  const query = () => {
    loading.value = true;
    listConfigs()
      .then((data) => {
        configs.value = data ?? [];
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      })
      .finally(() => {
        loading.value = false;
      });
  };

  const handleChange = (item: SystemConfig, val: string) => {
    const oldValue = item.configValue;
    item.configValue = val;
    updateConfig(item.configKey, val)
      .then(() => {
        EleMessage.success({ message: '保存成功', plain: true });
      })
      .catch((e) => {
        item.configValue = oldValue;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  onMounted(() => {
    query();
  });
</script>

<style scoped>
  .config-default {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    margin-top: 4px;
  }
</style>
