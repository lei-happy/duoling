<template>
  <ele-modal
    form
    :width="680"
    :title="isUpdate ? '修改车系' : '添加车系'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      label-position="right"
      class="series-edit-form"
      @submit.prevent=""
    >
      <el-form-item label="所属品牌">
        <el-input :model-value="props.brandName || '—'" disabled />
      </el-form-item>
      <el-form-item label="车系名称" prop="seriesName">
        <el-input
          v-model.trim="form.seriesName"
          placeholder="必填"
          maxlength="100"
          clearable
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="价格范围" prop="price">
        <el-input
          v-model.trim="form.price"
          placeholder="选填"
          maxlength="255"
          clearable
        />
      </el-form-item>
      <el-form-item label="能源类型" prop="energyType">
        <el-input
          v-model.trim="form.energyType"
          placeholder="如汽油、纯电动等"
          maxlength="50"
          clearable
        />
      </el-form-item>
      <el-form-item label="车系图片" prop="seriesImage">
        <div class="series-img-block">
          <el-upload
            class="series-img-uploader"
            accept="image/png,image/webp,image/gif"
            :show-file-list="false"
            :before-upload="beforeSeriesImageUpload"
          >
            <template v-if="form.seriesImage">
              <img
                class="series-img-preview"
                :src="seriesImagePreviewSrc"
                alt=""
              />
            </template>
            <el-icon v-else class="series-img-uploader-icon">
              <PlusOutlined />
            </el-icon>
          </el-upload>
          <div class="series-img-hint">
            规格：<strong>480×320 像素</strong
            >，<strong>透明背景</strong>；请使用 PNG / WebP / GIF，最大
            5MB。存站点相对路径。
          </div>
          <el-button
            v-if="form.seriesImage"
            type="danger"
            link
            @click="form.seriesImage = ''"
          >
            移除图片
          </el-button>
        </div>
      </el-form-item>

      <el-divider content-position="left"
        >尺寸与质量（与库表一致，选填）</el-divider
      >

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="车长(mm)" prop="lengthMm">
            <el-input-number
              v-model="form.lengthMm"
              :min="0"
              :max="999999"
              :controls="true"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车宽(mm)" prop="widthMm">
            <el-input-number
              v-model="form.widthMm"
              :min="0"
              :max="999999"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="车高(mm)" prop="heightMm">
            <el-input-number
              v-model="form.heightMm"
              :min="0"
              :max="999999"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="轴距(mm)" prop="wheelbaseMm">
            <el-input-number
              v-model="form.wheelbaseMm"
              :min="0"
              :max="999999"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="前轮距(mm)" prop="frontTrackMm">
            <el-input-number
              v-model="form.frontTrackMm"
              :min="0"
              :max="999999"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="后轮距(mm)" prop="rearTrackMm">
            <el-input-number
              v-model="form.rearTrackMm"
              :min="0"
              :max="999999"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="接近角(°)" prop="approachAngle">
            <el-input-number
              v-model="form.approachAngle"
              :min="0"
              :max="90"
              :precision="2"
              :step="0.1"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="离去角(°)" prop="departureAngle">
            <el-input-number
              v-model="form.departureAngle"
              :min="0"
              :max="90"
              :precision="2"
              :step="0.1"
              controls-position="right"
              class="series-num-full"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="整备质量(kg)" prop="curbWeightKg">
        <el-input-number
          v-model="form.curbWeightKg"
          :min="0"
          :max="999999"
          controls-position="right"
          class="series-num-full"
          style="max-width: 100%"
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
  import {
    addVehicleSeries,
    updateVehicleSeries
  } from '@/api/basic-data/vehicle-series';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import { uploadFile } from '@/api/system/file';
  import { PlusOutlined } from '@/components/icons';
  import {
    readImageFileDimensions,
    imageFileHasTransparency
  } from '@/utils/upload-image-spec';

  const SERIES_IMAGE_W = 480;
  const SERIES_IMAGE_H = 320;

  const props = defineProps<{
    brandId: number;
    brandName?: string;
    data?: VehicleSeries | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, _resetFields, assignFields] = useFormData({
    seriesId: void 0 as number | undefined,
    seriesName: '',
    price: '',
    energyType: '',
    seriesImage: '',
    lengthMm: undefined as number | undefined,
    widthMm: undefined as number | undefined,
    heightMm: undefined as number | undefined,
    wheelbaseMm: undefined as number | undefined,
    frontTrackMm: undefined as number | undefined,
    rearTrackMm: undefined as number | undefined,
    approachAngle: undefined as number | undefined,
    departureAngle: undefined as number | undefined,
    curbWeightKg: undefined as number | undefined
  });

  const seriesImagePreviewSrc = computed(() => {
    const p = form.seriesImage?.trim();
    if (!p) return '';
    if (p.startsWith('http://') || p.startsWith('https://')) return p;
    return p.startsWith('/') ? p : `/${p}`;
  });

  const rules: FormRules = {
    seriesName: [
      {
        required: true,
        message: '请输入车系名称',
        type: 'string',
        trigger: 'blur'
      }
    ]
  };

  const beforeSeriesImageUpload = async (file: File) => {
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
    if (file.size > 5 * 1024 * 1024) {
      EleMessage.error({ message: '图片不能超过 5MB', plain: true });
      return false;
    }
    try {
      const { width, height } = await readImageFileDimensions(file);
      if (width !== SERIES_IMAGE_W || height !== SERIES_IMAGE_H) {
        EleMessage.error({
          message: `车系图尺寸须为 ${SERIES_IMAGE_W}×${SERIES_IMAGE_H} 像素（当前 ${width}×${height}）`,
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
    uploadFile(file, undefined, file.name, 'car_series')
      .then((res) => {
        up.close();
        if (res.url) {
          form.seriesImage = res.url;
          EleMessage.success({ message: '上传成功', plain: true });
        }
      })
      .catch((e) => {
        up.close();
        EleMessage.error({ message: e.message, plain: true });
      });
    return false;
  };

  const handleCancel = () => {
    closeModal();
  };

  const buildPayload = () => ({
    seriesName: form.seriesName,
    price: form.price || undefined,
    energyType: form.energyType || undefined,
    seriesImage: form.seriesImage || undefined,
    lengthMm: form.lengthMm,
    widthMm: form.widthMm,
    heightMm: form.heightMm,
    wheelbaseMm: form.wheelbaseMm,
    frontTrackMm: form.frontTrackMm,
    rearTrackMm: form.rearTrackMm,
    approachAngle: form.approachAngle,
    departureAngle: form.departureAngle,
    curbWeightKg: form.curbWeightKg
  });

  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;

      const promise = isUpdate.value
        ? updateVehicleSeries(form.seriesId!, buildPayload())
        : addVehicleSeries({
            brandId: props.brandId,
            ...buildPayload()
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
      seriesId: props.data.seriesId,
      seriesName: props.data.seriesName ?? '',
      price: props.data.price ?? '',
      energyType: props.data.energyType ?? '',
      seriesImage: props.data.seriesImage ?? '',
      lengthMm: props.data.lengthMm ?? undefined,
      widthMm: props.data.widthMm ?? undefined,
      heightMm: props.data.heightMm ?? undefined,
      wheelbaseMm: props.data.wheelbaseMm ?? undefined,
      frontTrackMm: props.data.frontTrackMm ?? undefined,
      rearTrackMm: props.data.rearTrackMm ?? undefined,
      approachAngle: props.data.approachAngle ?? undefined,
      departureAngle: props.data.departureAngle ?? undefined,
      curbWeightKg: props.data.curbWeightKg ?? undefined
    });
    isUpdate.value = true;
  }
</script>

<style scoped>
  .series-edit-form :deep(.el-form-item__content) {
    align-items: flex-start;
  }
  .series-num-full {
    width: 100%;
  }
  .series-img-block {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }
  .series-img-uploader :deep(.el-upload) {
    border: 1px dashed var(--el-border-color);
    border-radius: 8px;
    cursor: pointer;
    width: 240px;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--el-transition-duration-fast);
  }
  .series-img-uploader :deep(.el-upload:hover) {
    border-color: var(--el-color-primary);
  }
  .series-img-preview {
    width: 240px;
    height: 160px;
    object-fit: contain;
    background:
      linear-gradient(45deg, #e8e8e8 25%, transparent 25%),
      linear-gradient(-45deg, #e8e8e8 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #e8e8e8 75%),
      linear-gradient(-45deg, transparent 75%, #e8e8e8 75%);
    background-size: 12px 12px;
    background-position:
      0 0,
      0 6px,
      6px -6px,
      -6px 0;
    background-color: #fff;
  }
  .series-img-uploader-icon {
    font-size: 28px;
    color: var(--el-text-color-secondary);
  }
  .series-img-hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
    max-width: 400px;
  }
</style>
