import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { listConfigsByGroup } from '@/api/system/config';
import { useUserStore } from '@/store/modules/user';
import { useThemeStore } from '@/store/modules/theme';
import {
  buildWatermarkFont,
  DEFAULT_WATERMARK_CONTENT,
  DEFAULT_WATERMARK_STYLE_JSON,
  parseWatermarkStyle,
  resolveWatermarkContent
} from '@/utils/watermark';

const enabled = ref(false);
const contentTemplate = ref(DEFAULT_WATERMARK_CONTENT);
const styleJson = ref(DEFAULT_WATERMARK_STYLE_JSON);
const ready = ref(false);
let loadingPromise: Promise<void> | null = null;

function applyConfigItems(
  items: Array<{ configKey: string; configValue?: string }>
) {
  const map = new Map(items.map((item) => [item.configKey, item.configValue]));
  enabled.value = map.get('system.watermark_enabled') === 'true';
  contentTemplate.value =
    map.get('system.watermark_content') || DEFAULT_WATERMARK_CONTENT;
  styleJson.value =
    map.get('system.watermark_style') || DEFAULT_WATERMARK_STYLE_JSON;
  ready.value = true;
}

export async function loadWatermarkConfig(force = false) {
  if (loadingPromise && !force) {
    return loadingPromise;
  }
  loadingPromise = listConfigsByGroup('security')
    .then((items) => {
      applyConfigItems(items ?? []);
    })
    .catch(() => {
      ready.value = true;
    })
    .finally(() => {
      loadingPromise = null;
    });
  return loadingPromise;
}

export function refreshWatermarkConfig() {
  return loadWatermarkConfig(true);
}

/** 保存成功后立即写入全局状态，避免与预览参数不一致 */
export function applyWatermarkConfigValues(values: {
  enabled: string;
  content: string;
  style: string;
}) {
  enabled.value = values.enabled === 'true';
  contentTemplate.value = values.content || DEFAULT_WATERMARK_CONTENT;
  styleJson.value = values.style || DEFAULT_WATERMARK_STYLE_JSON;
  ready.value = true;
}

export function useWatermarkConfig() {
  const userStore = useUserStore();
  const themeStore = useThemeStore();
  const { info } = storeToRefs(userStore);
  const { darkMode } = storeToRefs(themeStore);

  const parsedStyle = computed(() => parseWatermarkStyle(styleJson.value));

  const watermarkEnabled = computed(() => enabled.value);

  const watermarkContent = computed(() =>
    resolveWatermarkContent(contentTemplate.value, info.value)
  );

  const watermarkGap = computed(() => parsedStyle.value.gap);

  const watermarkRotate = computed(() => parsedStyle.value.rotate);

  const watermarkZIndex = computed(() => parsedStyle.value.zIndex);

  const watermarkFont = computed(() =>
    buildWatermarkFont(parsedStyle.value, darkMode.value)
  );

  return {
    watermarkReady: ready,
    watermarkEnabled,
    watermarkContent,
    watermarkGap,
    watermarkRotate,
    watermarkZIndex,
    watermarkFont,
    contentTemplate,
    styleJson,
    parsedStyle,
    watermarkRenderKey: computed(
      () => `${enabled.value}|${contentTemplate.value}|${styleJson.value}`
    ),
    loadWatermarkConfig,
    refreshWatermarkConfig,
    applyWatermarkConfigValues
  };
}
