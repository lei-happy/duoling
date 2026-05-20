<template>
  <div class="waybill-settings">
    <div v-if="freightItem" class="waybill-setting-row">
      <div class="waybill-setting-label">
        运费计算模式：
        <ele-tooltip
          placement="top-start"
          effect="light"
          :width="360"
          :offset="4"
        >
          <template #content>
            <div class="freight-help-tip">
              <p class="freight-help-tip__title">各模式说明</p>
              <ul>
                <li>
                  <span class="freight-help-tip__name">强制自动计费</span>
                  ：必须使用系统自动计算的运费，不允许手工填写。
                </li>
                <li>
                  <span class="freight-help-tip__name">优先自动，允许手动</span>
                  ：优先采用自动计费结果，必要时允许人工调整或填写。
                </li>
                <li>
                  <span class="freight-help-tip__name">仅手动填写</span>
                  ：运费以手工录入为准。
                </li>
              </ul>
            </div>
          </template>
          <el-icon class="field-help-icon" tabindex="-1">
            <QuestionCircleOutlined />
          </el-icon>
        </ele-tooltip>
      </div>
      <div class="waybill-setting-body">
        <el-radio-group
          :model-value="freightItem.configValue"
          @update:model-value="(val: string) => emitChange(freightItem!, val)"
        >
          <el-radio
            v-for="opt in freightOptions"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </el-radio>
        </el-radio-group>
        <span
          v-if="freightItem.defaultValue"
          class="config-default config-default--inline"
        >
          默认值：{{
            getEnumDisplayLabel(freightItem.configKey, freightItem.defaultValue)
          }}
        </span>
      </div>
    </div>
    <div v-if="listShowFreightItem" class="waybill-setting-row">
      <div class="waybill-setting-label">
        列表显示运费：
        <ele-tooltip
          placement="top-start"
          effect="light"
          :width="340"
          :offset="4"
        >
          <template #content>
            <div class="freight-help-tip">
              <p class="freight-help-tip__title">说明</p>
              <p class="freight-help-tip__plain">
                运费属于敏感信息。关闭后，运单列表与列表分页接口均不返回具体金额，编辑运单时亦不显示「运费信息」步骤；计算明细等仍可查看与维护运费。
              </p>
            </div>
          </template>
          <el-icon class="field-help-icon" tabindex="-1">
            <QuestionCircleOutlined />
          </el-icon>
        </ele-tooltip>
      </div>
      <div class="waybill-setting-body">
        <el-switch
          :model-value="listShowFreightItem.configValue === 'true'"
          @update:model-value="
            (val: boolean) =>
              emitChange(listShowFreightItem!, val ? 'true' : 'false')
          "
        />
        <span class="config-default config-default--inline">
          默认值：不显示
        </span>
      </div>
    </div>
    <div v-if="autoConfirmItem" class="waybill-setting-row">
      <div class="waybill-setting-label">
        运单录入自动确认：
        <ele-tooltip
          placement="top-start"
          effect="light"
          :width="360"
          :offset="4"
        >
          <template #content>
            <div class="freight-help-tip">
              <p class="freight-help-tip__title">说明</p>
              <p class="freight-help-tip__plain">
                关闭：新建或导入的运单先进入「待确认」，需要运营点击确认后再进入「待调度」。
              </p>
              <p class="freight-help-tip__plain">
                开启：新建或导入的运单跳过待确认，直接进入「待调度」。仅对开关开启后录入的运单生效，已存在的待确认运单仍需手动确认。
              </p>
            </div>
          </template>
          <el-icon class="field-help-icon" tabindex="-1">
            <QuestionCircleOutlined />
          </el-icon>
        </ele-tooltip>
      </div>
      <div class="waybill-setting-body">
        <el-switch
          :model-value="autoConfirmItem.configValue === 'true'"
          @update:model-value="
            (val: boolean) =>
              emitChange(autoConfirmItem!, val ? 'true' : 'false')
          "
        />
        <span class="config-default config-default--inline">
          默认值：关闭（需手动确认）
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { SystemConfig } from '@/api/system/config/model';
  import { QuestionCircleOutlined } from '@/components/icons';
  import {
    CONFIG_ENUM_OPTIONS,
    getEnumDisplayLabel
  } from '@/views/enterprise/config/constants';

  defineOptions({ name: 'WaybillSettings' });

  const props = defineProps<{
    items: SystemConfig[];
  }>();

  const emit = defineEmits<{
    (e: 'config-change', item: SystemConfig, val: string): void;
  }>();

  const freightItem = computed(() =>
    props.items.find((i) => i.configKey === 'waybill.freight_calc_mode')
  );

  const listShowFreightItem = computed(() =>
    props.items.find((i) => i.configKey === 'waybill.list_show_freight_amount')
  );

  const autoConfirmItem = computed(() =>
    props.items.find((i) => i.configKey === 'waybill.auto_confirm_on_create')
  );

  const freightOptions = CONFIG_ENUM_OPTIONS['waybill.freight_calc_mode'] || [];

  const emitChange = (item: SystemConfig, val: string) => {
    emit('config-change', item, val);
  };
</script>

<style scoped>
  .waybill-settings {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .waybill-setting-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 20px;
  }

  .waybill-setting-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
    font-size: var(--el-form-label-font-size);
    color: var(--el-text-color-regular);
    line-height: var(--el-component-size);
  }

  .waybill-setting-body {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px 16px;
    flex: 1;
    min-width: 0;
  }

  .field-help-icon {
    font-size: 15px;
    color: var(--el-text-color-secondary);
    cursor: help;
    outline: none;
  }

  .field-help-icon:hover {
    color: var(--el-color-primary);
  }

  .config-default {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  .config-default--inline {
    margin-top: 0;
  }

  .freight-help-tip {
    line-height: 1.55;
    font-size: 13px;
  }

  .freight-help-tip__title {
    margin: 0 0 8px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .freight-help-tip__plain {
    margin: 0;
    color: var(--el-text-color-regular);
  }

  .freight-help-tip ul {
    margin: 0;
    padding-left: 18px;
  }

  .freight-help-tip li {
    margin-bottom: 6px;
  }

  .freight-help-tip li:last-child {
    margin-bottom: 0;
  }

  .freight-help-tip__name {
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .freight-help-tip__code {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    font-family: var(--el-font-family);
  }
</style>
