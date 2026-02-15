<template>
  <ele-page :multi-card="true">
    <ele-card header="基础用法">
      <el-form label-width="88px" style="max-width: 420px" @submit.prevent="">
        <div style="text-align: center; margin-bottom: 8px">
          <ele-qr-code
            :value="text"
            :size="size"
            :level="level"
            :margin="margin"
            :image-settings="image"
            :tag="tag"
          />
        </div>
        <el-form-item label="渲染方式">
          <el-radio-group v-model="tag">
            <el-radio value="img" label="img" />
            <el-radio value="canvas" label="canvas" />
            <el-radio value="svg" label="svg" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="二维码内容">
          <el-input v-model="text" :maxlength="150" />
        </el-form-item>
        <el-form-item label="容错等级">
          <el-select
            v-model="level"
            class="ele-fluid"
            :popper-options="{ strategy: 'fixed' }"
          >
            <el-option value="L" label="L" />
            <el-option value="M" label="M" />
            <el-option value="Q" label="Q" />
            <el-option value="H" label="H" />
          </el-select>
        </el-form-item>
        <el-form-item label="尺寸">
          <el-slider v-model="size" :min="80" :max="280" :step="40" />
        </el-form-item>
        <el-form-item label="间距">
          <el-slider v-model="margin" :min="0" :max="20" />
        </el-form-item>
        <el-form-item label="自定义图片">
          <el-switch
            v-model="showImage"
            size="small"
            @change="handleShowImageChange"
          />
        </el-form-item>
        <template v-if="showImage">
          <el-form-item label="图片地址">
            <el-input v-model="image.src" :maxlength="400" />
          </el-form-item>
          <el-form-item label="图片宽高">
            <div style="display: flex; flex-wrap: wrap">
              <div style="width: 120px; margin-right: 16px">
                <el-input-number
                  v-model="image.width"
                  size="small"
                  :min="0"
                  :max="size"
                />
              </div>
              <div style="width: 120px">
                <el-input-number
                  v-model="image.height"
                  size="small"
                  :min="0"
                  :max="size"
                />
              </div>
            </div>
          </el-form-item>
          <el-form-item label="位置居中">
            <div>
              <el-switch
                v-model="center"
                size="small"
                @change="handleCenterChange"
              />
              <div v-if="!center" style="display: flex; flex-wrap: wrap">
                <div style="display: flex; align-items: center">
                  <div style="padding: 0 12px">x</div>
                  <div style="width: 120px">
                    <el-input-number
                      v-model="image.x"
                      size="small"
                      :min="0"
                      :max="size"
                    />
                  </div>
                </div>
                <div style="display: flex; align-items: center">
                  <div style="padding: 0 12px">y</div>
                  <div style="width: 120px">
                    <el-input-number
                      v-model="image.y"
                      size="small"
                      :min="0"
                      :max="size"
                    />
                  </div>
                </div>
              </div>
            </div>
          </el-form-item>
          <el-form-item label="背景擦除">
            <el-switch v-model="image.excavate" size="small" />
          </el-form-item>
        </template>
      </el-form>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type {
    Level,
    ImageSettings,
    QrCodeTag
  } from 'ele-admin-plus/es/ele-qr-code/types';

  defineOptions({ name: 'ExtensionQrCode' });

  const IMAGE_SRC = 'https://cdn.eleadmin.com/20200610/logo-radius.png';

  /** 二维码内容 */
  const text = ref('https://eleadmin.com');

  /** 渲染方式 */
  const tag = ref<QrCodeTag>('img');

  /** 容错级别 */
  const level = ref<Level>('L');

  /** 尺寸 */
  const size = ref(120);

  /** 内间距 */
  const margin = ref(0);

  /** 是否增加自定义图标 */
  const showImage = ref(true);

  /** 自定义图标 */
  const image = reactive<ImageSettings>({
    src: IMAGE_SRC,
    width: 28,
    height: 28,
    x: void 0,
    y: void 0,
    excavate: false
  });

  /** 自定义图标是否居中 */
  const center = ref(true);

  const handleShowImageChange = (checked: boolean) => {
    if (checked) {
      image.src = IMAGE_SRC;
    } else {
      image.src = void 0;
    }
  };

  /** 自定义图标居中改变事件 */
  const handleCenterChange = (checked: boolean) => {
    if (checked) {
      image.x = void 0;
      image.y = void 0;
    } else {
      image.x = 0;
      image.y = 0;
    }
  };
</script>
