<template>
  <ele-card header="自定义数据" :body-style="{ padding: 0 }">
    <div
      :style="{
        maxWidth: type === 'default' ? '100%' : '260px',
        padding: type === 'default' ? 0 : '20px'
      }"
    >
      <ele-icon-select
        clearable
        filterable
        :data="icons"
        v-model="selectedIcon"
        placeholder="请选择"
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
          type === 'modal' ? { maxable: true, closeOnClickModal: true } : void 0
        "
      >
        <template #icon="{ icon }">
          <el-icon>
            <component :is="icon" />
          </el-icon>
        </template>
      </ele-icon-select>
    </div>
    <div v-if="type === 'default'" style="padding: 20px">
      选中数据：{{ selectedIcon }}
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { IconItem } from 'ele-admin-plus/es/ele-icon-select/types';
  import type { PopperType } from 'ele-admin-plus/es/ele-basic-select/types';
  import * as BasicIcons from './basic-icons';

  defineOptions({ components: BasicIcons });

  defineProps<{
    type?: PopperType;
    tooltipType?: boolean | 'static';
  }>();

  /** 选中值 */
  const selectedIcon = ref('');

  /** 图标数据 */
  const icons = ref<IconItem[]>([
    {
      title: '线框风格',
      children: [
        {
          title: 'System',
          icons: [
            'CheckCircleOutlined',
            'CloseCircleOutlined',
            'QuestionCircleOutlined',
            'UserOutlined',
            'SearchOutlined',
            'SettingOutlined',
            'HomeOutlined',
            'MessageOutlined',
            'EditOutlined',
            'DeleteOutlined',
            'PlusCircleOutlined',
            'MinusCircleOutlined'
          ]
        },
        {
          title: 'Arrow',
          icons: ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']
        },
        {
          title: 'Media',
          icons: ['VerticalRightOutlined', 'VerticalLeftOutlined']
        },
        {
          title: 'Other',
          icons: ['DashboardOutlined', 'CompassOutlined', 'ProtectOutlined']
        }
      ]
    },
    {
      title: '实底风格',
      children: [
        {
          title: 'System',
          icons: [
            'CheckCircleFilled',
            'CloseCircleFilled',
            'QuestionCircleFilled',
            'ExclamationCircleFilled',
            'FilterFilled'
          ]
        },
        {
          title: 'Arrow',
          icons: ['CaretUpFilled', 'CaretDownFilled']
        },
        {
          title: 'Media',
          icons: [
            'StepBackwardFilled',
            'StepForwardFilled',
            'PlayFilled',
            'PauseFilled'
          ]
        },
        {
          title: 'Other',
          icons: ['QqFilled', 'WechatFilled', 'AlipayFilled']
        }
      ]
    }
  ]);
</script>
