<!-- 发起人范围配置抽屉 -->
<template>
  <el-drawer
    :model-value="visible"
    :size="460"
    title="发起人设置"
    :append-to-body="true"
    @update:model-value="updateVisible"
  >
    <el-form v-if="node" label-position="top">
      <el-form-item label="谁可以发起">
        <el-radio-group v-model="initiatorType">
          <el-radio value="all">所有人</el-radio>
          <el-radio value="user">指定成员</el-radio>
          <el-radio value="role">指定角色</el-radio>
          <el-radio value="dept">指定部门</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item v-if="initiatorType === 'user'" label="选择成员">
        <user-select v-model="userIds" multiple placeholder="选择可发起的成员" />
      </el-form-item>
      <el-form-item v-else-if="initiatorType === 'role'" label="选择角色">
        <role-select v-model="roleIds" multiple placeholder="选择可发起的角色" />
      </el-form-item>
      <el-form-item v-else-if="initiatorType === 'dept'" label="选择部门">
        <department-select
          v-model="deptIds"
          multiple
          placeholder="选择可发起的部门"
        />
        <el-checkbox v-model="includeChild" style="margin-top: 6px">
          包含子部门成员
        </el-checkbox>
      </el-form-item>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="仅配置范围内的用户可提交该审批；选择「所有人」则不限制。"
      />
    </el-form>

    <template #footer>
      <el-button type="primary" :loading="confirming" @click="onConfirm">
        完成
      </el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import UserSelect from '@/components/UserSelect/index.vue';
  import RoleSelect from '@/components/RoleSelect/index.vue';
  import DepartmentSelect from '@/components/DepartmentSelect/index.vue';
  import type { CanvasNode, InitiatorType } from '@/api/approval/model';
  import { syncMemberLabels } from '@/api/approval/transform';

  defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'confirm'): void;
  }>();

  const node = defineModel<CanvasNode | null>('node');
  const confirming = ref(false);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const onConfirm = async () => {
    if (!node.value || confirming.value) return;
    confirming.value = true;
    try {
      if (node.value.initiatorType === 'user') {
        const cfg = ensureCfg();
        await syncMemberLabels(cfg, cfg.user_ids ?? []);
      } else if (node.value.initiatorConfig?.user_labels) {
        delete node.value.initiatorConfig.user_labels;
      }
      emit('confirm');
      updateVisible(false);
    } finally {
      confirming.value = false;
    }
  };
  const ensureCfg = (): Record<string, any> => {
    if (!node.value) return {};
    if (!node.value.initiatorConfig) node.value.initiatorConfig = {};
    return node.value.initiatorConfig;
  };

  const initiatorType = computed<InitiatorType>({
    get: () => node.value?.initiatorType ?? 'all',
    set: (v) => {
      if (!node.value) return;
      node.value.initiatorType = v;
      node.value.initiatorConfig = {};
    }
  });

  const makeArrayProxy = (key: string) =>
    computed<number[]>({
      get: () => (node.value?.initiatorConfig?.[key] as number[]) ?? [],
      set: (v) => {
        ensureCfg()[key] = v;
      }
    });

  const userIds = makeArrayProxy('user_ids');
  const roleIds = makeArrayProxy('role_ids');
  const deptIds = makeArrayProxy('dept_ids');

  const includeChild = computed<boolean>({
    get: () => node.value?.initiatorConfig?.include_child ?? true,
    set: (v) => {
      ensureCfg().include_child = v;
    }
  });
</script>
