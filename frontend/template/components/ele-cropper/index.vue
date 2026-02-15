<!-- 图片裁剪 -->
<template>
  <div class="ele-cropper" :class="{ 'is-responsive': isResponsive }">
    <div class="ele-cropper-main">
      <!-- 裁剪区域 -->
      <div class="ele-cropper-image" :style="{ height }">
        <img ref="imageRef" :src="src" :style="{ display: 'none' }" />
      </div>
      <!-- 预览区域 -->
      <CropperPreview
        v-if="preview"
        ref="previewRef"
        :previewWidth="previewWidth"
        :aspectRatio="options ? options.aspectRatio : void 0"
      />
    </div>
    <!-- 操作按钮 -->
    <CropperTools
      :tools="tools"
      :accept="accept"
      :locale="locale"
      :tooltip="tooltip"
      :tooltipProps="tooltipProps"
      :beforeUploadClick="beforeUploadClick"
      @zoomIn="handleZoomIn"
      @zoomOut="handleZoomOut"
      @moveLeft="handleMoveLeft"
      @moveRight="handleMoveRight"
      @moveUp="handleMoveUp"
      @moveDown="handleMoveDown"
      @rotateLeft="handleRotateLeft"
      @rotateRight="handleRotateRight"
      @flipX="handleFlipX"
      @flipY="handleFlipY"
      @reset="handleReset"
      @upload="handleUpload"
      @ok="handleOk"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
  import Cropper from 'cropperjs';
  import type { EleCropperPreviewInstance } from '../ele-app/plusx';
  import { useResponsive } from '../ele-pro-layout/util';
  import CropperPreview from './components/cropper-preview.vue';
  import CropperTools from './components/cropper-tools.vue';
  import type { CurrentState, CropperOptions } from './types';
  import { cropperProps, cropperEmits } from './props';

  defineOptions({ name: 'EleCropper' });

  const props = defineProps(cropperProps);

  const emit = defineEmits(cropperEmits);

  /** 是否开启布局响应 */
  const isResponsive = useResponsive(props);

  /** 图片节点 */
  const imageRef = ref<HTMLImageElement | null>(null);

  /** 预览组件 */
  const previewRef = ref<EleCropperPreviewInstance>(null);

  /** 当前实例数据 */
  const state: CurrentState = {
    instance: null,
    imageType: props.imageType,
    scaleXValue: -1,
    scaleYValue: -1
  };

  /** 渲染 */
  const render = () => {
    destroy();
    const options: CropperOptions = { ...props.options };
    if (props.preview && previewRef.value) {
      options.preview = previewRef.value.getPreviews();
    }
    if (imageRef.value) {
      state.instance = new Cropper(imageRef.value, options);
    }
  };

  /** 销毁 */
  const destroy = () => {
    state.instance && state.instance.destroy();
    state.instance = null;
  };

  /** 放大 */
  const handleZoomIn = () => {
    state.instance && state.instance.zoom(0.1);
  };

  /** 缩小 */
  const handleZoomOut = () => {
    state.instance && state.instance.zoom(-0.1);
  };

  /** 左移 */
  const handleMoveLeft = () => {
    state.instance && state.instance.move(-10, 0);
  };

  /** 右移 */
  const handleMoveRight = () => {
    state.instance && state.instance.move(10, 0);
  };

  /** 上移 */
  const handleMoveUp = () => {
    state.instance && state.instance.move(0, -10);
  };

  /** 下移 */
  const handleMoveDown = () => {
    state.instance && state.instance.move(0, 10);
  };

  /** 左旋 */
  const handleRotateLeft = () => {
    state.instance && state.instance.rotate(-45);
  };

  /** 右旋 */
  const handleRotateRight = () => {
    state.instance && state.instance.rotate(45);
  };

  /** 左右镜像 */
  const handleFlipX = () => {
    state.instance && state.instance.scaleX(state.scaleXValue);
    state.scaleXValue = -state.scaleXValue;
  };

  /** 上下镜像 */
  const handleFlipY = () => {
    state.instance && state.instance.scaleY(state.scaleYValue);
    state.scaleYValue = -state.scaleYValue;
  };

  /** 重置 */
  const handleReset = () => {
    state.instance && state.instance.reset();
  };

  /** 替换图片 */
  const handleUpload = ({ data, type }: { data: string; type: string }) => {
    state.imageType = type;
    if (state.instance) {
      state.instance.replace(data);
    } else {
      const elem = imageRef.value;
      if (elem) {
        elem.src = data;
        elem.style.display = 'block';
      }
      render();
    }
  };

  /** 裁剪 */
  const handleOk = () => {
    if (!state.instance) {
      emit('done');
      return;
    }
    const opt = props.croppedOptions ? props.croppedOptions : void 0;
    const result = state.instance.getCroppedCanvas(opt);
    if (!result) {
      emit('done');
      return;
    }
    if (props.toBlob) {
      result.toBlob((blob) => {
        emit('done', blob);
      }, state.imageType);
      return;
    }
    emit('done', result.toDataURL(state.imageType));
  };

  watch(
    () => props.src,
    (src) => {
      if (src) {
        if (state.instance) {
          state.instance.replace(src);
        } else {
          nextTick(() => {
            render();
          });
        }
      } else {
        destroy();
      }
    }
  );

  watch(
    () => props.imageType,
    (value) => {
      if (value) {
        state.imageType = value;
      }
    }
  );

  onMounted(() => {
    props.src && render();
  });

  onBeforeUnmount(() => {
    destroy();
  });
</script>
