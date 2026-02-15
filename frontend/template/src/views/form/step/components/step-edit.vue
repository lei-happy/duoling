<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="108px"
    style="padding-right: 60px"
    @submit.prevent=""
  >
    <el-form-item label="付款账户" prop="account">
      <el-select
        clearable
        v-model="form.account"
        placeholder="请选择付款账户"
        class="ele-fluid"
      >
        <el-option value="plus@eleadmin.com" label="plus@eleadmin.com" />
        <el-option value="pro@eleadmin.com" label="pro@eleadmin.com" />
      </el-select>
    </el-form-item>
    <el-form-item label="收款账户" prop="receiver">
      <el-input clearable v-model="form.receiver" placeholder="请输入收款账户">
        <template #prepend>
          <el-select v-model="form.pay" style="width: 100px">
            <el-option value="alipay" label="支付宝" />
            <el-option value="wxpay" label="微信" />
          </el-select>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item label="收款人姓名" prop="name">
      <el-input clearable v-model="form.name" placeholder="请输入收款人姓名" />
    </el-form-item>
    <el-form-item label="转账金额" prop="amount">
      <el-input
        clearable
        v-model="form.amount"
        placeholder="请输入转账金额"
        :prefix-icon="prefixIcon"
      />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="loading" @click="submit">
        下一步
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
  import { ref, reactive, h } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { numberReg } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import type { StepForm } from '../model';

  const emit = defineEmits<{
    (e: 'done', data: StepForm): void;
  }>();

  const prefixIcon = h('span', { style: { fontStyle: 'normal' } }, '￥');

  /** 提交状态 */
  const loading = ref(false);

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form] = useFormData<StepForm>({
    account: 'plus@eleadmin.com',
    receiver: 'test@example.com',
    pay: 'alipay',
    name: 'Alex',
    amount: '500'
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    account: [
      {
        required: true,
        message: '请选择付款账户',
        type: 'string',
        trigger: 'change'
      }
    ],
    receiver: [
      {
        required: true,
        message: '请输入收款账户',
        type: 'string',
        trigger: 'blur'
      }
    ],
    name: [
      {
        required: true,
        message: '请输入收款人姓名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    amount: [
      {
        required: true,
        message: '请输入转账金额',
        type: 'string',
        trigger: 'blur'
      },
      {
        pattern: numberReg,
        message: '请输入合法金额数字',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  /** 步骤一提交 */
  const submit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      setTimeout(() => {
        loading.value = false;
        emit('done', form);
      }, 300);
    });
  };
</script>
