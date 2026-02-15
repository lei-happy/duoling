<template>
  <ele-card header="加载提示">
    <option-item label="状态" :responsive="false">
      <el-switch v-model="loading" size="small" />
    </option-item>
    <option-item label="尺寸" :responsive="false" style="margin: 6px 0 0 0">
      <el-radio-group
        v-model="loadingSize"
        :disabled="loadingType === 'circle'"
      >
        <el-radio value="small" label="小型" />
        <el-radio value="default" label="默认" />
        <el-radio value="large" label="大型" />
      </el-radio-group>
    </option-item>
    <option-item label="文本" :responsive="false" style="margin: 2px 0 0 0">
      <el-radio-group v-model="loadingText" @change="handleLoadingTextChange">
        <el-radio value="" label="不显示" />
        <el-radio value="Loading..." label="显示" />
      </el-radio-group>
    </option-item>
    <option-item label="类型" :responsive="false" style="margin: 2px 0 0 0">
      <el-radio-group v-model="loadingType">
        <el-radio value="dot" label="圆点" />
        <el-radio value="circle" label="圆圈" />
      </el-radio-group>
    </option-item>
    <ele-loading
      :key="loadingKey"
      :loading="loading"
      :size="loadingSize"
      :type="loadingType"
      :text="loadingText"
      :blur="true"
      style="padding: 20px 16px; max-width: 520px; position: relative"
    >
      <div style="font-size: 17px; max-height: 100%">Alert message title</div>
      <div style="word-break: break-all; margin-top: 4px; max-height: 100%">
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
        <span>Further details about the context of this alert.</span>
      </div>
    </ele-loading>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type {
    LoadingSize,
    LoadingType
  } from 'ele-admin-plus/es/ele-loading/types';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  /** 加载框显示状态 */
  const loading = ref(false);

  /** 加载框尺寸 */
  const loadingSize = ref<LoadingSize>('default');

  /** 加载框类型 */
  const loadingType = ref<LoadingType>('dot');

  /** 加载框显示文本 */
  const loadingText = ref('');

  /** 用于重新渲染加载框 */
  const loadingKey = ref(0);

  /** 加载框类型选择改变事件 */
  const handleLoadingTextChange = () => {
    if (loadingType.value === 'circle' && loading.value) {
      loadingKey.value++;
    }
  };
</script>
