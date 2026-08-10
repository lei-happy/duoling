<!--
  计划状态标签

  与后端 ``WAYBILL_STATUS_LABELS`` 对齐（见
  backend/app/modules/client/services/state_machine/waybill_state_machine.py）：

  | 数值 | 名称   | 颜色   |
  | 0    | 待确认 | info   |
  | 1    | 待调度 | primary|
  | 2    | 调度中 | warning|
  | 3    | 运输中 | warning|
  | 4    | 待交车 | success|
  | 5    | 已交车 | success|
  | 6    | 已回单 | success|
  | 7    | 已关闭 | danger |

  说明：文案取"客户视角的票据流转"，4/5 与商品车运输行业口径统一为「交车」；
  6 已回单（交车回单返还货主）是计划域独有的人工动作，与任务状态机无关。
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
    4: { label: '待交车', type: 'success' },
    5: { label: '已交车', type: 'success' },
    6: { label: '已回单', type: 'success' },
    7: { label: '已关闭', type: 'danger' }
  };

  const label = computed(() => STATUS_LABEL[props.status ?? 0]?.label || '--');
  const tagType = computed(
    () => STATUS_LABEL[props.status ?? 0]?.type || 'info'
  );
</script>
