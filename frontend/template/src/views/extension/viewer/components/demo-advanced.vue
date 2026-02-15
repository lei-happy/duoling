<template>
  <ele-card header="可自定义任意内容">
    <ele-viewer ref="viewerRef" style="height: 560px; max-width: 900px">
      <demo-top-layout
        :style="{
          width: '800px',
          background: 'var(--ele-layout-bg)',
          pointerEvents: 'auto'
        }"
      />
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
  import DemoTopLayout from '../../layout/components/demo-top-layout.vue';

  /** 查看器组件 */
  const viewerRef = ref<any>(null);

  /** 调用查看器组件方法 */
  const handleCallViewer = (methodName: string) => {
    if (viewerRef.value) {
      viewerRef.value[methodName]();
    }
  };
</script>
