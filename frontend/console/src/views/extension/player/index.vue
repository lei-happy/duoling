<template>
  <ele-page>
    <el-row :gutter="16">
      <el-col :md="12" :sm="24" :xs="24">
        <demo-basic />
      </el-col>
      <el-col :md="12" :sm="24" :xs="24">
        <demo-danmu />
      </el-col>
    </el-row>
    <el-row :gutter="16" class="demo-player-music-wrap">
      <el-col :md="12" :sm="24" :xs="24">
        <demo-live />
      </el-col>
      <el-col :md="12" :sm="24" :xs="24">
        <demo-music />
      </el-col>
    </el-row>
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoBasic from './components/demo-basic.vue';
  import DemoDanmu from './components/demo-danmu.vue';
  import DemoLive from './components/demo-live.vue';
  import DemoMusic from './components/demo-music.vue';

  defineOptions({ name: 'ExtensionPlayer' });
</script>

<style lang="scss" scoped>
  @media screen and (min-width: 992px) {
    .demo-player-music-wrap :deep(.demo-music-wrap) {
      height: 0px;
      padding-top: calc(56.25% + 32px + 16px);
      position: relative;

      .music-wrapper {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
      }

      .music-body {
        flex: 1;
        height: auto;
        overflow: hidden;
      }
    }
  }
</style>
