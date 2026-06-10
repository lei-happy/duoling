<template>
  <el-drawer
    :model-value="visible"
    :size="640"
    :title="form.id ? '编辑审批流程' : '新增审批流程'"
    :destroy-on-close="true"
    @update:model-value="updateVisible"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
      <el-form-item label="审批类型" prop="bizType">
        <el-select
          v-model="form.bizType"
          placeholder="请选择业务场景"
          style="width: 100%"
          :disabled="!!form.id"
        >
          <el-option
            v-for="t in bizTypeOptions"
            :key="t.value"
            :value="t.value"
            :label="t.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="流程名称" prop="flowName">
        <el-input
          v-model.trim="form.flowName"
          placeholder="如：社会运力准入审核"
        />
      </el-form-item>
      <el-form-item label="匹配优先级" prop="priority">
        <el-input-number v-model="form.priority" :min="1" :max="9999" />
        <span class="form-tip">数值越小越优先匹配</span>
      </el-form-item>
      <el-form-item label="兜底默认">
        <el-switch
          v-model="form.isDefault"
          :active-value="1"
          :inactive-value="0"
        />
        <span class="form-tip">条件都不命中时使用该默认模板</span>
      </el-form-item>
      <el-form-item label="允许撤回">
        <el-switch
          v-model="form.allowWithdraw"
          :active-value="1"
          :inactive-value="0"
        />
      </el-form-item>
      <el-form-item v-if="form.allowWithdraw" label="撤回范围">
        <el-radio-group v-model="form.withdrawScope">
          <el-radio :value="1">审批中任意时刻</el-radio>
          <el-radio :value="0">仅首节点审批前</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model.trim="form.remark" type="textarea" :rows="2" />
      </el-form-item>

      <el-divider content-position="left"
        >审批节点（自上而下顺序流转）</el-divider
      >

      <div v-for="(node, idx) in form.nodes" :key="idx" class="flow-node-card">
        <div class="flow-node-card-head">
          <span class="flow-node-card-title">节点 {{ idx + 1 }}</span>
          <div>
            <el-button link :disabled="idx === 0" @click="moveNode(idx, -1)">
              上移
            </el-button>
            <el-button
              link
              :disabled="idx === form.nodes.length - 1"
              @click="moveNode(idx, 1)"
            >
              下移
            </el-button>
            <el-button link type="danger" @click="removeNode(idx)">
              删除
            </el-button>
          </div>
        </div>

        <el-form-item label="节点名称">
          <el-input
            v-model.trim="node.nodeName"
            placeholder="如：运力准入审核"
          />
        </el-form-item>
        <el-form-item label="节点类型">
          <el-radio-group v-model="node.nodeType">
            <el-radio :value="1">审批</el-radio>
            <el-radio :value="2">抄送</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批人">
          <el-select
            v-model="node.approverType"
            style="width: 100%"
            @change="onApproverTypeChange(node)"
          >
            <el-option :value="1" label="指定成员" />
            <el-option :value="2" label="指定角色" />
            <el-option :value="3" label="指定部门" />
            <el-option :value="4" label="发起人部门负责人" />
            <el-option :value="5" label="逐级上级主管" />
            <el-option :value="6" label="发起人自选" />
            <el-option :value="7" label="发起人本人" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="node.approverType === 1" label="成员">
          <user-select
            v-model="node._userIds"
            multiple
            placeholder="选择成员"
          />
        </el-form-item>
        <el-form-item v-else-if="node.approverType === 2" label="角色">
          <role-select
            v-model="node._roleIds"
            multiple
            placeholder="选择角色"
          />
        </el-form-item>
        <el-form-item v-else-if="node.approverType === 3" label="部门">
          <department-select
            v-model="node._deptIds"
            multiple
            placeholder="选择部门"
          />
        </el-form-item>
        <el-form-item v-if="node.nodeType === 1" label="签署方式">
          <el-radio-group v-model="node.signType">
            <el-radio :value="1">或签</el-radio>
            <el-radio :value="2">会签</el-radio>
            <el-radio :value="3">依次会签</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="node.nodeType === 1" label="无审批人">
          <el-radio-group v-model="node.emptyStrategy">
            <el-radio :value="1">自动通过</el-radio>
            <el-radio :value="3">报错阻断</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>

      <el-button plain class="flow-add-node" @click="addNode">
        + 添加节点
      </el-button>
    </el-form>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="confirm">
        保存
      </el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import UserSelect from '@/components/UserSelect/index.vue';
  import RoleSelect from '@/components/RoleSelect/index.vue';
  import DepartmentSelect from '@/components/DepartmentSelect/index.vue';
  import { createFlow, updateFlow, getFlow } from '@/api/approval';
  import type { FlowNode } from '@/api/approval/model';

  interface EditNode extends FlowNode {
    _userIds: number[];
    _roleIds: number[];
    _deptIds: number[];
  }

  const props = defineProps<{
    visible: boolean;
    flowId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const bizTypeOptions = [
    { value: 'social_capacity_audit', label: '社会运力准入审核' }
  ];

  const formRef = ref<FormInstance | null>(null);
  const saving = ref(false);
  const form = reactive<{
    id?: number;
    bizType: string;
    flowName: string;
    priority: number;
    isDefault: number;
    allowWithdraw: number;
    withdrawScope: number;
    remark: string;
    nodes: EditNode[];
  }>({
    bizType: 'social_capacity_audit',
    flowName: '',
    priority: 100,
    isDefault: 1,
    allowWithdraw: 1,
    withdrawScope: 1,
    remark: '',
    nodes: []
  });

  const rules: FormRules = {
    bizType: [{ required: true, message: '请选择审批类型', trigger: 'change' }],
    flowName: [{ required: true, message: '请输入流程名称', trigger: 'blur' }]
  };

  const newNode = (): EditNode => ({
    nodeOrder: form.nodes.length + 1,
    nodeType: 1,
    nodeName: '审批',
    approverType: 2,
    approverConfig: null,
    signType: 1,
    condition: null,
    emptyStrategy: 3,
    allowTransfer: 1,
    allowAddsign: 1,
    _userIds: [],
    _roleIds: [],
    _deptIds: []
  });

  const addNode = () => form.nodes.push(newNode());
  const removeNode = (idx: number) => form.nodes.splice(idx, 1);
  const moveNode = (idx: number, dir: -1 | 1) => {
    const target = idx + dir;
    if (target < 0 || target >= form.nodes.length) return;
    const [n] = form.nodes.splice(idx, 1);
    form.nodes.splice(target, 0, n);
  };
  const onApproverTypeChange = (node: EditNode) => {
    node._userIds = [];
    node._roleIds = [];
    node._deptIds = [];
  };

  const resetForm = () => {
    form.id = undefined;
    form.bizType = 'social_capacity_audit';
    form.flowName = '';
    form.priority = 100;
    form.isDefault = 1;
    form.allowWithdraw = 1;
    form.withdrawScope = 1;
    form.remark = '';
    form.nodes = [newNode()];
  };

  const loadDetail = async (flowId: number) => {
    const data = await getFlow(flowId);
    form.id = data.id;
    form.bizType = data.bizType;
    form.flowName = data.flowName;
    form.priority = data.priority ?? 100;
    form.isDefault = data.isDefault ?? 0;
    form.allowWithdraw = data.allowWithdraw ?? 1;
    form.withdrawScope = data.withdrawScope ?? 1;
    form.remark = data.remark ?? '';
    form.nodes = (data.nodes ?? []).map((n) => {
      const cfg = n.approverConfig || {};
      return {
        ...n,
        _userIds: (cfg.user_ids as number[]) ?? [],
        _roleIds: (cfg.role_ids as number[]) ?? [],
        _deptIds: (cfg.dept_ids as number[]) ?? []
      } as EditNode;
    });
  };

  watch(
    () => [props.visible, props.flowId] as const,
    async ([v, id]) => {
      if (!v) return;
      if (id) {
        try {
          await loadDetail(id);
        } catch (e: any) {
          EleMessage.error({ message: e?.message ?? '加载失败', plain: true });
        }
      } else {
        resetForm();
      }
    }
  );

  const buildApproverConfig = (node: EditNode): Record<string, any> | null => {
    if (node.approverType === 1) return { user_ids: node._userIds };
    if (node.approverType === 2) return { role_ids: node._roleIds };
    if (node.approverType === 3)
      return { dept_ids: node._deptIds, include_child: true };
    return null;
  };

  const confirm = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (!form.nodes.length) {
      EleMessage.error({ message: '至少添加一个节点', plain: true });
      return;
    }
    const nodes: FlowNode[] = form.nodes.map((n, idx) => ({
      nodeOrder: idx + 1,
      nodeType: n.nodeType,
      nodeName: n.nodeName || `节点${idx + 1}`,
      approverType: n.approverType,
      approverConfig: buildApproverConfig(n),
      signType: n.signType,
      condition: n.condition ?? null,
      emptyStrategy: n.emptyStrategy,
      allowTransfer: n.allowTransfer,
      allowAddsign: n.allowAddsign
    }));
    const body = {
      bizType: form.bizType,
      flowName: form.flowName,
      priority: form.priority,
      isDefault: form.isDefault,
      allowWithdraw: form.allowWithdraw,
      withdrawScope: form.withdrawScope,
      remark: form.remark || undefined,
      nodes
    };
    saving.value = true;
    try {
      if (form.id) {
        await updateFlow(form.id, body);
      } else {
        await createFlow(body);
      }
      EleMessage.success({ message: '保存成功', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '保存失败', plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .form-tip {
    margin-left: 8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
  .flow-node-card {
    border: 1px solid var(--el-border-color);
    border-radius: 6px;
    padding: 12px 12px 0;
    margin-bottom: 12px;
  }
  .flow-node-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .flow-node-card-title {
    font-weight: 600;
  }
  .flow-add-node {
    width: 100%;
    border-style: dashed;
  }
</style>
