<!-- 银行账户新增 / 编辑 -->
<template>
  <el-dialog
    :model-value="visible"
    :title="account ? '编辑账户' : '新增账户'"
    width="640px"
    top="8vh"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="close"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="finance-edit-form"
      @submit.prevent
    >
      <el-row :gutter="16">
        <el-col :span="24">
          <el-form-item prop="enterpriseId">
            <div class="finance-entity-field">
              <span>经营主体</span>
              <business-entity-select
                v-model="form.enterpriseId"
                :disabled="!!account"
                :auto-default="!account"
              />
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="accountName">
            <floating-label
              label="请输入账户名称"
              type="input"
              v-model="form.accountName"
              :maxlength="100"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="accountNo">
            <floating-label
              label="请输入银行账号，列表只展示后四位"
              type="input"
              v-model="form.accountNo"
              :maxlength="50"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入开户银行"
              type="input"
              v-model="form.bankName"
              :maxlength="100"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入开户网点"
              type="input"
              v-model="form.bankBranch"
              :maxlength="100"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.accountType"
              label="请选择账户类型"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in BANK_ACCOUNT_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              v-model="form.usageScope"
              label="请选择收付用途"
              type="select"
              :clearable="false"
            >
              <el-option
                v-for="o in ACCOUNT_USAGE_SCOPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col v-if="!account" :span="24">
          <el-form-item>
            <floating-label
              v-model="form.balance"
              label="请输入建档账面余额"
              type="input-number"
              :input-number-precision="2"
              :input-number-step="100"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <div class="finance-switch-field">
              <span>默认账户</span>
              <div>
                <el-checkbox v-model="defaultReceive">收款默认用它</el-checkbox>
                <el-checkbox v-model="defaultPay">付款默认用它</el-checkbox>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入备注，选填"
              type="input"
              input-type="textarea"
              v-model="form.remark"
              :maxlength="255"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { FormInstance, FormRules } from 'element-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import BusinessEntitySelect from '@/components/BusinessEntitySelect/index.vue';
  import {
    createBankAccount,
    updateBankAccount
  } from '@/api/finance/bank-account';
  import type {
    BankAccountItem,
    BankAccountPayload
  } from '@/api/finance/bank-account/model';
  import {
    ACCOUNT_USAGE_SCOPE_OPTIONS,
    BANK_ACCOUNT_TYPE_OPTIONS
  } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    account?: BankAccountItem | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const saving = ref(false);
  const defaultReceive = ref(false);
  const defaultPay = ref(false);

  const form = reactive<BankAccountPayload>({
    accountType: 2,
    usageScope: 1,
    currency: 'CNY'
  });

  const rules = computed<FormRules>(() => ({
    enterpriseId: [
      { required: true, message: '请选择账户归属的经营主体', trigger: 'change' }
    ],
    accountName: [{ required: true, message: '请填账户名称', trigger: 'blur' }],
    accountNo: [{ required: true, message: '请填银行账号', trigger: 'blur' }]
  }));

  const reset = () => {
    const a = props.account;
    form.enterpriseId = a?.enterpriseId;
    form.accountName = a?.accountName;
    form.accountNo = a?.accountNo;
    form.bankName = a?.bankName;
    form.bankBranch = a?.bankBranch;
    form.accountType = a?.accountType ?? 2;
    form.usageScope = a?.usageScope ?? 1;
    form.currency = a?.currency ?? 'CNY';
    form.balance = a ? undefined : 0;
    form.remark = a?.remark;
    defaultReceive.value = a?.isDefaultReceive === 1;
    defaultPay.value = a?.isDefaultPay === 1;
  };

  watch(
    () => props.visible,
    (v) => {
      if (v) {
        reset();
        formRef.value?.clearValidate();
      }
    }
  );

  const close = () => emit('update:visible', false);

  const submit = async () => {
    if (!formRef.value) return;
    try {
      await formRef.value.validate();
    } catch {
      return;
    }
    saving.value = true;
    const payload: BankAccountPayload = {
      ...form,
      isDefaultReceive: defaultReceive.value ? 1 : 0,
      isDefaultPay: defaultPay.value ? 1 : 0
    };
    try {
      if (props.account) {
        delete payload.enterpriseId;
        delete payload.balance;
        await updateBankAccount(props.account.id, payload);
        EleMessage.success('账户已保存');
      } else {
        await createBankAccount(payload);
        EleMessage.success('账户已添加');
      }
      emit('done');
      close();
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '保存失败，请重试',
        plain: true
      });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  @use '../../_shared/ui.scss';
</style>
