<template>
  <template v-if="icon">
    <!-- 优先：自定义 SVG 图标（使用 mask-image 继承 currentColor） -->
    <ElIcon
      v-if="customSvgUrl"
      :style="componentStyle"
      :class="componentClass"
      v-bind="componentProps || {}"
    >
      <span
        class="custom-svg-icon"
        :style="[customSvgStyle, iconStyle]"
      />
    </ElIcon>
    <!-- 清新主题 PNG 图标 -->
    <img
      v-else-if="isSimpleTheme"
      :src="imgIconUrls[`/src/assets/menu-icons/${icon}.png`] || defaultImgUrl"
      :style="[{ width: '22px', height: '22px', background: 'none' }, imgStyle]"
      :class="imgClass"
    />
    <!-- 默认：组件图标（Element Plus / EleAdminPlus 全局注册的组件） -->
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
  import { computed } from 'vue';
  import type { ElIconProps } from 'ele-admin-plus/es/ele-app/el';
  import { imgIconUrls, useIsSimpleTheme, getSvgIconUrl } from '../util';
  const defaultImgUrl =
    imgIconUrls['/src/assets/menu-icons/IconProLinkOutlined.png'];

  const props = defineProps({
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

  /** 自定义 SVG 图标 URL（如果在 menu-icons 目录中找到同名 .svg 文件） */
  const customSvgUrl = computed(() => {
    if (!props.icon) return undefined;
    return getSvgIconUrl(props.icon);
  });

  /** 自定义 SVG 图标通过 mask-image 渲染的样式 */
  const customSvgStyle = computed<CSSProperties>(() => ({
    maskImage: `url(${customSvgUrl.value})`,
    WebkitMaskImage: `url(${customSvgUrl.value})`
  }));
</script>

<style scoped>
  .custom-svg-icon {
    display: inline-block;
    width: 1em;
    height: 1em;
    vertical-align: -0.15em;
    background-color: currentColor;
    mask-size: 100% 100%;
    -webkit-mask-size: 100% 100%;
    mask-repeat: no-repeat;
    -webkit-mask-repeat: no-repeat;
    mask-position: center;
    -webkit-mask-position: center;
  }
</style>
