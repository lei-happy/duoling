<template>
  <div class="ai-input">
    <!-- 已选附件 -->
    <div v-if="attachments.length" class="ai-input__attachments">
      <div v-for="att in attachments" :key="att.fileId" class="ai-input__attach">
        <el-icon><paperclip /></el-icon>
        <span class="ai-input__attach-name">{{ att.name }}</span>
        <el-icon class="ai-input__attach-del" @click="removeAttach(att.fileId)">
          <close />
        </el-icon>
      </div>
    </div>

    <el-input
      v-model="text"
      type="textarea"
      :autosize="{ minRows: 2, maxRows: 6 }"
      :placeholder="placeholder"
      resize="none"
      :disabled="disabled"
      @keydown.enter.exact.prevent="handleSubmit"
      @keydown.enter.shift.exact="onShiftEnter"
    />

    <div class="ai-input__bar">
      <el-tooltip content="上传 Excel/CSV 等附件（≤20MB）" placement="top">
        <el-button :icon="Paperclip" :loading="uploading" @click="pickFile">
          附件
        </el-button>
      </el-tooltip>
      <input
        ref="fileInputRef"
        type="file"
        accept=".xlsx,.xls,.csv,.pdf,.png,.jpg,.jpeg"
        style="display: none"
        @change="onFileChange"
      />
      <span class="ai-input__hint">Enter 发送 / Shift+Enter 换行</span>
      <el-button
        type="primary"
        :icon="Promotion"
        :loading="disabled"
        :disabled="!text.trim() && !attachments.length"
        @click="handleSubmit"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { ElMessage } from 'element-plus';
  import {
    Paperclip,
    Promotion,
    Close
  } from '@element-plus/icons-vue';
  import { uploadAiAttach } from '@/api/ai';
  import type { AiAttachment } from '@/api/ai/model';

  const props = defineProps<{
    disabled?: boolean;
    placeholder?: string;
  }>();

  const emit = defineEmits<{
    (e: 'send', payload: { content: string; attachments: AiAttachment[] }): void;
  }>();

  const text = ref('');
  const attachments = ref<AiAttachment[]>([]);
  const uploading = ref(false);
  const fileInputRef = ref<HTMLInputElement | null>(null);

  watch(
    () => props.disabled,
    (v) => {
      if (v) return;
      // 解锁后聚焦
    }
  );

  function onShiftEnter() {
    /* 默认换行行为 */
  }

  function handleSubmit() {
    if (props.disabled) return;
    const trimmed = text.value.trim();
    if (!trimmed && !attachments.value.length) return;
    emit('send', {
      content: trimmed,
      attachments: [...attachments.value]
    });
    text.value = '';
    attachments.value = [];
  }

  function pickFile() {
    fileInputRef.value?.click();
  }

  async function onFileChange(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    target.value = '';
    if (!file) return;
    if (file.size > 20 * 1024 * 1024) {
      ElMessage.error('附件大小不能超过 20MB');
      return;
    }
    uploading.value = true;
    try {
      const att = await uploadAiAttach(file);
      attachments.value.push(att);
    } catch (err: any) {
      ElMessage.error(err?.message || '上传失败');
    } finally {
      uploading.value = false;
    }
  }

  function removeAttach(fileId: string) {
    attachments.value = attachments.value.filter((a) => a.fileId !== fileId);
  }
</script>

<style lang="scss" scoped>
  .ai-input {
    border-top: 1px solid var(--el-border-color-light);
    padding: 10px 12px 12px;
    background: var(--el-bg-color);

    &__attachments {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 6px;
    }
    &__attach {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 6px;
      background: var(--el-fill-color-light);
      font-size: 12px;
    }
    &__attach-name {
      max-width: 220px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    &__attach-del {
      cursor: pointer;
      color: var(--el-text-color-placeholder);
      &:hover {
        color: var(--el-color-danger);
      }
    }
    &__bar {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
    }
    &__hint {
      flex: 1;
      font-size: 12px;
      color: var(--el-text-color-placeholder);
      text-align: right;
    }
  }
</style>
