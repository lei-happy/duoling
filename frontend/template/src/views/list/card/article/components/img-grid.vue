<template>
  <div class="demo-img-grid">
    <el-image
      v-for="(item, index) in images"
      :key="item"
      fit="cover"
      :src="item"
      :style="{
        width: '100%',
        height: '100%',
        cursor: 'zoom-in'
      }"
      @click="openPreview(index)"
    />
  </div>
</template>

<script lang="ts" setup>
  const props = defineProps<{
    images: string[];
  }>();

  const emit = defineEmits<{
    (e: 'preview', images: string[], index: number): void;
  }>();

  const openPreview = (index: number) => {
    emit('preview', props.images, index);
  };
</script>

<style lang="scss" scoped>
  .demo-img-grid {
    display: grid;
    grid-gap: 3px 3px;
    grid-template-columns: repeat(3, 1fr);
    height: 100%;
    padding: 4px;
    box-sizing: border-box;
    border-radius: 4px;
    border: 1px solid var(--el-border-color-light);

    :deep(.el-image) {
      transition: all 0.2s;

      &:hover {
        filter: brightness(0.8);
      }
    }
  }
</style>
