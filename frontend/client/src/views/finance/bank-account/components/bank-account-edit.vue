<!-- 银行账户新增 / 编辑 -->
<template>
  <el-dialog
    :model-value="visible"
    :title="account ? '编辑账户' : '新增账户'"
    width="560px"
    top="8vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="close"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent
    >
      <el-form-item label="经营主体" prop="enterpriseId">
        <business-entity-select
          v-model="form.enterpriseId"
          :disabled="!!account"
          :auto-default="!account"
        />
      </el-form-item>
      <el-form-item label="账户名称" prop="accountName">
        <el-input
          v-model="form.accountName"
          placeholder="如：某某物流有限公司基本户"
          maxlength="100"
        />
      </el-form-item>
      <el-form-item label="银行账号" prop="accountNo">
        <el-input
          v-model="form.accountNo"
          placeholder="填完整账号，列表只展示后四位"
          maxlength="50"
        />
      </el-form-item>
      <el-form-item label="开户银行">
        <el-input
          v-model="form.bankName"
          placeholder="如：工商银行"
          maxlength="100"
        />
      </el-form-item>
      <el-form-item label="开户网点">
        <el-input
          v-model="form.bankBranch"
          placeholder="如：某某支行"
          maxlength="100"
        />
      </el-form-item>
      <el-form-item label="账户类型">
        <el-select v-model="form.accountType" style="width: 100%">
          <el-option
            v-for="o in BANK_ACCOUNT_TYPE_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="收付用途">
        <el-select v-model="form.usageScope" style="width: 100%">
          <el-option
            v-for="o in ACCOUNT_USAGE_SCOPE_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="!account" label="账面余额">
        <el-input-number
          v-model="form.balance"
          :precision="2"
          :controls="false"
          placeholder="建档时的账面余额，之后由收付款自动增减"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="默认账户">
        <el-checkbox v-model="defaultReceive">收款默认用它</el-checkbox>
        <el-checkbox v-model="defaultPay">付款默认用它</el-checkbox>
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          maxlength="255"
          show-word-limit
        />
      </el-form-item>
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
