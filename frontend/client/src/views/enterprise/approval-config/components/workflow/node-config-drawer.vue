<!-- 审批人 / 抄送人 节点配置抽屉 -->
<template>
  <el-drawer
    :model-value="visible"
    :size="460"
    :title="node?.type === 'cc' ? '抄送人设置' : '审批人设置'"
    :append-to-body="true"
    @update:model-value="updateVisible"
  >
    <el-form v-if="node" label-position="top">
      <el-form-item label="节点名称">
        <el-input v-model.trim="node.nodeName" placeholder="请输入节点名称" />
      </el-form-item>

      <el-form-item :label="node.type === 'cc' ? '抄送人来源' : '审批人来源'">
        <el-select
          v-model="approverType"
          style="width: 100%"
          @change="onTypeChange"
        >
          <el-option
            v-for="t in typeOptions"
            :key="t.value"
            :value="t.value"
            :label="t.label"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="approverType === 1" label="选择成员">
        <user-select v-model="userIds" multiple placeholder="选择成员" />
      </el-form-item>
      <el-form-item v-else-if="approverType === 2" label="选择角色">
        <role-select v-model="roleIds" multiple placeholder="选择角色" />
      </el-form-item>
      <el-form-item v-else-if="approverType === 3" label="选择部门">
        <department-select v-model="deptIds" multiple placeholder="选择部门" />
        <el-checkbox v-model="includeChild" style="margin-top: 6px">
          包含子部门成员
        </el-checkbox>
      </el-form-item>

      <template v-else-if="approverType === 4">
        <el-form-item label="负责人来源">
          <el-radio-group v-model="deptLeaderRef">
            <el-radio value="initiator">发起人所在部门</el-radio>
            <el-radio value="dept_id">指定部门</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="deptLeaderRef === 'dept_id'" label="选择部门">
          <department-select v-model="deptLeaderId" placeholder="请选择部门" />
        </el-form-item>
        <p class="wf-rule-tip">
          取对应部门在「组织架构」中配置的负责人；请确保部门已设置负责人。
        </p>
      </template>

      <template v-else-if="approverType === 5">
        <el-form-item label="上级层级">
          <el-select v-model="supervisorLevel" style="width: 100%">
            <el-option
              v-for="n in 5"
              :key="n"
              :value="n"
              :label="supervisorLevelLabel(n)"
            />
          </el-select>
        </el-form-item>
        <p class="wf-rule-tip">
          沿发起人「直属上级」链向上查找；请在「用户管理」中维护上级关系。
        </p>
      </template>

      <template v-if="node.type === 'approval'">
        <el-form-item label="签署方式">
          <el-radio-group v-model="node.signType">
            <el-radio v-for="s in SIGN_TYPES" :key="s.value" :value="s.value">
              {{ s.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批人为空时">
          <el-radio-group v-model="node.emptyStrategy">
            <el-radio
              v-for="e in EMPTY_STRATEGIES"
              :key="e.value"
              :value="e.value"
            >
              {{ e.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="高级">
          <div class="wf-switch-row">
            <span>允许转审</span>
            <el-switch
              v-model="node.allowTransfer"
              :active-value="1"
              :inactive-value="0"
            />
          </div>
          <div class="wf-switch-row">
            <span>允许加签</span>
            <el-switch
              v-model="node.allowAddsign"
              :active-value="1"
              :inactive-value="0"
            />
          </div>
        </el-form-item>
      </template>
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
  import type { CanvasNode } from '@/api/approval/model';
  import {
    APPROVER_TYPES,
    SIGN_TYPES,
    EMPTY_STRATEGIES,
    syncMemberLabels
  } from '@/api/approval/transform';

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
      if (node.value.approverType === 1) {
        const cfg = ensureCfg();
        await syncMemberLabels(cfg, cfg.user_ids ?? []);
      } else if (node.value.approverConfig?.user_labels) {
        delete node.value.approverConfig.user_labels;
      }
      emit('confirm');
      updateVisible(false);
    } finally {
      confirming.value = false;
    }
  };

  const typeOptions = computed(() =>
    node.value?.type === 'cc'
      ? APPROVER_TYPES.filter((t) => [1, 2, 3].includes(t.value))
      : APPROVER_TYPES
  );

  const ensureCfg = (): Record<string, any> => {
    if (!node.value) return {};
    if (!node.value.approverConfig) node.value.approverConfig = {};
    return node.value.approverConfig;
  };

  const approverType = computed<number>({
    get: () => node.value?.approverType ?? 1,
    set: (v) => {
      if (node.value) node.value.approverType = v;
    }
  });

  const supervisorLevelLabel = (n: number) =>
    n === 1 ? '直接上级（第1级）' : `第${n}级上级`;

  const onTypeChange = () => {
    if (!node.value) return;
    const t = node.value.approverType;
    if (t === 4) {
      node.value.approverConfig = { dept_ref: 'initiator' };
    } else if (t === 5) {
      node.value.approverConfig = { level: 1 };
    } else {
      node.value.approverConfig = {};
    }
  };

  const makeArrayProxy = (key: string) =>
    computed<number[]>({
      get: () => (node.value?.approverConfig?.[key] as number[]) ?? [],
      set: (v) => {
        ensureCfg()[key] = v;
      }
    });

  const userIds = makeArrayProxy('user_ids');
  const roleIds = makeArrayProxy('role_ids');
  const deptIds = makeArrayProxy('dept_ids');

  const includeChild = computed<boolean>({
    get: () => node.value?.approverConfig?.include_child ?? true,
    set: (v) => {
      ensureCfg().include_child = v;
    }
  });

  const deptLeaderRef = computed<'initiator' | 'dept_id'>({
    get: () => {
      const ref = node.value?.approverConfig?.dept_ref;
      return ref === 'dept_id' ? 'dept_id' : 'initiator';
    },
    set: (v) => {
      const cfg = ensureCfg();
      cfg.dept_ref = v;
      if (v === 'initiator') {
        delete cfg.dept_id;
      }
    }
  });

  const deptLeaderId = computed<number | undefined>({
    get: () => node.value?.approverConfig?.dept_id,
    set: (v) => {
      const cfg = ensureCfg();
      cfg.dept_ref = 'dept_id';
      cfg.dept_id = v;
    }
  });

  const supervisorLevel = computed<number>({
    get: () => Number(node.value?.approverConfig?.level ?? 1),
    set: (v) => {
      ensureCfg().level = v;
    }
  });
</script>

<style scoped>
  .wf-rule-tip {
    margin: -4px 0 12px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
  }
</style>
