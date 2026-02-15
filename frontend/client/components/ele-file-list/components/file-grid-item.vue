<!-- 网格布局条目 -->
<template>
  <div
    class="ele-file-list-item"
    :class="[
      { 'is-checked': selected },
      { 'is-active': ctxMenuDropdownVisible }
    ]"
    @click.stop="handleClick"
  >
    <div class="ele-file-list-item-body" @contextmenu="handleContextmenu">
      <div class="ele-file-list-item-icon">
        <slot name="icon" :icon="icon" :item="item">
          <img
            :src="icon"
            :class="{ 'ele-file-list-item-image': !!item.thumbnail }"
          />
        </slot>
      </div>
      <slot name="title" :item="item">
        <div :title="item.name" class="ele-file-list-item-title">
          {{ item.name }}
        </div>
      </slot>
    </div>
    <!-- 复选框 -->
    <div
      v-if="selectable"
      class="ele-file-list-item-checkbox"
      @click.stop="handleCheckChange"
    >
      <i class="ele-file-list-checkbox is-checked"></i>
    </div>
    <!-- 右键菜单 -->
    <div
      ref="dropdownTriggerRef"
      class="ele-file-list-item-dropdown"
      @click.stop=""
    ></div>
  </div>
</template>

<script lang="ts" setup>
  import type { PropType } from 'vue';
  import { ref, computed } from 'vue';
  import type {
    IconItem,
    FileItem,
    SelectionType,
    ContextOpenOption
  } from '../types';

  defineOptions({ name: 'FileGridItem' });

  const props = defineProps({
    /** 数据 */
    item: {
      type: Object as PropType<FileItem>,
      required: true
    },
    /** 选择框类型 */
    selectionType: String as PropType<SelectionType>,
    /** 多选选中数据 */
    selections: Array as PropType<FileItem[]>,
    /** 单选选中数据 */
    current: Object as PropType<FileItem>,
    /** 后缀对应的图标 */
    icons: Array as PropType<IconItem[]>,
    /** 右键下拉菜单是否显示 */
    ctxMenuDropdownVisible: Boolean
  });

  const emit = defineEmits({
    click: (_item: FileItem) => true,
    checkChange: (_item: FileItem) => true,
    contextOpen: (_option: ContextOpenOption) => true
  });

  /** 右键菜单触发节点 */
  const dropdownTriggerRef = ref<HTMLElement | null>(null);

  /** 是否可以选中 */
  const selectable = computed<boolean>(() => {
    return (
      props.selectionType === 'checkbox' || props.selectionType === 'radio'
    );
  });

  /** 是否选中 */
  const selected = computed<boolean>(() => {
    if (!selectable.value || !props.item) {
      return false;
    }
    if (props.selectionType === 'checkbox') {
      return !!(
        props.selections &&
        props.selections.some((t) => t.key === props.item.key)
      );
    }
    return !!(props.current && props.current.key === props.item.key);
  });

  /** 对应图标 */
  const icon = computed<string | undefined>(() => {
    // 有缩略图返回文件缩略图
    if (props.item.thumbnail) {
      return props.item.thumbnail;
    }
    if (!props.icons) {
      return;
    }
    // 文件夹
    if (props.item.isDirectory) {
      return props.icons.find((d) => d.type === 'dir')?.icon;
    }
    // 匹配后缀对应的图标
    if (props.item.name) {
      const icon = props.icons.find((d) => {
        if (!d.suffixes) {
          return false;
        }
        return !!d.suffixes.find((t) => !!props.item.name.endsWith(t));
      })?.icon;
      if (icon) {
        return icon;
      }
    }
    return props.icons.find((d) => d.type === 'file')?.icon;
  });

  /** 点击事件 */
  const handleClick = () => {
    emit('click', props.item);
  };

  /** 复选框点击事件 */
  const handleCheckChange = () => {
    emit('checkChange', props.item);
  };

  /** 触发右键菜单 */
  const handleContextmenu = (e: MouseEvent) => {
    if (dropdownTriggerRef.value != null) {
      emit('contextOpen', {
        item: props.item,
        triggerEl: dropdownTriggerRef.value,
        e
      });
    }
  };
</script>
