<template>
  <el-dialog
    :title="form.id ? '编辑流程信息' : '新增审批流程'"
    :model-value="visible"
    width="720px"
    draggable
    class="flow-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="flow-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-tabs v-model="activeTab" class="flow-edit-tabs">
        <el-tab-pane label="基础信息" name="basic">
          <div class="flow-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item prop="bizType">
                  <floating-label
                    v-model="form.bizType"
                    label="请选择审批场景"
                    type="select"
                    :disabled="!!form.id"
                  >
                    <el-option
                      v-for="t in bizTypeOptions"
                      :key="t.value"
                      :value="t.value"
                      :label="t.label"
                    />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="flowName">
                  <floating-label
                    label="请输入流程名称"
                    type="input"
                    v-model.trim="form.flowName"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item>
                  <floating-label
                    label="请输入备注"
                    type="input"
                    input-type="textarea"
                    v-model.trim="form.remark"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-alert
              v-if="!form.id"
              type="info"
              :closable="false"
              show-icon
              title="保存后请在列表「审批流程配置」中绘制审批流程画布（节点、审批人、条件分支）"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="匹配规则" name="match">
          <div class="flow-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item prop="priority">
                  <floating-label
                    label="请输入匹配优先级"
                    type="input"
                    input-type="number"
                    v-model="priorityStr"
                    clearable
                  />
                </el-form-item>
                <p class="form-tip">数值越小越优先匹配，范围 1–9999</p>
              </el-col>
              <el-col :span="24">
                <div class="flow-switch-row">
                  <span class="flow-switch-label">兜底默认</span>
                  <el-switch
                    v-model="form.isDefault"
                    :active-value="1"
                    :inactive-value="0"
                  />
                  <span class="form-tip">条件都不命中时使用该默认模板</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="审批设置" name="approval">
          <div class="flow-tab-pane">
            <div class="flow-switch-row">
              <span class="flow-switch-label">允许撤回</span>
              <el-switch
                v-model="form.allowWithdraw"
                :active-value="1"
                :inactive-value="0"
              />
            </div>
            <div v-if="form.allowWithdraw" class="flow-withdraw-scope">
              <span class="flow-switch-label">撤回范围</span>
              <el-radio-group v-model="form.withdrawScope">
                <el-radio :value="1">审批中任意时刻</el-radio>
                <el-radio :value="0">仅首节点审批前</el-radio>
              </el-radio-group>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="confirm">
        {{ form.id ? '保存' : '保存并配置流程' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
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

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const activeTab = ref('basic');
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
    isDefault: 0,
    allowWithdraw: 1,
    withdrawScope: 1,
    remark: ''
  });

  const priorityStr = computed({
    get: () => String(form.priority ?? 100),
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.priority = 100;
        return;
      }
      const n = Number(t);
      if (Number.isFinite(n)) {
        form.priority = Math.min(9999, Math.max(1, Math.round(n)));
      }
    }
  });

  const rules: FormRules = {
    bizType: [{ required: true, message: '请选择审批场景', trigger: 'change' }],
    flowName: [{ required: true, message: '请输入流程名称', trigger: 'blur' }],
    priority: [
      {
        validator: (_rule, value, callback) => {
          if (value == null || value < 1 || value > 9999) {
            callback(new Error('优先级需在 1–9999 之间'));
            return;
          }
          callback();
        },
        trigger: 'blur'
      }
    ]
  };

  const resetForm = () => {
    form.id = undefined;
    form.bizType = 'social_capacity_audit';
    form.flowName = '';
    form.priority = 100;
    form.isDefault = 0;
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
      if (!v) {
        void nextTick(() => formRef.value?.clearValidate());
        return;
      }
      activeTab.value = 'basic';
      if (id) {
        try {
          await loadDetail(id);
        } catch (e: any) {
          EleMessage.error({ message: e?.message ?? '加载失败', plain: true });
        }
      } else {
        resetForm();
      }
      void nextTick(() => formRef.value?.clearValidate());
    }
  );

  const confirm = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      activeTab.value = 'basic';
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

<style scoped>
  .flow-edit-form {
    margin: 0;
  }

  .flow-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .flow-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .flow-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .flow-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .flow-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .flow-edit-tabs :deep(.el-tabs__item) {
    flex: 1;
    min-width: 0;
    margin: 0;
    padding: 0 6px;
    height: 36px;
    line-height: 36px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    transition:
      color 0.2s,
      background 0.2s,
      box-shadow 0.2s;
  }

  .flow-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .flow-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .flow-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .flow-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .flow-tab-pane {
    max-height: min(360px, calc(100vh - 300px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .flow-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .flow-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .flow-edit-dialog :deep(.flow-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }

  .form-tip {
    margin: 0 0 12px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.5;
  }

  .flow-switch-row,
  .flow-withdraw-scope {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 12px;
    margin-bottom: 16px;
  }

  .flow-switch-label {
    font-size: 13px;
    color: var(--el-text-color-regular);
    min-width: 72px;
  }

  .flow-withdraw-scope :deep(.el-radio) {
    margin-right: 16px;
  }
</style>
