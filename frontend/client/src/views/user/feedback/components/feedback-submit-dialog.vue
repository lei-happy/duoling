<!-- 提交意见反馈弹窗：选类型 → 写一段话 → 可选附图 -->
<template>
  <el-dialog
    :model-value="modelValue"
    width="680px"
    align-center
    destroy-on-close
    append-to-body
    :close-on-click-modal="false"
    class="feedback-submit-dialog"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template #header>
      <div class="feedback-dialog__header">
        <h3 class="feedback-dialog__title">提交意见反馈</h3>
        <p class="feedback-dialog__sub">
          选个类型，把情况说清楚即可；有截图更好帮我们对症处理
        </p>
      </div>
    </template>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="feedback-dialog__form"
      @submit.prevent=""
    >
      <el-form-item prop="feedback_type" class="feedback-dialog__item--type">
        <template #label>
          <span class="feedback-dialog__label">反馈类型</span>
        </template>
        <div class="feedback-type-grid" role="radiogroup" aria-label="反馈类型">
          <button
            v-for="opt in typeOptions"
            :key="opt.value"
            type="button"
            role="radio"
            :aria-checked="form.feedback_type === opt.value"
            class="feedback-type-card"
            :class="{ 'is-active': form.feedback_type === opt.value }"
            @click="form.feedback_type = opt.value"
          >
            <span class="feedback-type-card__label">{{ opt.label }}</span>
            <span class="feedback-type-card__hint">{{ opt.hint }}</span>
          </button>
        </div>
      </el-form-item>

      <el-form-item prop="content" class="feedback-dialog__item--content">
        <template #label>
          <span class="feedback-dialog__label">你想反馈什么</span>
        </template>
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="7"
          maxlength="2000"
          show-word-limit
          resize="none"
          placeholder="直接写就行，例如：运单导出点了没反应，浏览器提示超时。希望能导出成功或给出明确提示。"
        />
      </el-form-item>

      <div class="feedback-dialog__secondary">
        <el-form-item label="截图（可选）" class="feedback-dialog__item--photos">
          <div class="feedback-photos">
            <div
              v-for="(url, idx) in form.images"
              :key="url + idx"
              class="feedback-photos__item"
            >
              <el-image
                :src="resolveUploadUrl(url)"
                fit="cover"
                :preview-src-list="previewList"
                :initial-index="idx"
              />
              <button
                type="button"
                class="feedback-photos__remove"
                aria-label="移除截图"
                @click="removeImage(idx)"
              >
                <el-icon :size="12"><Close /></el-icon>
              </button>
            </div>
            <el-upload
              v-if="form.images.length < 5"
              class="feedback-photos__add"
              accept="image/*"
              :show-file-list="false"
              :before-upload="beforeUpload"
            >
              <el-icon :size="18"><Plus /></el-icon>
              <span>添加截图</span>
            </el-upload>
          </div>
          <div class="feedback-dialog__tip">最多 5 张，每张不超过 5MB</div>
        </el-form-item>

        <el-form-item
          label="联系电话（可选）"
          prop="contact_phone"
          class="feedback-dialog__item--phone"
        >
          <el-input
            v-model="form.contact_phone"
            maxlength="20"
            placeholder="默认使用登录手机号，可修改"
          />
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="feedback-dialog__footer">
        <el-button
          v-if="showMyLink"
          link
          type="primary"
          class="feedback-dialog__link"
          @click="emit('view-list')"
        >
          查看我的反馈
        </el-button>
        <div class="feedback-dialog__actions">
          <el-button @click="emit('update:modelValue', false)">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submit">
            提交反馈
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { Close, Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { createFeedback } from '@/api/feedback';
  import { uploadFile } from '@/api/system/file';
  import { useUserStore } from '@/store/modules/user';
  import { resolveUploadUrl } from '@/utils/upload-url';

  const props = withDefaults(
    defineProps<{
      modelValue: boolean;
      /** 是否展示「查看我的反馈」入口（顶栏快捷提交时用） */
      showMyLink?: boolean;
    }>(),
    { showMyLink: false }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void;
    (e: 'done'): void;
    (e: 'view-list'): void;
  }>();

  const userStore = useUserStore();
  const formRef = ref<FormInstance | null>(null);
  const submitting = ref(false);

  const typeOptions = [
    { value: 0, label: '建议', hint: '想要更好用' },
    { value: 1, label: '缺陷', hint: '出错或异常' },
    { value: 2, label: '投诉', hint: '体验不满意' },
    { value: 3, label: '其他', hint: '不好归类时' }
  ];

  const form = reactive({
    feedback_type: 0,
    content: '',
    images: [] as string[],
    contact_phone: ''
  });

  const rules: FormRules = {
    feedback_type: [
      { required: true, message: '请选择反馈类型', trigger: 'change' }
    ],
    content: [
      { required: true, message: '请填写你想反馈的内容', trigger: 'blur' }
    ]
  };

  const previewList = computed(() =>
    form.images.map((u) => resolveUploadUrl(u))
  );

  /** 用正文首行/前 40 字生成列表用标题，用户无需单独填写 */
  const deriveTitle = (text: string) => {
    const compact = text.replace(/\s+/g, ' ').trim();
    if (!compact) return '用户反馈';
    const firstLine = text
      .split(/\r?\n/)
      .map((s) => s.trim())
      .find(Boolean);
    const source = (firstLine || compact).replace(/\s+/g, ' ');
    return source.length > 40 ? `${source.slice(0, 40)}…` : source;
  };

  const resetForm = () => {
    form.feedback_type = 0;
    form.content = '';
    form.images = [];
    form.contact_phone = userStore.info?.phone || '';
    formRef.value?.clearValidate?.();
  };

  watch(
    () => props.modelValue,
    (open) => {
      if (open) resetForm();
    }
  );

  const removeImage = (idx: number) => {
    form.images.splice(idx, 1);
  };

  const beforeUpload = async (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      EleMessage.error({ message: '图片不能超过 5MB', plain: true });
      return false;
    }
    try {
      const res = await uploadFile(file, undefined, file.name, 'feedback');
      if (res?.url) {
        form.images.push(res.url);
      }
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '上传失败，请重试',
        plain: true
      });
    }
    return false;
  };

  const submit = () => {
    formRef.value?.validate?.(async (valid) => {
      if (!valid) return;
      const content = form.content.trim();
      submitting.value = true;
      const loading = EleMessage.loading({
        message: '正在提交反馈，请稍候…',
        plain: true
      });
      try {
        const res = await createFeedback({
          feedback_type: form.feedback_type,
          title: deriveTitle(content),
          content,
          images: form.images,
          contact_phone: form.contact_phone?.trim() || undefined
        });
        loading.close();
        EleMessage.success({
          message: res.message || '反馈已提交，我们会尽快处理',
          plain: true
        });
        emit('update:modelValue', false);
        emit('done');
      } catch (e: any) {
        loading.close();
        EleMessage.error({
          message: e.message || '提交失败，请稍后重试',
          plain: true
        });
      } finally {
        submitting.value = false;
      }
    });
  };
</script>

<style scoped>
  .feedback-dialog__header {
    padding-right: 28px;
  }

  .feedback-dialog__title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.01em;
    line-height: 1.3;
    color: var(--el-text-color-primary);
  }

  .feedback-dialog__sub {
    margin: 6px 0 0;
    font-size: 13px;
    line-height: 1.55;
    color: var(--el-text-color-secondary);
  }

  .feedback-dialog__form {
    padding-top: 2px;
  }

  .feedback-dialog__label {
    font-weight: 600;
  }

  .feedback-dialog__form :deep(.el-form-item__label) {
    margin-bottom: 8px !important;
    color: var(--el-text-color-primary);
  }

  .feedback-dialog__item--type {
    margin-bottom: 18px;
  }

  .feedback-dialog__item--content {
    margin-bottom: 18px;
  }

  .feedback-dialog__item--content :deep(.el-textarea__inner) {
    padding: 12px 14px;
    line-height: 1.65;
    border-radius: 10px;
    font-size: 14px;
  }

  .feedback-type-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    width: 100%;
  }

  .feedback-type-card {
    appearance: none;
    border: 1px solid var(--el-border-color);
    background: var(--el-bg-color);
    border-radius: 12px;
    padding: 14px 12px;
    text-align: left;
    cursor: pointer;
    min-height: 68px;
    transition:
      border-color 160ms ease-out,
      background-color 160ms ease-out,
      transform 120ms ease-out,
      box-shadow 160ms ease-out;
  }

  .feedback-type-card:hover {
    border-color: color-mix(
      in srgb,
      var(--el-color-primary) 40%,
      var(--el-border-color)
    );
  }

  .feedback-type-card:active {
    transform: scale(0.985);
  }

  .feedback-type-card.is-active {
    border-color: var(--el-color-primary);
    background: color-mix(in srgb, var(--el-color-primary) 7%, transparent);
    box-shadow: inset 0 0 0 1px
      color-mix(in srgb, var(--el-color-primary) 35%, transparent);
  }

  .feedback-type-card.is-active .feedback-type-card__label {
    color: var(--el-color-primary);
  }

  .feedback-type-card__label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .feedback-type-card__hint {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    line-height: 1.4;
    color: var(--el-text-color-secondary);
  }

  .feedback-dialog__secondary {
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 16px 20px;
    align-items: start;
  }

  .feedback-dialog__item--photos,
  .feedback-dialog__item--phone {
    margin-bottom: 0;
  }

  .feedback-photos {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .feedback-photos__item {
    position: relative;
    width: 76px;
    height: 76px;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--el-border-color-lighter);
  }

  .feedback-photos__item :deep(.el-image) {
    width: 100%;
    height: 100%;
  }

  .feedback-photos__remove {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 18px;
    height: 18px;
    border: none;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #fff;
    background: rgba(0, 0, 0, 0.5);
    padding: 0;
  }

  .feedback-photos__add {
    width: 76px;
    height: 76px;
    border: 1px dashed var(--el-border-color);
    border-radius: 10px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    background: var(--el-fill-color-lighter);
    transition:
      border-color 160ms ease-out,
      color 160ms ease-out,
      background-color 160ms ease-out;
  }

  .feedback-photos__add:hover {
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
    background: color-mix(in srgb, var(--el-color-primary) 6%, transparent);
  }

  .feedback-photos__add :deep(.el-upload) {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }

  .feedback-dialog__tip {
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .feedback-dialog__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .feedback-dialog__link {
    padding-left: 0;
  }

  .feedback-dialog__actions {
    margin-left: auto;
    display: flex;
    gap: 8px;
  }

  @media (max-width: 720px) {
    .feedback-type-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .feedback-dialog__secondary {
      grid-template-columns: 1fr;
    }
  }
</style>

<style>
  .feedback-submit-dialog.el-dialog {
    border-radius: 16px;
    overflow: hidden;
  }

  .feedback-submit-dialog .el-dialog__header {
    margin-right: 0;
    padding: 22px 24px 8px;
  }

  .feedback-submit-dialog .el-dialog__headerbtn {
    top: 18px;
    right: 16px;
  }

  .feedback-submit-dialog .el-dialog__body {
    padding: 8px 24px 6px;
  }

  .feedback-submit-dialog .el-dialog__footer {
    padding: 14px 24px 20px;
    border-top: 1px solid var(--el-border-color-extra-light);
  }
</style>
