<!-- 单条结算账户编辑（在 carrier-edit 内嵌使用） -->
<template>
  <el-dialog
    :title="isEdit ? '编辑结算账户' : '新增结算账户'"
    :model-value="visible"
    width="660px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="settlement-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item prop="accountLabel">
            <floating-label
              label="账户标签（如：对公主账户/私户-司机张三）"
              type="input"
              v-model.trim="form.accountLabel"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="accountType">
            <floating-label
              v-model="form.accountType"
              label="账户类型"
              type="select"
            >
              <el-option label="对公" :value="0" />
              <el-option label="对私" :value="1" />
              <el-option label="其他" :value="2" />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="settlementType">
            <floating-label
              v-model="form.settlementType"
              label="结算方式"
              type="select"
            >
              <el-option label="月结" :value="0" />
              <el-option label="票结" :value="1" />
              <el-option label="预付" :value="2" />
              <el-option label="趟结" :value="3" />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="结算周期天数（月结/趟结）"
              type="input"
              input-type="number"
              v-model.number="form.settlementPeriod"
              clearable
            />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="开户行"
              type="input"
              v-model.trim="form.bankName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="开户支行"
              type="input"
              v-model.trim="form.bankBranch"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="银行账号"
              type="input"
              v-model.trim="form.bankAccount"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="户名"
              type="input"
              v-model.trim="form.bankAccountName"
              clearable
            />
          </el-form-item>
        </el-col>

        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="适用范围（业务线/路线/车型，文本备注）"
              type="input"
              v-model.trim="form.applicableScope"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-checkbox
            :model-value="form.isDefault === 1"
            @update:model-value="(v: any) => (form.isDefault = v ? 1 : 0)"
          >
            设为默认结算账户
          </el-checkbox>
        </el-col>
        <el-col :span="12">
          <el-checkbox
            :model-value="form.status === 1"
            @update:model-value="(v: any) => (form.status = v ? 1 : 0)"
          >
            启用
          </el-checkbox>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="备注"
              type="input"
              input-type="textarea"
              v-model="form.remark"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
      </el-row>
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
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import type { CarrierSettlement } from '@/api/partner/carrier/model';

  const props = defineProps<{
    visible: boolean;
    data: CarrierSettlement | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'submit', payload: CarrierSettlement): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<CarrierSettlement>({
    accountLabel: '',
    accountType: 0,
    settlementType: 0,
    isDefault: 0,
    status: 1,
    sortOrder: 0
  });

  const rules = reactive<FormRules>({
    accountLabel: [
      { required: true, message: '请输入账户标签', trigger: 'blur' }
    ],
    accountType: [
      { required: true, message: '请选择账户类型', trigger: 'change' }
    ],
    settlementType: [
      { required: true, message: '请选择结算方式', trigger: 'change' }
    ]
  });

  function reset() {
    Object.assign(form, {
      id: undefined,
      carrierId: undefined,
      accountLabel: '',
      accountType: 0,
      settlementType: 0,
      settlementPeriod: undefined,
      settlementDay: undefined,
      bankName: undefined,
      bankBranch: undefined,
      bankAccount: undefined,
      bankAccountName: undefined,
      swiftCode: undefined,
      taxRate: undefined,
      applicableScope: undefined,
      isDefault: 0,
      status: 1,
      sortOrder: 0,
      remark: undefined
    });
  }

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      if (props.data?.id) {
        Object.assign(form, props.data);
      } else {
        reset();
        if (props.data) {
          // 仅传入默认值（如行内"新增"按钮预填）
          Object.assign(form, props.data);
        }
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    formRef.value?.validate((valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        emit('submit', { ...form });
        updateVisible(false);
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .settlement-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
</style>
