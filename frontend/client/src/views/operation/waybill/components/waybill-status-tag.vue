<!--
  运单状态标签

  与后端 ``WAYBILL_STATUS_LABELS`` 对齐（见
  backend/app/modules/client/services/state_machine/waybill_state_machine.py）：

  | 数值 | 名称   | 颜色   |
  | 0    | 待确认 | info   |
  | 1    | 待调度 | primary|
  | 2    | 调度中 | warning|
  | 3    | 运输中 | warning|
  | 4    | 待签收 | success|
  | 5    | 已签收 | success|
  | 6    | 已关闭 | danger |

  说明：2026-05 文案调整为"客户视角的票据流转"，强调签收是运单维度的核心动作；
  数据库 status 数值不变，无需历史数据兼容字段。
-->
<template>
  <el-tag :type="tagType as any" size="small">{{ label }}</el-tag>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';

  const props = defineProps<{
    status: number | null | undefined;
  }>();

  const STATUS_LABEL: Record<number, { label: string; type: string }> = {
    0: { label: '待确认', type: 'info' },
    1: { label: '待调度', type: 'primary' },
    2: { label: '调度中', type: 'warning' },
    3: { label: '运输中', type: 'warning' },
    4: { label: '待签收', type: 'success' },
    5: { label: '已签收', type: 'success' },
    6: { label: '已关闭', type: 'danger' }
  };

  const label = computed(() => STATUS_LABEL[props.status ?? 0]?.label || '--');
  const tagType = computed(
    () => STATUS_LABEL[props.status ?? 0]?.type || 'info'
  );
</script>
