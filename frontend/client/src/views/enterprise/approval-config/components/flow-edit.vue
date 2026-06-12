<template>
  <el-drawer
    :model-value="visible"
    :size="520"
    :title="form.id ? '编辑流程信息' : '新增审批流程'"
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

      <el-alert
        v-if="!form.id"
        type="info"
        :closable="false"
        show-icon
        title="保存后请在列表「审批流程配置」中绘制审批流程画布（节点、审批人、条件分支）"
      />
    </el-form>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="confirm">
        {{ form.id ? '保存' : '保存并配置流程' }}
      </el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { createFlow, updateFlow, getFlow } from '@/api/approval';

  const props = defineProps<{
    visible: boolean;
    flowId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', createdId?: number): void;
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
  }>({
    bizType: 'social_capacity_audit',
    flowName: '',
    priority: 100,
    isDefault: 1,
    allowWithdraw: 1,
    withdrawScope: 1,
    remark: ''
  });

  const rules: FormRules = {
    bizType: [{ required: true, message: '请选择审批类型', trigger: 'change' }],
    flowName: [{ required: true, message: '请输入流程名称', trigger: 'blur' }]
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

  const confirm = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    const body = {
      bizType: form.bizType,
      flowName: form.flowName,
      priority: form.priority,
      isDefault: form.isDefault,
      allowWithdraw: form.allowWithdraw,
      withdrawScope: form.withdrawScope,
      remark: form.remark || undefined
    };
    saving.value = true;
    try {
      if (form.id) {
        await updateFlow(form.id, body);
        EleMessage.success({ message: '保存成功', plain: true });
        updateVisible(false);
        emit('done');
      } else {
        const created = await createFlow(body);
        EleMessage.success({ message: '创建成功', plain: true });
        updateVisible(false);
        emit('done', created?.id);
      }
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
</style>
