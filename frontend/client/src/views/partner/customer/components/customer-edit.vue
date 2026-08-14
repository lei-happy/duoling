<template>
  <el-dialog
    :title="isEdit ? '编辑客户' : '新增客户'"
    :model-value="visible"
    width="720px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="customer-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <!-- 必填字段靠前 -->
        <el-col :span="12">
          <el-form-item prop="customerName">
            <floating-label
              label="请输入客户名称"
              type="input"
              v-model.trim="form.customerName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="customerType">
            <floating-label
              v-model="form.customerType"
              label="请选择客户类型"
              type="select"
              clearable
            >
              <el-option label="主机厂" :value="0" />
              <el-option label="贸易商" :value="1" />
              <el-option label="经销商" :value="2" />
              <el-option label="个人" :value="3" />
              <el-option label="其他" :value="4" />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="contactPerson">
            <floating-label
              label="请输入联系人"
              type="input"
              v-model.trim="form.contactPerson"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="contactPhone">
            <floating-label
              label="请输入联系电话"
              type="input"
              v-model.trim="form.contactPhone"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="status">
            <floating-label
              v-model="form.status"
              label="请选择客户状态"
              type="select"
              :clearable="false"
            >
              <el-option label="正常" :value="1" />
              <el-option label="停用" :value="0" />
            </floating-label>
          </el-form-item>
        </el-col>
        <!-- 选填 -->
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入客户编码，留空则自动生成"
              type="input"
              v-model.trim="form.customerCode"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入简称"
              type="input"
              v-model.trim="form.shortName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入统一社会信用代码"
              type="input"
              v-model.trim="form.creditCode"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入地址"
              type="input"
              v-model.trim="form.address"
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
              v-model="form.remark"
              :clearable="false"
            />
          </el-form-item>
        </el-col>

        <!-- 结算与信用：四个字段互相配合决定到期日与额度预警，放一起才不容易填错 -->
        <el-col :span="24">
          <el-divider content-position="left">结算与信用</el-divider>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="settlementType">
            <floating-label
              v-model="form.settlementType"
              label="请选择结算方式"
              type="select"
              clearable
            >
              <el-option label="月结" :value="0" />
              <el-option label="票结" :value="1" />
              <el-option label="预付" :value="2" />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="paymentDays">
            <floating-label
              v-model="form.paymentDays"
              label="账期天数，留空按 0 天算"
              type="input-number"
              :input-number-min="0"
              :input-number-max="365"
              :input-number-precision="0"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="creditLimit">
            <floating-label
              v-model="form.creditLimit"
              label="信用额度（元），留空不限额"
              type="input-number"
              :input-number-min="0"
              :input-number-step="1000"
              :input-number-precision="2"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="creditStatus">
            <floating-label
              v-model="form.creditStatus"
              label="请选择信用状态"
              type="select"
              :clearable="false"
            >
              <el-option label="正常" :value="1" />
              <el-option label="重点关注" :value="2" />
              <el-option label="暂停合作" :value="0" />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <div class="credit-tip">
            账期与结算方式一起决定应收到期日：月结按周期末顺延、票结按开票日顺延。
            超额度与逾期只在页面上提示，不会阻断录单派车。
          </div>
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
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addCustomer, updateCustomer } from '@/api/partner/customer';
  import type { Customer } from '@/api/partner/customer/model';

  const props = defineProps<{
    visible: boolean;
    data: Customer | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Customer>({});

  const rules = reactive<FormRules>({
    customerName: [
      { required: true, message: '请输入客户名称', trigger: 'blur' }
    ],
    customerType: [
      { required: true, message: '请选择客户类型', trigger: 'change' }
    ],
    settlementType: [
      { required: true, message: '请选择结算方式', trigger: 'change' }
    ],
    contactPerson: [
      { required: true, message: '请输入联系人', trigger: 'blur' }
    ],
    contactPhone: [
      { required: true, message: '请输入联系电话', trigger: 'blur' }
    ],
    status: [{ required: true, message: '请选择客户状态', trigger: 'change' }]
  });

  function resetFormForCreate() {
    Object.assign(form, {
      id: undefined,
      customerCode: undefined,
      customerName: undefined,
      shortName: undefined,
      customerType: undefined,
      contactPerson: undefined,
      contactPhone: undefined,
      address: undefined,
      settlementType: undefined,
      creditCode: undefined,
      status: 1,
      remark: undefined,
      paymentDays: undefined,
      creditLimit: undefined,
      creditStatus: 1
    });
  }

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      if (props.data?.id) {
        Object.assign(form, props.data);
      } else {
        resetFormForCreate();
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const buildPayload = (): Customer => {
    const payload: Customer = { ...form };
    if (!payload.customerCode?.trim()) {
      delete payload.customerCode;
    }
    delete payload.creditStatusLabel;
    // 账期与额度清空是真实诉求（改回未设置 / 不限额），显式传 null 让后端清列
    payload.paymentDays = payload.paymentDays ?? null;
    payload.creditLimit = payload.creditLimit ?? null;
    return payload;
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const payload = buildPayload();
        if (isEdit.value) {
          await updateCustomer(payload);
        } else {
          await addCustomer(payload);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .customer-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  .customer-edit-form :deep(.el-divider) {
    margin: 0 0 18px;
  }

  .credit-tip {
    margin-top: -8px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.7;
  }
</style>
