<!-- 反馈详情弹窗：区分「我提交的」与「官方回复」 -->
<template>
  <el-dialog
    :model-value="modelValue"
    width="640px"
    align-center
    destroy-on-close
    append-to-body
    class="feedback-detail-dialog"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template #header>
      <div class="feedback-detail__header">
        <h3 class="feedback-detail__title">反馈详情</h3>
        <div v-if="detail" class="feedback-detail__meta">
          <el-tag size="small" :disable-transitions="true">
            {{ typeLabel(detail.feedback_type) }}
          </el-tag>
          <el-tag
            :type="statusTagType(detail.status)"
            size="small"
            :disable-transitions="true"
          >
            {{ statusLabel(detail.status) }}
          </el-tag>
        </div>
      </div>
    </template>

    <div v-if="detail" class="feedback-detail__body">
      <!-- 用户提交 -->
      <section class="feedback-panel feedback-panel--user">
        <div class="feedback-panel__head">
          <span class="feedback-panel__badge">我提交的</span>
          <span class="feedback-panel__time">
            {{ formatDateTime(detail.created_at) }}
          </span>
        </div>
        <div v-if="showSubmitter" class="feedback-panel__submitter">
          提交人 · {{ detail.user_name || '-' }}
        </div>
        <div class="feedback-panel__content">{{ detail.content }}</div>
        <div v-if="detail.images?.length" class="feedback-panel__images">
          <el-image
            v-for="(url, idx) in detail.images"
            :key="url + idx"
            :src="resolveUploadUrl(url)"
            fit="cover"
            :preview-src-list="previewList"
            :initial-index="idx"
            class="feedback-panel__image"
          />
        </div>
      </section>

      <!-- 官方回复 -->
      <section
        class="feedback-panel feedback-panel--official"
        :class="{ 'is-empty': !detail.reply }"
      >
        <div class="feedback-panel__head">
          <span class="feedback-panel__badge feedback-panel__badge--official">
            官方回复
          </span>
          <span
            v-if="detail.reply && detail.replied_at"
            class="feedback-panel__time"
          >
            {{ formatDateTime(detail.replied_at) }}
          </span>
        </div>

        <template v-if="detail.reply">
          <div class="feedback-panel__content">{{ detail.reply }}</div>
          <div v-if="detail.handler_name" class="feedback-panel__handler">
            处理人 · {{ detail.handler_name }}
          </div>
        </template>
        <div v-else class="feedback-panel__empty">
          <p class="feedback-panel__empty-title">还在处理中</p>
          <p class="feedback-panel__empty-desc">
            我们已收到你的反馈，有进展会在这里回复
          </p>
        </div>
      </section>
    </div>

    <template #footer>
      <el-button type="primary" @click="emit('update:modelValue', false)">
        知道了
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { Feedback } from '@/api/feedback/model';
  import { resolveUploadUrl } from '@/utils/upload-url';
  import { formatDateTime } from '@/utils/date-util';

  const props = defineProps<{
    modelValue: boolean;
    detail: Feedback | null;
    showSubmitter?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void;
  }>();

  const previewList = computed(() =>
    (props.detail?.images || []).map((u) => resolveUploadUrl(u))
  );

  const typeLabel = (t?: number) =>
    ({ 0: '建议', 1: '缺陷', 2: '投诉', 3: '其他' })[t ?? -1] || '-';

  const statusLabel = (s?: number) =>
    ({ 0: '待处理', 1: '处理中', 2: '已解决', 3: '已关闭' })[s ?? -1] || '-';

  const statusTagType = (s?: number) =>
    ({ 0: 'info', 1: 'warning', 2: 'success', 3: 'info' })[s ?? -1] || 'info';
</script>

<style scoped>
  .feedback-detail__header {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding-right: 28px;
  }

  .feedback-detail__title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--el-text-color-primary);
  }

  .feedback-detail__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .feedback-detail__body {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .feedback-panel {
    border-radius: 12px;
    padding: 16px 18px;
    border: 1px solid var(--el-border-color-lighter);
  }

  .feedback-panel--user {
    background: var(--el-fill-color-blank);
  }

  .feedback-panel--official {
    background: color-mix(in srgb, var(--el-color-primary) 5%, transparent);
    border-color: color-mix(
      in srgb,
      var(--el-color-primary) 22%,
      var(--el-border-color-lighter)
    );
  }

  .feedback-panel--official.is-empty {
    background: var(--el-fill-color-lighter);
    border-color: var(--el-border-color-extra-light);
    border-style: dashed;
  }

  .feedback-panel__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
  }

  .feedback-panel__badge {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-regular);
    background: var(--el-fill-color);
  }

  .feedback-panel__badge--official {
    color: var(--el-color-primary);
    background: color-mix(in srgb, var(--el-color-primary) 12%, transparent);
  }

  .feedback-panel__time {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
  }

  .feedback-panel__submitter {
    margin: -4px 0 10px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .feedback-panel__content {
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    color: var(--el-text-color-primary);
  }

  .feedback-panel__images {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
  }

  .feedback-panel__image {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    overflow: hidden;
  }

  .feedback-panel__handler {
    margin-top: 12px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .feedback-panel__empty {
    padding: 6px 0 2px;
  }

  .feedback-panel__empty-title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-regular);
  }

  .feedback-panel__empty-desc {
    margin: 6px 0 0;
    font-size: 13px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }
</style>

<style>
  .feedback-detail-dialog.el-dialog {
    border-radius: 16px;
    overflow: hidden;
  }

  .feedback-detail-dialog .el-dialog__header {
    margin-right: 0;
    padding: 22px 24px 10px;
  }

  .feedback-detail-dialog .el-dialog__headerbtn {
    top: 18px;
    right: 16px;
  }

  .feedback-detail-dialog .el-dialog__body {
    padding: 8px 24px 4px;
  }

  .feedback-detail-dialog .el-dialog__footer {
    padding: 12px 24px 20px;
  }
</style>
