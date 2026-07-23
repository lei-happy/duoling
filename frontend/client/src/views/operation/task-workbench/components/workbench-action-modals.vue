<!--
  调度工作台 — 语义化动作弹窗宿主

  将各状态对应的 action-*.vue 集中在一处，父页面只维护「当前打开的 dialog key」与选中任务，
  避免 index 里堆叠多份 v-model 与重复绑定。
-->
<template>
  <action-assign-carrier
    :visible="actionDialog === 'assign-carrier'"
    :tasks="targets"
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
  <action-revert
    v-if="revertActionKey"
    :visible="actionDialog === 'revert'"
    :tasks="targets"
    :action-key="revertActionKey"
    @update:visible="(v) => onDialogVisible('revert', v)"
    @done="emit('done')"
  />
  <action-revert-sign
    :visible="actionDialog === 'revert-sign'"
    :tasks="targets"
    @update:visible="(v) => onDialogVisible('revert-sign', v)"
    @done="emit('done')"
  />
  <action-force-cancel
    :visible="actionDialog === 'force-cancel'"
    :tasks="targets"
    @update:visible="(v) => onDialogVisible('force-cancel', v)"
    @done="emit('done')"
  />
  <action-cancel-task
    :visible="actionDialog === 'cancel-task'"
    :tasks="targets"
    @update:visible="(v) => onDialogVisible('cancel-task', v)"
    @done="emit('done')"
  />

  <task-edit
    v-model:visible="editVisible"
    :data="singleTask"
    @done="emit('done')"
  />

  <finance-edit
    v-if="singleTask"
    v-model:visible="financeVisible"
    :task="singleTask"
    :doc-id="null"
    :init-doc-type="financeInitDocType"
    :init-is-final="financeInitIsFinal"
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
  import ActionRevert from './action-revert.vue';
  import ActionRevertSign from './action-revert-sign.vue';
  import ActionForceCancel from './action-force-cancel.vue';
  import ActionCancelTask from './action-cancel-task.vue';
  import TaskEdit from '../../task/components/task-edit.vue';
  import FinanceEdit from '../../task-finance/components/finance-edit.vue';
  import type { Task } from '@/api/operation/task/model';
  import type {
    TaskActionConfig,
    TaskActionKey
  } from '../../task/task-actions';

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
  // 费用单创建预填类型：生成结算单=3/1；新建预付单=1/0；不传则由弹框按节点过滤
  const financeInitDocType = defineModel<number | undefined>(
    'financeInitDocType',
    { default: undefined }
  );
  const financeInitIsFinal = defineModel<number | undefined>(
    'financeInitIsFinal',
    { default: undefined }
  );
  // 任务单编辑抽屉（沿用 task/components/task-edit.vue），编辑 status -1/0/1 任务
  const editVisible = defineModel<boolean>('editVisible', { default: false });
  // 当 actionDialog='revert' 时，调用方需同步设置具体的 revert 动作 key
  // 用于通用撤销弹窗 (action-revert.vue) 决定 from→to 文案与 revertTo 参数
  const revertActionKey = defineModel<TaskActionKey | null>('revertActionKey', {
    default: null
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
