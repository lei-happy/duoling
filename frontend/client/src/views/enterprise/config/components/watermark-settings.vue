<template>
  <div class="watermark-settings">
    <div v-if="enabledItem" class="watermark-setting-row">
      <div class="watermark-setting-label">启用水印：</div>
      <div class="watermark-setting-body">
        <el-switch v-model="enabledDraft" />
        <span class="config-default config-default--inline">默认值：关闭</span>
      </div>
    </div>

    <div
      v-if="contentItem"
      class="watermark-setting-row watermark-setting-row--top"
    >
      <div class="watermark-setting-label">水印内容：</div>
      <div class="watermark-setting-body watermark-setting-body--column">
        <el-input
          ref="contentInputRef"
          v-model="contentDraft"
          type="textarea"
          :rows="3"
          placeholder="例如：{nickname} {phoneLast4} {date}"
        />
        <div class="watermark-variable-bar">
          <span class="watermark-variable-bar__label">插入变量：</span>
          <el-button
            v-for="item in WATERMARK_VARIABLES"
            :key="item.key"
            size="small"
            @click="insertVariable(item.key)"
          >
            {{ item.label }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="watermark-setting-row">
      <div class="watermark-setting-label">字号：</div>
      <div class="watermark-setting-body watermark-setting-body--slider">
        <el-slider
          v-model="styleDraft.fontSize"
          :min="12"
          :max="24"
          :step="1"
          :format-tooltip="(val: number) => `${val}px`"
        />
      </div>
    </div>

    <div class="watermark-setting-row">
      <div class="watermark-setting-label">透明度：</div>
      <div class="watermark-setting-body watermark-setting-body--slider">
        <el-slider
          v-model="opacityPercent"
          :min="5"
          :max="30"
          :format-tooltip="(val: number) => `${val}%`"
        />
      </div>
    </div>

    <div class="watermark-setting-row">
      <div class="watermark-setting-label">旋转角度：</div>
      <div class="watermark-setting-body watermark-setting-body--slider">
        <el-slider
          v-model="styleDraft.rotate"
          :min="-45"
          :max="0"
          :step="1"
          :format-tooltip="(val: number) => `${val}°`"
        />
      </div>
    </div>

    <div class="watermark-setting-row">
      <div class="watermark-setting-label">水平间距：</div>
      <div class="watermark-setting-body watermark-setting-body--slider">
        <el-slider
          v-model="styleDraft.gap[0]"
          :min="100"
          :max="300"
          :step="10"
          :format-tooltip="(val: number) => `${val}px`"
        />
      </div>
    </div>

    <div class="watermark-setting-row">
      <div class="watermark-setting-label">垂直间距：</div>
      <div class="watermark-setting-body watermark-setting-body--slider">
        <el-slider
          v-model="styleDraft.gap[1]"
          :min="80"
          :max="240"
          :step="10"
          :format-tooltip="(val: number) => `${val}px`"
        />
      </div>
    </div>

    <div class="watermark-preview">
      <div class="watermark-preview__title">效果预览</div>
      <div class="watermark-preview__desc">
        下方为本地预览，保存后才会在全站页面生效
      </div>
      <div class="watermark-preview__frame">
        <SystemWatermarkOverlay
          :visible="enabledDraft"
          :content="previewContent"
          :gap="styleDraft.gap"
          :rotate="styleDraft.rotate"
          :font="previewFont"
          :z-index="styleDraft.zIndex"
          :height="220"
        >
          <div class="watermark-preview__mock">
            <div class="watermark-preview__mock-toolbar"></div>
            <div class="watermark-preview__mock-table">
              <div
                v-for="row in 4"
                :key="row"
                class="watermark-preview__mock-row"
              ></div>
            </div>
          </div>
        </SystemWatermarkOverlay>
      </div>
      <div v-if="!enabledDraft" class="watermark-preview__hint">
        开启「启用水印」后可预览效果
      </div>
      <div class="watermark-preview__actions">
        <el-button
          type="primary"
          :loading="saving"
          :disabled="!isDirty"
          @click="handleSave"
        >
          保存设置
        </el-button>
        <el-button :disabled="!isDirty || saving" @click="resetDraft">
          重置
        </el-button>
        <span v-if="isDirty" class="watermark-preview__dirty"
          >有未保存的修改</span
        >
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import type { InputInstance } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { storeToRefs } from 'pinia';
  import { updateConfig } from '@/api/system/config';
  import type { SystemConfig } from '@/api/system/config/model';
  import { useUserStore } from '@/store/modules/user';
  import { useThemeStore } from '@/store/modules/theme';
  import SystemWatermarkOverlay from '@/components/SystemWatermarkOverlay/index.vue';
  import {
    refreshWatermarkConfig,
    applyWatermarkConfigValues
  } from '@/utils/use-watermark-config';
  import {
    buildWatermarkFont,
    DEFAULT_WATERMARK_CONTENT,
    DEFAULT_WATERMARK_STYLE,
    DEFAULT_WATERMARK_STYLE_JSON,
    getColorAlpha,
    parseWatermarkStyle,
    resolveWatermarkContent,
    serializeWatermarkStyle,
    setColorAlpha,
    WATERMARK_VARIABLES,
    type WatermarkStyleConfig
  } from '@/utils/watermark';

  defineOptions({ name: 'WatermarkSettings' });

  const props = defineProps<{
    items: SystemConfig[];
  }>();

  const emit = defineEmits<{
    (
      e: 'saved',
      payload: { enabled: string; content: string; style: string }
    ): void;
  }>();

  const userStore = useUserStore();
  const themeStore = useThemeStore();
  const { info } = storeToRefs(userStore);
  const { darkMode } = storeToRefs(themeStore);

  const contentInputRef = ref<InputInstance>();
  const saving = ref(false);
  const syncing = ref(false);
  const enabledDraft = ref(false);
  const contentDraft = ref(DEFAULT_WATERMARK_CONTENT);
  const styleDraft = ref<WatermarkStyleConfig>({ ...DEFAULT_WATERMARK_STYLE });
  const opacityPercent = ref(
    Math.round(getColorAlpha(DEFAULT_WATERMARK_STYLE.color) * 100)
  );

  const enabledItem = computed(() =>
    props.items.find((item) => item.configKey === 'system.watermark_enabled')
  );

  const contentItem = computed(() =>
    props.items.find((item) => item.configKey === 'system.watermark_content')
  );

  const styleItem = computed(() =>
    props.items.find((item) => item.configKey === 'system.watermark_style')
  );

  const savedEnabled = computed(
    () => enabledItem.value?.configValue === 'true'
  );

  const savedContent = computed(
    () => contentItem.value?.configValue || DEFAULT_WATERMARK_CONTENT
  );

  const savedStyleJson = computed(
    () => styleItem.value?.configValue || DEFAULT_WATERMARK_STYLE_JSON
  );

  const draftStyleJson = computed(() =>
    serializeWatermarkStyle(styleDraft.value)
  );

  const isDirty = computed(() => {
    const enabledVal = enabledDraft.value ? 'true' : 'false';
    const contentVal = contentDraft.value.trim() || DEFAULT_WATERMARK_CONTENT;
    return (
      enabledVal !== (enabledItem.value?.configValue ?? 'false') ||
      contentVal !== savedContent.value ||
      draftStyleJson.value !== savedStyleJson.value
    );
  });

  const syncDraftFromItems = () => {
    syncing.value = true;
    enabledDraft.value = savedEnabled.value;
    contentDraft.value = savedContent.value;
    styleDraft.value = parseWatermarkStyle(savedStyleJson.value);
    opacityPercent.value = Math.round(
      getColorAlpha(styleDraft.value.color) * 100
    );
    syncing.value = false;
  };

  watch(
    () => [
      enabledItem.value?.configValue,
      contentItem.value?.configValue,
      styleItem.value?.configValue
    ],
    syncDraftFromItems,
    { immediate: true }
  );

  watch(opacityPercent, (percent) => {
    if (syncing.value) {
      return;
    }
    styleDraft.value.color = setColorAlpha(
      styleDraft.value.color,
      percent / 100
    );
  });

  const previewContent = computed(() =>
    resolveWatermarkContent(contentDraft.value, info.value)
  );

  const previewFont = computed(() =>
    buildWatermarkFont(styleDraft.value, darkMode.value)
  );

  const resetDraft = () => {
    syncDraftFromItems();
  };

  const handleSave = async () => {
    if (!enabledItem.value || !contentItem.value || !styleItem.value) {
      return;
    }
    const enabledVal = enabledDraft.value ? 'true' : 'false';
    const contentVal = contentDraft.value.trim() || DEFAULT_WATERMARK_CONTENT;
    const styleVal = draftStyleJson.value;

    saving.value = true;
    try {
      await Promise.all([
        updateConfig('system.watermark_enabled', enabledVal),
        updateConfig('system.watermark_content', contentVal),
        updateConfig('system.watermark_style', styleVal)
      ]);
      emit('saved', {
        enabled: enabledVal,
        content: contentVal,
        style: styleVal
      });
      applyWatermarkConfigValues({
        enabled: enabledVal,
        content: contentVal,
        style: styleVal
      });
      await refreshWatermarkConfig();
      EleMessage.success({ message: '保存成功，水印已全站生效', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message || '保存失败', plain: true });
    } finally {
      saving.value = false;
    }
  };

  const insertVariable = (key: string) => {
    const token = `{${key}}`;
    contentDraft.value = contentDraft.value
      ? `${contentDraft.value} ${token}`.trim()
      : token;
    contentInputRef.value?.focus?.();
  };
</script>

<style scoped>
  .watermark-settings {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .watermark-setting-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 20px;
  }

  .watermark-setting-row--top {
    align-items: flex-start;
  }

  .watermark-setting-label {
    flex-shrink: 0;
    width: 88px;
    font-size: var(--el-form-label-font-size);
    color: var(--el-text-color-regular);
    line-height: var(--el-component-size);
  }

  .watermark-setting-body {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px 16px;
    flex: 1;
    min-width: 0;
  }

  .watermark-setting-body--column {
    flex-direction: column;
    align-items: stretch;
  }

  .watermark-setting-body--slider {
    max-width: 360px;
  }

  .config-default {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  .config-default--inline {
    margin-top: 0;
  }

  .watermark-variable-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .watermark-variable-bar__label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .watermark-preview__title {
    margin-bottom: 6px;
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .watermark-preview__desc {
    margin-bottom: 10px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .watermark-preview__frame {
    border: 1px solid var(--el-border-color-light);
    border-radius: var(--el-border-radius-base);
    overflow: hidden;
    background: var(--el-bg-color);
  }

  .watermark-preview__mock {
    padding: 12px;
    background: var(--el-fill-color-blank);
  }

  .watermark-preview__mock-toolbar {
    height: 28px;
    margin-bottom: 12px;
    border-radius: 4px;
    background: var(--el-fill-color-light);
  }

  .watermark-preview__mock-table {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .watermark-preview__mock-row {
    height: 28px;
    border-radius: 4px;
    background: var(--el-fill-color-lighter);
  }

  .watermark-preview__hint {
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .watermark-preview__actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
  }

  .watermark-preview__dirty {
    font-size: 12px;
    color: var(--el-color-warning);
  }
</style>
