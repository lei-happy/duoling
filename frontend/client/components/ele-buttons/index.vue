<!-- 表格操作按钮 -->
<template>
  <div
    v-if="gap != null || wrap != null || modalFooter"
    class="ele-buttons-wrap ele-buttons"
    :class="{
      'is-nowrap': wrap === false,
      'is-gap': gap != null,
      'is-modal-footer': modalFooter
    }"
    :style="gap == null || gap === true ? {} : { gap: `${gap || 0}px` }"
  >
    <ItemRender
      v-for="(item, index) in items"
      :key="item.key ?? item.command ?? item.title"
      :item="item"
      :divider="index === 0 ? false : divider"
      :type="type"
      :wrapClass="false"
      :lang="lang"
      @itemClick="handleItemClick"
    />
    <slot></slot>
  </div>
  <template v-else>
    <ItemRender
      v-for="(item, index) in items"
      :key="item.key ?? item.command ?? item.title"
      :item="item"
      :divider="index === 0 ? false : divider"
      :type="type"
      :wrapClass="true"
      :lang="lang"
      @itemClick="handleItemClick"
    />
    <slot></slot>
  </template>
</template>

<script lang="ts" setup>
  import { useLocale } from '../ele-config-provider/receiver';
  import ItemRender from './components/item-render.vue';
  import { buttonsProps, buttonsEmits } from './props';

  defineOptions({ name: 'EleButtons' });

  const props = defineProps(buttonsProps);

  const emit = defineEmits(buttonsEmits);

  /** 国际化语言 */
  const { lang } = useLocale('buttons', props);

  /** 操作项点击事件 */
  const handleItemClick = (command: any, e?: MouseEvent) => {
    emit('itemClick', command, e);
  };
</script>
