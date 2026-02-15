<template>
  <ele-card header="基础用法">
    <ele-viewer
      ref="viewerRef"
      src="https://cdn.eleadmin.com/20200610/pECHMJU.webp"
      :markers="markers"
      :rotate-step="45"
      :zoom-min="10"
      :image-style="{ filter: 'grayscale(60%) contrast(120%) saturate(200%)' }"
      style="height: 560px; max-width: 900px"
    >
      <template #markerItem="{ item }">
        <div v-if="item.key === 3" class="marker-watermark">
          <div>{{ item.text }}</div>
        </div>
        <div v-else class="marker-item">
          <div>{{ item.text }}</div>
        </div>
      </template>
    </ele-viewer>
    <div style="margin-top: 12px">
      可缩放、拖动、旋转等，可添加跟随缩放旋转和不跟随缩放旋转的标记点
    </div>
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

  /** 标记点 */
  const markers = ref([
    { key: 1, x: 455, y: 328, fixed: true, text: '找同款吊灯' },
    { key: 2, x: 142, y: 808, fixed: true, text: '找同款挂画' },
    { key: 3, x: 908, y: 1360, text: '我会跟随缩放' }
  ]);

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
  .marker-item {
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
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #ffffff;
      box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.4);
    }

    & > div {
      height: 24px;
      line-height: 24px;
      border-radius: 12px;
      padding: 0 8px;
      color: #ffffff;
      font-size: 12px;
      transition: background-color 0.2s;
      background: rgba(0, 0, 0, 0.5);
      position: absolute;
      left: 12px;
      top: -12px;
      white-space: nowrap;
      pointer-events: auto;
      cursor: pointer;

      &:hover {
        background: rgba(0, 0, 0, 0.8);
      }
    }
  }

  .marker-watermark {
    width: 0;
    height: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;

    & > div {
      flex-shrink: 0;
      height: 60px;
      line-height: 60px;
      border-radius: 10px;
      padding: 0 20px;
      color: #ffffff;
      font-size: 32px;
      background: #ff2442;
      white-space: nowrap;
      transition: background-color 0.2s;
      pointer-events: auto;
      cursor: pointer;

      &:hover {
        background: #980015;
      }
    }
  }
</style>
