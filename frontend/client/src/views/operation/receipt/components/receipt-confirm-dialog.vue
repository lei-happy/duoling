<!--
  确认回单弹窗

  业务：计划全量签收（status=5 已签收）后，把签收底单返还货主即"回单"。
  本弹窗上传回单底单凭证 + 回收时间 + 备注，提交后计划 5 → 6 已回单。
  仅计划维度动作，不影响任务状态机。
-->
<template>
  <el-dialog
    :model-value="visible"
    title="确认回单"
    width="640px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="waybill"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="`计划 ${waybill.waybillNo} · ${waybill.customerName || '--'} · ${waybill.origin || '--'} → ${waybill.destination || '--'}`"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="92px"
      v-loading="loading"
    >
      <el-form-item label="回收时间" prop="receivedAt" required>
        <el-date-picker
          v-model="form.receivedAt"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          placeholder="选择底单回收时间"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="回单底单">
        <div class="photo-uploader">
          <div
            v-for="(url, idx) in form.fileUrls"
            :key="url"
            class="photo-item"
          >
            <el-image
              :src="url"
              fit="cover"
              :preview-src-list="form.fileUrls"
              :initial-index="idx"
            />
            <el-icon class="photo-remove" @click="removeFile(idx)">
              <Close />
            </el-icon>
          </div>
          <el-upload
            v-if="form.fileUrls.length < 9"
            class="photo-add"
            accept="image/*"
            :show-file-list="false"
            :before-upload="beforeUpload"
          >
            <el-icon><Plus /></el-icon>
            <span class="photo-add__hint">添加底单</span>
          </el-upload>
        </div>
        <div class="ele-text-secondary mt-4">
          最多 9 张，每张不超过 5MB（底单图片可选，便于追溯）。
        </div>
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="可选"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        确认回单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { Close, Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { confirmWaybillReceipt } from '@/api/waybill';
  import { uploadFile } from '@/api/system/file';
  import type { Waybill } from '@/api/waybill/model';

  const props = defineProps<{
    visible: boolean;
    waybill: Waybill | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const loading = ref(false);
  const submitting = ref(false);

  const form = reactive({
    receivedAt: '',
    fileUrls: [] as string[],
    remark: ''
  });

  const rules: FormRules = {
    receivedAt: [{ required: true, message: '请选择底单回收时间' }]
  };

  const onOpen = () => {
    form.receivedAt = new Date().toISOString().slice(0, 19);
    form.fileUrls = [];
    form.remark = '';
  };

  const beforeUpload = async (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      EleMessage.error({ message: '图片不能超过 5MB', plain: true });
      return false;
    }
    try {
      const res = await uploadFile(file, undefined, file.name, 'waybill_receipt');
      if (res?.url) {
        form.fileUrls.push(res.url);
        EleMessage.success({ message: '上传成功', plain: true });
      }
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '上传失败',
        plain: true
      });
    }
    return false;
  };

  const removeFile = (idx: number) => {
    form.fileUrls.splice(idx, 1);
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (!props.waybill?.id) return;
    submitting.value = true;
    try {
      await confirmWaybillReceipt(props.waybill.id, {
        fileUrls: form.fileUrls,
        fileType: 1,
        receivedAt: form.receivedAt,
        remark: form.remark || undefined
      });
      EleMessage.success({ message: '已确认回单', plain: true });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '确认回单失败',
        plain: true
      });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .photo-uploader {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
  }

  .photo-item {
    position: relative;
    width: 88px;
    height: 88px;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid var(--el-border-color);

    :deep(.el-image) {
      width: 100%;
      height: 100%;
    }
  }

  .photo-remove {
    position: absolute;
    top: 2px;
    right: 2px;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    padding: 2px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 12px;
  }

  .photo-add {
    width: 88px;
    height: 88px;
    border: 1px dashed var(--el-border-color);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    gap: 4px;

    &:hover {
      border-color: var(--el-color-primary);
      color: var(--el-color-primary);
    }

    &__hint {
      font-size: 12px;
    }
  }

  .mt-4 {
    margin-top: 4px;
  }
</style>
