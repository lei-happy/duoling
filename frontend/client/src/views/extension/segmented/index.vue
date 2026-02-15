<template>
  <ele-page>
    <ele-card header="基础用法">
      <div style="overflow-x: auto">
        <ele-segmented
          v-model="active1"
          :items="[
            { label: 'Daily', value: 1 },
            { label: 'Weekly', value: 2 },
            { label: 'Monthly', value: 3 },
            { label: 'Quarterly', value: 4 },
            { label: 'Yearly', value: 5 }
          ]"
        />
      </div>
      <div style="margin: 22px 0 8px 0">宽度铺满:</div>
      <div style="max-width: 600px">
        <ele-segmented
          block
          v-model="active2"
          :items="[
            { label: 'Map', value: 'Map' },
            { label: 'Transit', value: 'Transit' },
            { label: 'Satellite', value: 'Satellite' }
          ]"
        />
      </div>
    </ele-card>
    <ele-card header="禁用">
      <ele-segmented
        disabled
        v-model="active2"
        :items="[
          { label: 'Map', value: 'Map' },
          { label: 'Transit', value: 'Transit' },
          { label: 'Satellite', value: 'Satellite' }
        ]"
      />
      <div style="overflow-x: auto">
        <ele-segmented
          v-model="active1"
          :items="[
            { label: 'Daily', value: 1 },
            { label: 'Weekly', value: 2, disabled: true },
            { label: 'Monthly', value: 3 },
            { label: 'Quarterly', value: 4, disabled: true },
            { label: 'Yearly', value: 5 }
          ]"
          style="margin-top: 16px"
        />
      </div>
    </ele-card>
    <ele-card header="图标">
      <ele-segmented
        v-model="active3"
        :items="[
          {
            label: 'User',
            value: 1,
            icon: UserOutlined,
            iconStyle: { transform: 'translateY(-1px)' }
          },
          {
            label: 'Setting',
            value: 2,
            icon: SettingOutlined,
            iconStyle: { transform: 'translateY(-1px)' }
          }
        ]"
      />
      <ele-segmented
        v-model="active3"
        :items="[
          { value: 1, icon: UserOutlined },
          { value: 2, icon: SettingOutlined }
        ]"
        style="margin-top: 16px"
      />
    </ele-card>
    <ele-card header="尺寸">
      <div style="overflow-x: auto">
        <ele-segmented
          size="large"
          v-model="active1"
          :items="[
            { label: 'Daily', value: 1 },
            { label: 'Weekly', value: 2 },
            { label: 'Monthly', value: 3 },
            { label: 'Quarterly', value: 4 },
            { label: 'Yearly', value: 5 }
          ]"
        />
      </div>
      <div style="overflow-x: auto">
        <ele-segmented
          v-model="active1"
          :items="[
            { label: 'Daily', value: 1 },
            { label: 'Weekly', value: 2 },
            { label: 'Monthly', value: 3 },
            { label: 'Quarterly', value: 4 },
            { label: 'Yearly', value: 5 }
          ]"
          style="margin-top: 16px"
        />
      </div>
      <div style="overflow-x: auto">
        <ele-segmented
          size="small"
          v-model="active1"
          :items="[
            { label: 'Daily', value: 1 },
            { label: 'Weekly', value: 2 },
            { label: 'Monthly', value: 3 },
            { label: 'Quarterly', value: 4 },
            { label: 'Yearly', value: 5 }
          ]"
          style="margin-top: 16px"
        />
      </div>
    </ele-card>
    <ele-card header="自定义渲染">
      <ele-segmented
        size="large"
        v-model="active2"
        :items="items"
        style="--ele-segmented-large-height: 68px"
      >
        <template #label="{ item }">
          <div
            :style="{
              lineHeight: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }"
          >
            <el-avatar :src="item.avatar" :size="32" />
            <div style="margin-top: 6px; font-size: 14px">
              {{ item.label }}
            </div>
          </div>
        </template>
      </ele-segmented>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { UserOutlined, SettingOutlined } from '@/components/icons';

  defineOptions({ name: 'ExtensionSegmented' });

  const active1 = ref(1);

  const active2 = ref('Map');

  const active3 = ref(1);

  const items = ref([
    {
      label: 'Map',
      value: 'Map',
      avatar:
        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg'
    },
    {
      label: 'Transit',
      value: 'Transit',
      avatar:
        'https://cdn.eleadmin.com/20200609/b6a811873e704db49db994053a5019b2.jpg'
    },
    {
      label: 'Satellite',
      value: 'Satellite',
      avatar:
        'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg'
    }
  ]);
</script>
