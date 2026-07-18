<template>
  <el-dialog
    title="运价规则版本历史"
    :model-value="visible"
    width="900px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-table
      v-loading="loading"
      :data="logs"
      border
      stripe
      max-height="520"
      size="small"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="version-diff">
            <div class="diff-col">
              <div class="diff-cap">变更前</div>
              <pre>{{ formatJson(row.snapshotBefore) }}</pre>
            </div>
            <div class="diff-col">
              <div class="diff-cap">变更后</div>
              <pre>{{ formatJson(row.snapshotAfter) }}</pre>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="ruleVersionBefore"
        label="变更前版本"
        width="100"
        align="center"
      />
      <el-table-column
        prop="ruleVersionAfter"
        label="变更后版本"
        width="100"
        align="center"
      />
      <el-table-column
        prop="changeType"
        label="变更类型"
        width="100"
        align="center"
      >
        <template #default="{ row }">
          <el-tag
            :type="
              row.changeType === 'delete'
                ? 'danger'
                : row.changeType === 'create'
                  ? 'success'
                  : 'warning'
            "
            size="small"
          >
            {{ changeTypeText(row.changeType) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="operatorId"
        label="操作人ID"
        width="100"
        align="center"
      />
      <el-table-column
        prop="affectedWaybillCount"
        label="影响计划数"
        width="100"
        align="center"
      />
      <el-table-column prop="remark" label="备注" min-width="180" />
      <el-table-column
        prop="createdAt"
        label="变更时间"
        width="170"
        align="center"
      />
    </el-table>
    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { listRateVersionHistory } from '@/api/billing/contract';

  const props = defineProps<{
    visible: boolean;
    rateId: number | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const loading = ref(false);
  const logs = ref<any[]>([]);

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const changeTypeText = (t?: string) => {
    if (t === 'create') return '创建';
    if (t === 'delete') return '删除';
    if (t === 'status_change') return '状态';
    return '更新';
  };

  const formatJson = (val: unknown): string => {
    if (val == null) return '--';
    try {
      const obj = typeof val === 'string' ? JSON.parse(val) : val;
      return JSON.stringify(obj, null, 2);
    } catch (_) {
      return String(val);
    }
  };

  const loadLogs = async (id: number) => {
    loading.value = true;
    try {
      const data = await listRateVersionHistory(id);
      logs.value = (data as any[]) ?? [];
    } catch (_) {
      logs.value = [];
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val && props.rateId) {
        loadLogs(props.rateId);
      } else if (!val) {
        logs.value = [];
      }
    }
  );
</script>

<style scoped lang="scss">
  .version-diff {
    display: flex;
    gap: 16px;
    padding: 8px 16px;
  }
  .diff-col {
    flex: 1;
    min-width: 0;
  }
  .diff-cap {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
    font-weight: 500;
  }
  .diff-col pre {
    background: var(--el-fill-color-light);
    border-radius: 6px;
    padding: 8px;
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 320px;
    overflow: auto;
  }
</style>
