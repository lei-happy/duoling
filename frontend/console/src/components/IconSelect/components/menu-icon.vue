<template>
  <template v-if="icon">
    <img
      v-if="isSimpleTheme"
      :src="imgIconUrls[`/src/assets/menu-icons/${icon}.png`] || defaultImgUrl"
      :style="[{ width: '22px', height: '22px', background: 'none' }, imgStyle]"
      :class="imgClass"
    />
    <ElIcon
      v-else
      :style="componentStyle"
      :class="componentClass"
      v-bind="componentProps || {}"
    >
      <component :is="icon" :style="iconStyle" />
    </ElIcon>
  </template>
</template>

<script lang="ts" setup>
  import type { PropType, CSSProperties } from 'vue';
  import type { ElIconProps } from 'ele-admin-plus/es/ele-app/el';
  import { imgIconUrls, useIsSimpleTheme } from '../util';
  const defaultImgUrl =
    imgIconUrls['/src/assets/menu-icons/IconProLinkOutlined.png'];

  defineProps({
    /** 图标名称 */
    icon: String,
    /** 图标组件属性 */
    componentProps: Object as PropType<ElIconProps>,
    /** 图标图片类名 */
    componentClass: String,
    /** 图标组件样式 */
    componentStyle: Object as PropType<CSSProperties>,
    /** 图标 svg 样式 */
    iconStyle: Object as PropType<CSSProperties>,
    /** 图标图片类名 */
    imgClass: String,
    /** 图标图片样式 */
    imgStyle: Object as PropType<CSSProperties>
  });

  /** 是否是清新主题 */
  const { isSimpleTheme } = useIsSimpleTheme();
</script>
