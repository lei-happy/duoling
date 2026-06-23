<!--
  任务侧「关联运单状态分布」只读展示

  与任务状态机彼此独立：任务仅展示其下运单的状态分布（例如 3 张运单中
  2 张已签收、1 张已回单），不改变任务状态，也不出现"回单"等运单专属动作。
  数据来源：TaskOut / TaskListItemOut 的 waybillStatusSummary 字段。
-->
<template>
  <div v-if="hasData" class="wb-summary" :class="{ 'is-inline': inline }">
    <el-tag
      v-for="it in summary!.items"
      :key="it.status"
      :type="(STATUS_META[it.status]?.type as any) || 'info'"
      size="small"
      effect="plain"
    >
      {{ STATUS_META[it.status]?.label || `状态${it.status}` }}×{{ it.count }}
    </el-tag>
  </div>
  <span v-else class="ele-text-secondary">--</span>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { WaybillStatusSummary } from '@/api/operation/task/model';

  const props = defineProps<{
    summary?: WaybillStatusSummary | null;
    /** 行内紧凑模式（列表用） */
    inline?: boolean;
  }>();

  /** 与运单状态机 WAYBILL_STATUS_LABELS 对齐 */
  const STATUS_META: Record<number, { label: string; type: string }> = {
    0: { label: '待确认', type: 'info' },
    1: { label: '待调度', type: 'primary' },
    2: { label: '调度中', type: 'warning' },
    3: { label: '运输中', type: 'warning' },
    4: { label: '待签收', type: 'success' },
    5: { label: '已签收', type: 'success' },
    6: { label: '已回单', type: 'success' },
    7: { label: '已关闭', type: 'danger' }
  };

  const hasData = computed(
    () => !!props.summary && (props.summary.items?.length ?? 0) > 0
  );
</script>

<style lang="scss" scoped>
  .wb-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;

    &.is-inline {
      justify-content: center;
    }
  }
</style>
