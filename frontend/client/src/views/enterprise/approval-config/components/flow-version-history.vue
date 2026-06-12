<template>
  <el-dialog
    :title="dialogTitle"
    :model-value="visible"
    width="860px"
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
          <div class="version-snapshot">
            <pre>{{ formatSnapshot(row.snapshot) }}</pre>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="version"
        label="版本"
        width="80"
        align="center"
      >
        <template #default="{ row }">v{{ row.version }}</template>
      </el-table-column>
      <el-table-column
        prop="changeType"
        label="变更类型"
        width="100"
        align="center"
      >
        <template #default="{ row }">
          <el-tag :type="changeTypeTag(row.changeType)" size="small">
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
      <el-table-column prop="remark" label="备注" min-width="160" />
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
  import { ref, watch, computed } from 'vue';
  import { listFlowVersionHistory } from '@/api/approval';
  import type { FlowVersionLog } from '@/api/approval/model';

  const props = defineProps<{
    visible: boolean;
    flowId: number | null;
    flowName?: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const loading = ref(false);
  const logs = ref<FlowVersionLog[]>([]);

  const dialogTitle = computed(() =>
    props.flowName
      ? `${props.flowName} - 版本历史`
      : '审批流程版本历史'
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const changeTypeText = (t?: string) => {
    if (t === 'publish') return '发布';
    if (t === 'disable') return '停用';
    if (t === 'enable') return '启用';
    return t || '—';
  };

  const changeTypeTag = (
    t?: string
  ): 'success' | 'danger' | 'warning' | 'info' => {
    if (t === 'publish') return 'success';
    if (t === 'disable') return 'danger';
    if (t === 'enable') return 'warning';
    return 'info';
  };

  const formatSnapshot = (val: unknown): string => {
    if (val == null) return '--';
    try {
      const obj = typeof val === 'string' ? JSON.parse(val) : val;
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(val);
    }
  };

  const loadLogs = async (id: number) => {
    loading.value = true;
    try {
      const data = await listFlowVersionHistory(id);
      logs.value = data ?? [];
    } catch {
      logs.value = [];
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val && props.flowId) {
        loadLogs(props.flowId);
      } else if (!val) {
        logs.value = [];
      }
    }
  );
</script>

<style scoped lang="scss">
  .version-snapshot {
    padding: 8px 16px;
  }

  .version-snapshot pre {
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
