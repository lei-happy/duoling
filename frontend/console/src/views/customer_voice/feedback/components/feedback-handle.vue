<!-- 处理意见反馈 -->
<template>
  <ele-modal
    form
    :width="720"
    title="处理反馈"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-descriptions v-if="detail" :column="2" border class="mb-16">
      <el-descriptions-item label="租户">
        {{ detail.tenant_name || detail.tenant_code || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="提交人">
        {{ detail.user_name || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="联系电话">
        {{ detail.contact_phone || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="提交时间">
        {{ detail.created_at || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="类型">
        {{ typeLabel(detail.feedback_type) }}
      </el-descriptions-item>
      <el-descriptions-item label="标题" :span="2">
        {{ detail.title }}
      </el-descriptions-item>
      <el-descriptions-item label="内容" :span="2">
        <div class="feedback-content">{{ detail.content }}</div>
      </el-descriptions-item>
      <el-descriptions-item
        v-if="detail.images?.length"
        label="截图"
        :span="2"
      >
        <div class="feedback-images">
          <el-image
            v-for="(url, idx) in detail.images"
            :key="url + idx"
            :src="url"
            fit="cover"
            :preview-src-list="detail.images"
            :initial-index="idx"
            class="feedback-images__item"
          />
        </div>
      </el-descriptions-item>
    </el-descriptions>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="88px">
      <el-form-item label="处理状态" prop="status">
        <el-select
          v-model="form.status"
          placeholder="请选择状态"
          style="width: 100%"
        >
          <el-option label="待处理" :value="0" />
          <el-option label="处理中" :value="1" />
          <el-option label="已解决" :value="2" />
          <el-option label="已关闭" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="回复内容" prop="reply">
        <el-input
          v-model="form.reply"
          type="textarea"
          :rows="4"
          maxlength="2000"
          show-word-limit
          placeholder="回复将展示给提交用户"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          {
            preset: 'cancel',
            onClick: () => modalProps.onCancel?.()
          },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { getFeedback, handleFeedback } from '@/api/feedback';
  import type { Feedback } from '@/api/feedback/model';

  const props = defineProps<{
    data?: Feedback | null;
    onDone?: () => void;
  }>();

  const { modalProps, closeModal } = useModal();
  const loading = ref(false);
  const detail = ref<Feedback | null>(null);
  const formRef = ref<FormInstance | null>(null);
  const form = reactive({
    status: 0,
    reply: ''
  });

  const rules: FormRules = {
    status: [{ required: true, message: '请选择处理状态', trigger: 'change' }]
  };

  const typeLabel = (t?: number) =>
    ({ 0: '建议', 1: '缺陷', 2: '投诉', 3: '其他' })[t ?? -1] || '-';

  onMounted(async () => {
    if (!props.data?.id) return;
    loading.value = true;
    try {
      detail.value = (await getFeedback(props.data.id)) || null;
      form.status = detail.value?.status ?? 0;
      form.reply = detail.value?.reply || '';
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载失败，请重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  });

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid || !props.data?.id) return;
      const loadingMsg = EleMessage.loading({
        message: '正在保存处理结果，请稍候…',
        plain: true
      });
      handleFeedback(props.data.id, {
        status: form.status,
        reply: form.reply
      })
        .then((msg) => {
          loadingMsg.close();
          EleMessage.success({
            message: msg || '已更新处理结果',
            plain: true
          });
          props.onDone?.();
          closeModal();
        })
        .catch((e) => {
          loadingMsg.close();
          EleMessage.error({
            message: e.message || '保存失败，请稍后重试',
            plain: true
          });
        });
    });
  };
</script>

<style scoped>
  .mb-16 {
    margin-bottom: 16px;
  }
  .feedback-content {
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
  }
  .feedback-images {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .feedback-images__item {
    width: 72px;
    height: 72px;
    border-radius: 4px;
  }
</style>
