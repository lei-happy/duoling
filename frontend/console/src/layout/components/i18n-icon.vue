<!-- 国际化语言切换 -->
<template>
  <ele-dropdown
    :items="items"
    :model-value="locale"
    :placement="placement"
    :menu-style="{ minWidth: '108px' }"
    :popper-options="{
      modifiers: [{ name: 'offset', options: { offset: [0, 5] } }]
    }"
    :icon-props="{
      size: 12,
      style: { fontStyle: 'normal', fontWeight: '600' }
    }"
    style="line-height: inherit"
    @command="changeLanguage"
  >
    <div style="display: flex; align-items: center; height: 100%">
      <el-icon>
        <GlobalOutlined :style="iconStyle" />
      </el-icon>
    </div>
  </ele-dropdown>
</template>

<script lang="ts" setup>
  import type { CSSProperties } from 'vue';
  import { ref, markRaw, h } from 'vue';
  import { useI18n } from 'vue-i18n';
  import type { ElTooltipProps } from 'element-plus';
  import { GlobalOutlined } from '@/components/icons';
  import { setCacheLang } from '@/i18n/use-locale';

  withDefaults(
    defineProps<{
      /** placement */
      placement?: ElTooltipProps['placement'];
      /** 自定义样式 */
      iconStyle?: CSSProperties;
    }>(),
    {
      placement: 'bottom'
    }
  );

  const { locale } = useI18n();

  const items = ref([
    { title: '简体中文', command: 'zh_CN', icon: markRaw(h('span', {}, 'CN')) },
    { title: '繁體中文', command: 'zh_TW', icon: markRaw(h('span', {}, 'HK')) },
    { title: 'English', command: 'en', icon: markRaw(h('span', {}, 'US')) }
  ]);

  /** 切换语言 */
  const changeLanguage = (command: string) => {
    locale.value = command;
    setCacheLang(command);
  };
</script>
