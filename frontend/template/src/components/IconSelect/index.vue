<!-- 图标选择器 -->
<template>
  <EleIconSelect
    v-bind="{ ...emitProps, ...omit($props, ['componentLang']) }"
    :data="iconData"
  >
    <template #icon="{ icon }">
      <MenuIcon :icon="icon" />
    </template>
  </EleIconSelect>
</template>

<script lang="ts" setup>
  import type { PropType } from 'vue';
  import { computed } from 'vue';
  import {
    iconSelectProps,
    iconSelectEmits
  } from 'ele-admin-plus/es/ele-icon-select/props';
  import { omit } from 'ele-admin-plus/es/utils/common';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import { useComponentLang } from '@/utils/use-component-lang';
  import type { IconSelectLocale } from './util';
  import MenuIcon from './components/menu-icon.vue';
  import { getIconSelectData, imgIconNames, useIsSimpleTheme } from './util';

  defineOptions({ name: 'IconSelect' });

  const props = defineProps({
    ...iconSelectProps,
    /** 自定义文案 */
    componentLang: { type: Object as PropType<Partial<IconSelectLocale>> }
  });

  const emit = defineEmits(iconSelectEmits);

  const { emitProps } = useComponentEvents(iconSelectEmits, emit);

  const { lang } = useComponentLang<IconSelectLocale>(
    {
      zh_CN: {
        outlined: '线框风格',
        filled: '实底风格'
      },
      zh_TW: {
        outlined: '線框風格',
        filled: '實底風格'
      },
      en: {
        outlined: 'Outlined',
        filled: 'Filled'
      }
    },
    props
  );

  /** 是否是清新主题 */
  const { isSimpleTheme } = useIsSimpleTheme();

  /** 图标数据 */
  const iconData = computed(() => {
    if (isSimpleTheme.value) {
      return [{ title: 'EleAdminPlus', icons: imgIconNames }];
    }
    return getIconSelectData(lang.value);
  });
</script>
