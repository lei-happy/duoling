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
            :disabled="t.disabled"
          >
            <span>{{ t.label }}</span>
            <span v-if="t.tip" class="wf-opt-tip">{{ t.tip }}</span>
          </el-option>
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
      <el-form-item v-else-if="approverType === 6" label="自选范围">
        <el-radio-group v-model="pickScope">
          <el-radio value="all">全员</el-radio>
          <el-radio value="dept">本部门</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-alert
        v-else-if="approverType === 4 || approverType === 5"
        type="warning"
        :closable="false"
        show-icon
        title="该能力依赖组织模型扩展，第 2 期生效"
        style="margin-bottom: 16px"
      />

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
      <el-button type="primary" @click="updateVisible(false)">完成</el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import UserSelect from '@/components/UserSelect/index.vue';
  import RoleSelect from '@/components/RoleSelect/index.vue';
  import DepartmentSelect from '@/components/DepartmentSelect/index.vue';
  import type { CanvasNode } from '@/api/approval/model';
  import {
    APPROVER_TYPES,
    SIGN_TYPES,
    EMPTY_STRATEGIES
  } from '@/api/approval/transform';

  defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  /** 直接编辑画布树中的节点对象（两端共享同一响应式引用） */
  const node = defineModel<CanvasNode | null>('node');

  const updateVisible = (v: boolean) => emit('update:visible', v);

  // 抄送节点只支持「指定成员/角色/部门」
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

  const onTypeChange = () => {
    if (node.value) node.value.approverConfig = {};
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

  const pickScope = computed<string>({
    get: () => node.value?.approverConfig?.scope ?? 'all',
    set: (v) => {
      ensureCfg().scope = v;
    }
  });
</script>
