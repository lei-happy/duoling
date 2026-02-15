<template>
  <ele-card
    header="基础用法"
    :body-style="{ overflow: 'hidden', padding: '8px 13px 13px 13px' }"
  >
    <option-item label="显示折叠按钮" :responsive="false" style="margin: 0">
      <el-radio-group v-model="allowCollapse">
        <el-radio :value="true" label="是" />
        <el-radio :value="false" label="否" />
        <el-radio value="both" label="双向折叠" />
      </el-radio-group>
    </option-item>
    <option-item label="支持自由拉伸" :responsive="false" style="margin: 0">
      <el-radio-group v-model="resizable">
        <el-radio :value="true" label="是" />
        <el-radio :value="false" label="否" />
      </el-radio-group>
    </option-item>
    <option-item label="上下布局模式" :responsive="false" style="margin: 0">
      <el-radio-group v-model="vertical">
        <el-radio :value="true" label="是" />
        <el-radio :value="false" label="否" />
      </el-radio-group>
    </option-item>
    <option-item label="反转布局方向" :responsive="false" style="margin: 0">
      <el-radio-group v-model="reverse">
        <el-radio :value="true" label="是" />
        <el-radio :value="false" label="否" />
      </el-radio-group>
    </option-item>
    <ele-split-panel
      :space="0"
      :size="160"
      :collapse-btn-offset="2"
      :allow-collapse="allowCollapse"
      :resizable="resizable"
      :vertical="vertical"
      :reverse="reverse"
      :percentage="true"
      :custom-style="{ background: 'rgba(185,182,229,.4)', border: 'none' }"
      :body-style="{ background: 'rgba(125,226,252,.4)' }"
      style="height: 360px; margin-top: 12px; overflow: hidden"
    >
      <div>边栏</div>
      <template #body>
        <div>内容</div>
      </template>
    </ele-split-panel>
  </ele-card>
  <ele-card header="组合使用" :body-style="{ padding: '13px' }">
    <div style="margin: 0 0 8px 0">先左右再上下</div>
    <ele-split-panel
      :space="0"
      :min-size="40"
      :max-size="-40"
      :resizable="true"
      :percentage="true"
      :custom-style="{ background: 'rgba(185,182,229,.4)', border: 'none' }"
      :body-style="{ overflow: 'hidden' }"
      :responsive="false"
      style="height: 400px"
    >
      <div>边栏</div>
      <template #body>
        <ele-split-panel
          :space="0"
          :min-size="40"
          :max-size="-40"
          :vertical="true"
          :resizable="true"
          :percentage="true"
          :custom-style="{ background: 'rgba(171,199,255,.5)', border: 'none' }"
          :body-style="{ background: 'rgba(125,226,252,.4)' }"
          :responsive="false"
          style="height: 100%"
        >
          <div>内容一</div>
          <template #body>
            <div>内容二</div>
          </template>
        </ele-split-panel>
      </template>
    </ele-split-panel>
    <div style="margin: 16px 0 8px 0">先上下再左右</div>
    <ele-split-panel
      :space="0"
      :size="80"
      :min-size="40"
      :max-size="-40"
      :vertical="true"
      :resizable="true"
      :percentage="true"
      :custom-style="{ background: 'rgba(185,182,229,.4)', border: 'none' }"
      :body-style="{ overflow: 'hidden' }"
      :responsive="false"
      style="height: 400px"
    >
      <div>顶栏</div>
      <template #body>
        <ele-split-panel
          :space="0"
          :min-size="40"
          :max-size="-40"
          :resizable="true"
          :percentage="true"
          :custom-style="{ background: 'rgba(171,199,255,.5)', border: 'none' }"
          :body-style="{ background: 'rgba(125,226,252,.4)' }"
          :responsive="false"
          style="height: 100%"
        >
          <div>边栏</div>
          <template #body>
            <div>内容</div>
          </template>
        </ele-split-panel>
      </template>
    </ele-split-panel>
  </ele-card>
  <ele-card
    header="可随意自由组合"
    :body-style="{ overflow: 'hidden', padding: '13px' }"
  >
    <ele-split-panel
      :space="0"
      :size="80"
      :vertical="true"
      :resizable="true"
      :percentage="true"
      :allow-collapse="true"
      :collapse-btn-offset="2"
      :custom-style="{ background: 'rgba(185,182,229,.4)', border: 'none' }"
      :body-style="{ overflow: 'hidden' }"
      :responsive="false"
      style="height: 400px"
    >
      <div>顶栏</div>
      <template #body>
        <ele-split-panel
          :space="0"
          size="16%"
          :resizable="true"
          :percentage="true"
          :allow-collapse="true"
          :collapse-btn-offset="2"
          :custom-style="{ background: 'rgba(171,199,255,.5)', border: 'none' }"
          :body-style="{ overflow: 'hidden' }"
          :responsive="false"
          style="height: 100%"
        >
          <div>左边栏</div>
          <template #body>
            <ele-split-panel
              :space="0"
              size="20%"
              :resizable="true"
              :percentage="true"
              :allow-collapse="true"
              :collapse-btn-offset="2"
              :reverse="true"
              :custom-style="{
                background: 'rgba(171,199,255,.5)',
                border: 'none'
              }"
              :body-style="{ overflow: 'hidden' }"
              :responsive="false"
              style="height: 100%"
            >
              <div>右边栏</div>
              <template #body>
                <ele-split-panel
                  :space="0"
                  size="20%"
                  :reverse="true"
                  :vertical="true"
                  :resizable="true"
                  :percentage="true"
                  :allow-collapse="true"
                  :collapse-btn-offset="2"
                  :custom-style="{
                    background: 'rgba(185,182,229,.4)',
                    border: 'none'
                  }"
                  :body-style="{ background: 'rgba(125,226,252,.4)' }"
                  :responsive="false"
                  style="height: 100%"
                >
                  <div>底栏</div>
                  <template #body>
                    <div>内容</div>
                  </template>
                </ele-split-panel>
              </template>
            </ele-split-panel>
          </template>
        </ele-split-panel>
      </template>
    </ele-split-panel>
  </ele-card>
  <ele-card header="实际案例">
    <el-button type="primary" @click="openTable">结合表格案例</el-button>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  const emit = defineEmits<{
    (e: 'change', type?: string): void;
  }>();

  /** 是否显示折叠按钮 */
  const allowCollapse = ref<boolean | 'both'>(true);

  /** 是否支持自由拉伸 */
  const resizable = ref(true);

  /** 是否上下布局模式 */
  const vertical = ref(false);

  /** 是否反转布局方向 */
  const reverse = ref(false);

  /** 切换到结合表格案例 */
  const openTable = () => {
    emit('change', 'table');
  };
</script>
