<template>
  <div class="finance-settings">
    <div class="finance-settings__intro">
      勾选每类费用单允许在<strong>哪些任务节点</strong>发起。未勾选的节点：开启下方「强制拦截」后将无法发起，关闭时仅在操作界面隐藏入口、不阻断。
    </div>

    <div class="finance-settings__enforce">
      <el-switch
        v-model="enforce"
        :active-value="true"
        :inactive-value="false"
      />
      <div class="finance-settings__enforce-text">
        <div class="finance-settings__enforce-title">强制拦截不合规的发起</div>
        <div class="finance-settings__enforce-desc">
          开启后，在未勾选的节点提交费用单会被拦截；关闭时仅在界面引导，允许保存。
        </div>
      </div>
    </div>

    <div class="finance-settings__grid-wrap">
      <table class="finance-settings__grid">
        <thead>
          <tr>
            <th class="finance-settings__col-type">单据类型</th>
            <th v-for="s in statuses" :key="s.value">{{ s.label }}</th>
            <th class="finance-settings__col-op">整行</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dt in docTypes" :key="dt.value">
            <td class="finance-settings__col-type">
              <span class="finance-settings__type-name">{{ dt.label }}</span>
            </td>
            <td
              v-for="s in statuses"
              :key="s.value"
              class="finance-settings__cell"
            >
              <el-checkbox v-model="matrix[dt.value][s.value]" />
            </td>
            <td class="finance-settings__col-op">
              <el-button link type="primary" @click="toggleRow(dt.value)">
                {{ isRowAllChecked(dt.value) ? '清空' : '全选' }}
              </el-button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="finance-settings__actions">
      <el-button type="primary" :disabled="!configItem" @click="save">
        保存费用单发起设置
      </el-button>
      <span class="finance-settings__default">
        默认：各类费用单在所有节点均可发起、不强制拦截
      </span>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { SystemConfig } from '@/api/system/config/model';
  import { TASK_STATUS_OPTIONS } from '@/views/operation/task/status-config';

  defineOptions({ name: 'FinanceSettings' });

  const CONFIG_KEY = 'finance.task_doc_stage_rules';

  const props = defineProps<{
    items: SystemConfig[];
  }>();

  const emit = defineEmits<{
    (e: 'config-change', item: SystemConfig, val: string): void;
  }>();

  const docTypes = [
    { value: 1, label: '预付单' },
    { value: 2, label: '补款单' },
    { value: 3, label: '结算单' },
    { value: 4, label: '承包单' }
  ];

  const statuses = TASK_STATUS_OPTIONS.map((s) => ({
    value: s.value as number,
    label: s.label
  }));

  const configItem = computed(() =>
    props.items.find((i) => i.configKey === CONFIG_KEY)
  );

  const enforce = ref(false);

  /** matrix[docType][status] = 是否允许 */
  const matrix = reactive<Record<number, Record<number, boolean>>>({});

  const resetMatrix = (allowedByType: Record<number, Set<number>> | null) => {
    for (const dt of docTypes) {
      const row: Record<number, boolean> = {};
      for (const s of statuses) {
        // 无配置时默认全放开
        row[s.value] = allowedByType
          ? !!allowedByType[dt.value]?.has(s.value)
          : true;
      }
      matrix[dt.value] = row;
    }
  };

  const parseConfig = (raw: string | undefined | null) => {
    if (!raw) {
      enforce.value = false;
      resetMatrix(null);
      return;
    }
    try {
      const obj = JSON.parse(raw) as {
        enforce?: boolean;
        rules?: Record<string, number[]>;
      };
      enforce.value = !!obj.enforce;
      const allowed: Record<number, Set<number>> = {};
      for (const dt of docTypes) {
        const list = obj.rules?.[String(dt.value)] ?? [];
        allowed[dt.value] = new Set(
          Array.isArray(list) ? list.map((n) => Number(n)) : []
        );
      }
      resetMatrix(allowed);
    } catch {
      enforce.value = false;
      resetMatrix(null);
    }
  };

  watch(
    () => [configItem.value?.configValue, configItem.value?.id] as const,
    () => parseConfig(configItem.value?.configValue),
    { immediate: true }
  );

  const isRowAllChecked = (dt: number) =>
    statuses.every((s) => matrix[dt]?.[s.value]);

  const toggleRow = (dt: number) => {
    const next = !isRowAllChecked(dt);
    for (const s of statuses) {
      matrix[dt][s.value] = next;
    }
  };

  const save = () => {
    const item = configItem.value;
    if (!item) return;
    const rules: Record<string, number[]> = {};
    for (const dt of docTypes) {
      rules[String(dt.value)] = statuses
        .filter((s) => matrix[dt.value]?.[s.value])
        .map((s) => s.value);
    }
    const json = JSON.stringify({ enforce: enforce.value, rules });
    if (json.length > 500) {
      EleMessage.error({ message: '配置项过长，请减少勾选项', plain: true });
      return;
    }
    emit('config-change', item, json);
  };
</script>

<style scoped>
  .finance-settings {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .finance-settings__intro {
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
  }

  .finance-settings__enforce {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 14px;
    border-radius: var(--el-border-radius-base);
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-7);
  }

  .finance-settings__enforce-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .finance-settings__enforce-desc {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
  }

  .finance-settings__grid-wrap {
    overflow-x: auto;
  }

  .finance-settings__grid {
    border-collapse: collapse;
    width: 100%;
    min-width: 720px;
  }

  .finance-settings__grid th,
  .finance-settings__grid td {
    border: 1px solid var(--el-border-color-lighter);
    padding: 8px 10px;
    text-align: center;
    font-size: 13px;
    white-space: nowrap;
  }

  .finance-settings__grid thead th {
    background: var(--el-fill-color-light);
    font-weight: 600;
    color: var(--el-text-color-regular);
  }

  .finance-settings__col-type {
    text-align: left;
    position: sticky;
    left: 0;
    background: var(--el-bg-color);
    z-index: 1;
  }

  .finance-settings__grid thead .finance-settings__col-type {
    background: var(--el-fill-color-light);
  }

  .finance-settings__type-name {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .finance-settings__actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px 16px;
  }

  .finance-settings__default {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }
</style>
