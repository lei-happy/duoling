<template>
  <ele-card header="用于景区地图">
    <ele-viewer
      ref="viewerRef"
      src="https://cdn.chimelong.com/upload/039efd65c3282816/408cbfefc64b04c4.jpg"
      :markers="[{ key: 1, x: 604, y: 840, fixed: true, text: '您的位置' }]"
      :rotate-step="45"
      :image-style="{ filter: 'grayscale(60%) contrast(120%) saturate(200%)' }"
      style="height: 560px; max-width: 900px"
    >
      <template #markerItem="{ item }">
        <div class="zoo-map-location">
          <div>{{ item.text }}</div>
        </div>
      </template>
    </ele-viewer>
    <div style="margin-top: 12px">
      <el-button class="ele-btn-icon" @click="handleCallViewer('zoomIn')">
        放大
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('zoomOut')">
        缩小
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('rotateLeft')">
        向左旋转
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('rotateRight')">
        向右旋转
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('autoIntoView')">
        自适应缩放
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('reset')">
        重置
      </el-button>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';

  /** 查看器组件 */
  const viewerRef = ref<any>(null);

  /** 调用查看器组件方法 */
  const handleCallViewer = (methodName: string) => {
    if (viewerRef.value) {
      viewerRef.value[methodName]();
    }
  };
</script>

<style lang="scss" scoped>
  .zoo-map-location {
    width: 0;
    height: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;

    &::before {
      content: '';
      flex-shrink: 0;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ff2024;
      box-shadow: 0 0 0 4px rgba(255, 122, 125, 0.6);
    }

    &::after {
      content: '';
      position: absolute;
      top: -14px;
      left: -6px;
      border: 6px solid transparent;
      border-top-color: #ff2024;
    }

    & > div {
      color: #fff;
      font-size: 16px;
      padding: 4px 12px;
      background: #ff2024;
      border-radius: 6px;
      white-space: nowrap;
      position: absolute;
      bottom: 14px;
    }
  }
</style>
