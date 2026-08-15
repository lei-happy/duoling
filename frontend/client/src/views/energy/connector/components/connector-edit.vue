<template>
  <el-dialog
    title="新增数据接入"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <p class="form-tip">先选供应商和接入方式。Excel 接入保存后，可在列表里直接导入账单。</p>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-form-item prop="connectorName">
        <floating-label
          label="请输入接入名称"
          type="input"
          v-model.trim="form.connectorName"
          clearable
        />
      </el-form-item>
      <el-form-item prop="connectorCode">
        <floating-label
          v-model="form.connectorCode"
          label="请选择接入类型"
          type="select"
          :clearable="false"
        >
          <el-option
            v-for="o in CONNECTOR_CODES"
            :key="o.value"
            :label="o.label"
            :value="o.value"
          />
        </floating-label>
      </el-form-item>
      <el-form-item prop="supplierId">
        <floating-label
          v-model="form.supplierId"
          label="请选择供应商"
          type="select"
          filterable
          :clearable="false"
        >
          <el-option
            v-for="s in suppliers"
            :key="s.id"
            :label="s.supplierName"
            :value="s.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.accountId"
          label="请选择默认账户"
          type="select"
          filterable
          clearable
        >
          <el-option
            v-for="a in accounts"
            :key="a.id"
            :label="a.accountName"
            :value="a.id"
          />
        </floating-label>
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.syncMode"
          label="请选择同步方式"
          type="select"
          :clearable="false"
        >
          <el-option
            v-for="o in SYNC_MODES"
            :key="o.value"
            :label="o.label"
            :value="o.value"
          />
        </floating-label>
      </el-form-item>
      <el-form-item v-if="form.syncMode === 'cron'">
        <floating-label
          label="请输入 Cron，如 0 2 * * *"
          type="input"
          v-model.trim="form.cron"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入备注"
          type="input"
          input-type="textarea"
          v-model="form.remark"
          :clearable="false"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addConnector } from '@/api/energy';
  import { CONNECTOR_CODES, SYNC_MODES } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    suppliers: Array<Record<string, any>>;
    accounts: Array<Record<string, any>>;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({});

  const rules = reactive<FormRules>({
    connectorName: [
      { required: true, message: '请输入接入名称', trigger: 'blur' }
    ],
    connectorCode: [
      { required: true, message: '请选择接入类型', trigger: 'change' }
    ],
    supplierId: [
      { required: true, message: '请选择供应商', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, {
        connectorName: '',
        connectorCode: 'excel',
        supplierId: undefined,
        accountId: undefined,
        syncMode: 'manual',
        cron: '',
        remark: ''
      });
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        await addConnector(form);
        EleMessage.success({ message: '已新增接入配置', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        if (e?.message) EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .form-tip {
    margin: 0 0 16px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.7;
  }

  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
