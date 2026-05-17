<!--
  调度工作台 — 语义化动作弹窗宿主

  将各状态对应的 action-*.vue 集中在一处，父页面只维护「当前打开的 dialog key」与选中任务，
  避免 index 里堆叠多份 v-model 与重复绑定。
-->
<template>
  <action-assign-carrier
    :visible="actionDialog === 'assign-carrier'"
    :task="singleTask"
    @update:visible="(v) => onDialogVisible('assign-carrier', v)"
    @done="emit('done')"
  />
  <action-dispatch
    :visible="actionDialog === 'dispatch'"
    :task="singleTask"
    @update:visible="(v) => onDialogVisible('dispatch', v)"
    @done="emit('dispatch-done')"
  />
  <action-plan-route
    :visible="actionDialog === 'plan-route'"
    :task="singleTask"
    @update:visible="(v) => onDialogVisible('plan-route', v)"
    @done="emit('done')"
  />
  <action-confirm-load
    :visible="actionDialog === 'confirm-load'"
    :tasks="targets"
    @update:visible="(v) => onDialogVisible('confirm-load', v)"
    @done="emit('done')"
  />
  <action-confirm-arrive
    :visible="actionDialog === 'confirm-arrive'"
    :tasks="targets"
    @update:visible="(v) => onDialogVisible('confirm-arrive', v)"
    @done="emit('done')"
  />
  <action-confirm-sign
    :visible="actionDialog === 'confirm-sign'"
    :tasks="targets"
    @update:visible="(v) => onDialogVisible('confirm-sign', v)"
    @done="emit('done')"
  />

  <finance-edit
    v-if="singleTask"
    v-model:visible="financeVisible"
    :task="singleTask"
    :doc-id="null"
    :init-doc-type="3"
    :init-is-final="1"
    @done="emit('done')"
  />
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import ActionAssignCarrier from './action-assign-carrier.vue';
  import ActionDispatch from './action-dispatch.vue';
  import ActionPlanRoute from './action-plan-route.vue';
  import ActionConfirmLoad from './action-confirm-load.vue';
  import ActionConfirmArrive from './action-confirm-arrive.vue';
  import ActionConfirmSign from './action-confirm-sign.vue';
  import FinanceEdit from '../../task-finance/components/finance-edit.vue';
  import type { Task } from '@/api/operation/task/model';
  import type { TaskActionConfig } from '../../task/task-actions';

  type DialogKey = NonNullable<TaskActionConfig['dialog']>;

  const props = defineProps<{
    targets: Task[];
  }>();

  const actionDialog = defineModel<DialogKey | null>('actionDialog', {
    default: null
  });
  const financeVisible = defineModel<boolean>('financeVisible', {
    default: false
  });

  const emit = defineEmits<{
    (e: 'done'): void;
    (e: 'dispatch-done'): void;
  }>();

  const singleTask = computed<Task | null>(() =>
    props.targets.length > 0 ? props.targets[0]! : null
  );

  const onDialogVisible = (key: DialogKey, v: boolean) => {
    if (!v && actionDialog.value === key) {
      actionDialog.value = null;
    }
  };
</script>
