<template>
  <div>
    <ele-alert
      show-icon
      title="确认转账后，资金将直接打入对方账户，无法退回。"
      style="margin-bottom: 18px"
    />
    <el-descriptions
      :border="true"
      :column="1"
      size="large"
      class="detail-table"
    >
      <el-descriptions-item label="付款账户">
        <div>{{ data.account }}</div>
      </el-descriptions-item>
      <el-descriptions-item label="收款账户">
        <div>{{ data.receiver }}</div>
      </el-descriptions-item>
      <el-descriptions-item label="收款人姓名">
        <div>{{ data.name }}</div>
      </el-descriptions-item>
      <el-descriptions-item label="转账金额">
        <div style="display: flex; align-items: flex-end">
          <ele-text size="xl" style="line-height: 1">
            {{ data.amount }}&nbsp;
          </ele-text>
          <div style="line-height: 1.15">&nbsp;元</div>
        </div>
      </el-descriptions-item>
      <el-descriptions-item label="支付密码">
        <div style="max-width: 220px">
          <el-input
            type="password"
            v-model="form.password"
            placeholder="请输入支付密码"
            show-password
          />
        </div>
      </el-descriptions-item>
    </el-descriptions>
    <div style="margin-top: 22px; padding-left: 140px">
      <el-button type="primary" :loading="loading" @click="submit">
        下一步
      </el-button>
      <el-button @click="back">上一步</el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { StepForm } from '../model';

  defineProps<{
    data: StepForm;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
    (e: 'back'): void;
  }>();

  /** 提交状态 */
  const loading = ref(false);

  /** 表单数据 */
  const form = reactive({
    password: '123456'
  });

  /** 下一步 */
  const submit = () => {
    if (!form.password) {
      EleMessage.error({ message: '请输入支付密码', plain: true });
      return;
    }
    loading.value = true;
    setTimeout(() => {
      loading.value = false;
      emit('done');
    }, 300);
  };

  /** 上一步 */
  const back = () => {
    emit('back');
  };
</script>

<style lang="scss" scoped>
  .detail-table :deep(td.el-descriptions__label.el-descriptions__cell) {
    width: 120px;
    text-align: right;
    font-weight: normal;
  }
</style>
