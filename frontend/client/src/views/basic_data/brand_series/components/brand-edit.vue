<template>
  <ele-modal
    form
    :width="520"
    :title="isUpdate ? '修改品牌' : '添加品牌'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
      class="brand-edit-form"
      @submit.prevent=""
    >
      <el-form-item label="中文名称" prop="brandNameCn">
        <el-input
          v-model.trim="form.brandNameCn"
          placeholder="请输入品牌中文名称"
          maxlength="100"
          clearable
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="品牌 Logo" prop="brandLogo">
        <div class="logo-block">
          <el-upload
            class="brand-logo-uploader"
            accept="image/png,image/webp,image/gif"
            :show-file-list="false"
            :before-upload="beforeLogoUpload"
          >
            <template v-if="form.brandLogo">
              <img class="brand-logo-preview" :src="logoPreviewSrc" alt="" />
            </template>
            <el-icon v-else class="brand-logo-uploader-icon">
              <PlusOutlined />
            </el-icon>
          </el-upload>
          <div class="logo-hint">
            规格：<strong>56×56 像素</strong>，<strong>透明背景</strong>；请使用 PNG / WebP /
            GIF，最大 5MB。将保存为站点相对路径。
          </div>
          <el-button
            v-if="form.brandLogo"
            type="danger"
            link
            class="logo-remove"
            @click="clearLogo"
          >
            移除 Logo
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="品牌国别" prop="brandCountry">
        <el-input
          v-model.trim="form.brandCountry"
          placeholder="选填"
          maxlength="50"
          clearable
        />
      </el-form-item>
      <el-form-item label="品牌介绍" prop="brandIntroduce">
        <el-input
          v-model="form.brandIntroduce"
          type="textarea"
          :rows="5"
          maxlength="2000"
          show-word-limit
          placeholder="选填"
          class="brand-intro-textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => handleSave() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import { addVehicleBrand, updateVehicleBrand } from '@/api/basic-data/vehicle-brand';
  import type { VehicleBrand } from '@/api/basic-data/vehicle-brand/model';
  import { uploadFile } from '@/api/system/file';
  import { PlusOutlined } from '@/components/icons';
  import {
    readImageFileDimensions,
    imageFileHasTransparency
  } from '@/utils/upload-image-spec';

  const BRAND_LOGO_SIZE = 56;

  const props = defineProps<{
    data?: VehicleBrand | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData({
    brandId: void 0 as number | undefined,
    brandNameCn: '',
    brandLogo: '',
    brandCountry: '',
    brandIntroduce: ''
  });

  const logoPreviewSrc = computed(() => {
    const p = form.brandLogo?.trim();
    if (!p) return '';
    if (p.startsWith('http://') || p.startsWith('https://')) {
      return p;
    }
    return p.startsWith('/') ? p : `/${p}`;
  });

  const rules: FormRules = {
    brandNameCn: [
      {
        required: true,
        message: '请输入品牌中文名称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  };

  const beforeLogoUpload = async (file: File) => {
    const allowed =
      file.type === 'image/png' ||
      file.type === 'image/webp' ||
      file.type === 'image/gif';
    if (!allowed) {
      EleMessage.error({
        message: '请上传 PNG、WebP 或 GIF（需支持透明背景）',
        plain: true
      });
      return false;
    }
    const maxMb = 5;
    if (file.size > maxMb * 1024 * 1024) {
      EleMessage.error({ message: `图片不能超过 ${maxMb}MB`, plain: true });
      return false;
    }
    try {
      const { width, height } = await readImageFileDimensions(file);
      if (width !== BRAND_LOGO_SIZE || height !== BRAND_LOGO_SIZE) {
        EleMessage.error({
          message: `Logo 尺寸须为 ${BRAND_LOGO_SIZE}×${BRAND_LOGO_SIZE} 像素（当前 ${width}×${height}）`,
          plain: true
        });
        return false;
      }
    } catch {
      EleMessage.error({ message: '无法读取图片尺寸', plain: true });
      return false;
    }
    const transparent = await imageFileHasTransparency(file);
    if (transparent === false) {
      EleMessage.error({
        message: '请使用带透明背景的 PNG、WebP 或 GIF',
        plain: true
      });
      return false;
    }
    const up = EleMessage.loading({
      message: '上传中..',
      plain: true,
      mask: true
    });
    uploadFile(file, undefined, file.name, 'brand_logo')
      .then((res) => {
        up.close();
        if (res.url) {
          form.brandLogo = res.url;
          EleMessage.success({ message: '上传成功', plain: true });
        }
      })
      .catch((e) => {
        up.close();
        EleMessage.error({ message: e.message, plain: true });
      });
    return false;
  };

  const clearLogo = () => {
    form.brandLogo = '';
  };

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;

      const promise = isUpdate.value
        ? updateVehicleBrand(form.brandId!, {
            brandNameCn: form.brandNameCn,
            brandLogo: form.brandLogo || undefined,
            brandCountry: form.brandCountry || undefined,
            brandIntroduce: form.brandIntroduce || undefined
          })
        : addVehicleBrand({
            brandNameCn: form.brandNameCn,
            brandLogo: form.brandLogo || undefined,
            brandCountry: form.brandCountry || undefined,
            brandIntroduce: form.brandIntroduce || undefined
          });

      promise
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg, plain: true });
          emit('done');
          handleCancel();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  if (props.data) {
    assignFields({
      brandId: props.data.brandId,
      brandNameCn: props.data.brandNameCn ?? '',
      brandLogo: props.data.brandLogo ?? '',
      brandCountry: props.data.brandCountry ?? '',
      brandIntroduce: props.data.brandIntroduce ?? ''
    });
    isUpdate.value = true;
  }
</script>

<style scoped>
  .brand-edit-form :deep(.el-form-item__content) {
    align-items: flex-start;
  }
  .logo-block {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }
  .brand-logo-uploader :deep(.el-upload) {
    border: 1px dashed var(--el-border-color);
    border-radius: 8px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--el-transition-duration-fast);
  }
  .brand-logo-uploader :deep(.el-upload:hover) {
    border-color: var(--el-color-primary);
  }
  .brand-logo-preview {
    width: 56px;
    height: 56px;
    object-fit: contain;
    display: block;
    background: linear-gradient(45deg, #e8e8e8 25%, transparent 25%),
      linear-gradient(-45deg, #e8e8e8 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #e8e8e8 75%),
      linear-gradient(-45deg, transparent 75%, #e8e8e8 75%);
    background-size: 8px 8px;
    background-position: 0 0, 0 4px, 4px -4px, -4px 0;
    background-color: #fff;
  }
  .brand-logo-uploader-icon {
    font-size: 22px;
    color: var(--el-text-color-secondary);
  }
  .logo-hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
    max-width: 360px;
  }
  .logo-remove {
    padding: 0;
  }
  .brand-intro-textarea {
    width: 100%;
  }
</style>
