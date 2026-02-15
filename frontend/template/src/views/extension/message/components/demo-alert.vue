<template>
  <ele-card header="警告提示">
    <div style="margin-bottom: 8px">基本用法:</div>
    <el-row :gutter="16">
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          title="Info Text"
          show-icon
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          type="success"
          title="Success Text"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          type="warning"
          title="Warning Text"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          type="error"
          title="Error Text"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
    </el-row>
    <div style="margin: 8px 0">文字描述:</div>
    <el-row :gutter="16">
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          title="Info Text"
          description="Info Description Info Description Info Description Info Description"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          type="success"
          title="Success Text"
          description="Success Description Success Description Success Description"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          type="warning"
          title="Warning Text"
          description="Warning Description Warning Description Warning Description"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
      <el-col :md="6" :sm="12" :xs="24">
        <ele-alert
          show-icon
          type="error"
          title="Error Text"
          description="Error Description Error Description Error Description Error Description"
          style="margin-bottom: 12px"
          :effect="effect"
        />
      </el-col>
    </el-row>
    <div style="margin: 8px 0">嵌套使用、操作按钮:</div>
    <el-row :gutter="16">
      <el-col :md="6" :sm="24" :xs="24">
        <ele-alert
          show-icon
          title="嵌套使用"
          :closable="false"
          :effect="effect"
          :icon-props="{ style: { fontSize: '18px', marginTop: '3px' } }"
          style="margin-bottom: 12px"
        >
          <ele-alert
            show-icon
            type="error"
            title="Error Description Error Description"
            :effect="effect"
            :title-style="{ fontSize: '13px', lineHeight: '18px' }"
          />
        </ele-alert>
      </el-col>
      <el-col :md="6" :sm="24" :xs="24">
        <ele-alert
          show-icon
          title="Info Text"
          description="Info Description Info Description"
          :effect="effect"
          style="margin-bottom: 12px"
        >
          <template #action>
            <div
              :style="{
                display: 'flex',
                'flex-direction': 'column',
                '--el-fill-color-light': 'rgba(0, 0, 0, 0.06)',
                '--el-fill-color': 'rgba(0, 0, 0, 0.15)'
              }"
            >
              <el-button type="primary" size="small" style="width: 72px">
                Accept
              </el-button>
              <el-button
                :text="effect !== 'dark'"
                :type="effect === 'dark' ? 'primary' : void 0"
                size="small"
                style="margin: 4px 0 0 0; width: 72px"
              >
                Decline
              </el-button>
            </div>
          </template>
        </ele-alert>
      </el-col>
      <el-col :md="6" :sm="24" :xs="24">
        <ele-alert
          show-icon
          type="success"
          title="Success Text"
          :effect="effect"
          style="margin-bottom: 12px"
        >
          <template #action>
            <div
              :style="{
                '--el-fill-color-light': 'rgba(0, 0, 0, 0.06)',
                '--el-fill-color': 'rgba(0, 0, 0, 0.15)'
              }"
            >
              <el-button
                :text="effect !== 'dark'"
                :type="effect === 'dark' ? 'success' : void 0"
                size="small"
              >
                UNDO
              </el-button>
            </div>
          </template>
        </ele-alert>
      </el-col>
      <el-col :md="6" :sm="24" :xs="24">
        <ele-alert
          show-icon
          type="error"
          title="Error Text"
          :closable="false"
          :effect="effect"
          style="margin-bottom: 12px"
        >
          <template #action>
            <div
              :style="{
                '--el-fill-color-light': 'rgba(0, 0, 0, 0.06)',
                '--el-fill-color': 'rgba(0, 0, 0, 0.15)'
              }"
            >
              <el-button
                :text="effect !== 'dark'"
                :type="effect === 'dark' ? 'danger' : void 0"
                size="small"
                style="padding: 0 6px"
              >
                UNDO
              </el-button>
            </div>
          </template>
        </ele-alert>
      </el-col>
    </el-row>
    <option-item label="主题风格">
      <el-radio-group v-model="effect">
        <el-radio value="light" label="light" />
        <el-radio value="dark" label="dark" />
      </el-radio-group>
    </option-item>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  /** 警告提示主题 */
  const effect = ref<'light' | 'dark'>('light');
</script>
