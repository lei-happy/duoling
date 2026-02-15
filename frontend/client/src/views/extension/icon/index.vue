<template>
  <ele-page>
    <ele-card header="基础用法" :body-style="{ padding: 0 }">
      <div style="padding: 20px 0 16px 20px">
        <option-item label="下拉模式" style="margin: 0 0 12px 0">
          <el-radio-group v-model="type">
            <el-radio value="popper" label="下拉" />
            <el-radio value="modal" label="弹窗" />
            <el-radio value="drawer" label="抽屉" />
            <el-radio value="default" label="嵌入" />
          </el-radio-group>
        </option-item>
        <option-item label="图标网格" style="margin: 0">
          <el-radio-group v-model="tooltipType">
            <el-radio :value="true" label="紧凑" />
            <el-radio value="static" label="宽松" />
          </el-radio-group>
        </option-item>
      </div>
      <div
        :style="{
          maxWidth: type === 'default' ? '100%' : '260px',
          padding: type === 'default' ? 0 : '0 20px 20px 20px'
        }"
      >
        <icon-select
          clearable
          v-model="selectedIcon"
          placeholder="请选择图标"
          filterable="popper"
          :popper-options="{ strategy: 'fixed' }"
          :popper-type="type"
          :tooltip="tooltipType"
          :popper-width="
            type === 'modal' || type === 'drawer'
              ? 720
              : tooltipType === 'static'
                ? 568
                : void 0
          "
          :popper-height="
            type === 'modal' ? 580 : tooltipType === 'static' ? 448 : 388
          "
          :popper-props="
            type === 'modal'
              ? { maxable: true, closeOnClickModal: true }
              : void 0
          "
        />
      </div>
      <div v-if="type === 'default'" style="padding: 20px">
        选中数据：{{ selectedIcon }}
      </div>
    </ele-card>
    <demo-basic :type="type" :tooltipType="tooltipType" />
    <demo-advanced :type="type" :tooltipType="tooltipType" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { PopperType } from 'ele-admin-plus/es/ele-basic-select/types';
  import type { ItemTooltip } from 'ele-admin-plus/es/ele-icon-select/types';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';
  import IconSelect from '@/components/IconSelect/index.vue';
  import DemoBasic from './components/demo-basic.vue';
  import DemoAdvanced from './components/demo-advanced.vue';

  defineOptions({ name: 'ExtensionIcon' });

  /** 选中的图标 */
  const selectedIcon = ref('');

  /** 下拉模式 */
  const type = ref<PopperType>('popper');

  /** 图标网格 */
  const tooltipType = ref<ItemTooltip>(true);
</script>
