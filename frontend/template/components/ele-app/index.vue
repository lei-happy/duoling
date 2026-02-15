<!-- 包裹组件 -->
<template>
  <slot></slot>
  <EleModalRender
    :modals="modals"
    @removeItem="removeModal"
    @updateItemVisible="updateModalVisible"
    @updateItemProps="updateModalProps"
  />
  <EleDropdown
    v-bind="dropdownProps"
    ref="dropdownRef"
    :triggerKeys="[]"
    :persistent="false"
    componentType="pro"
    :virtualTriggering="true"
    :virtualRef="dropdownVirtualRef"
    :disabled="!dropdownItems.length"
    :items="dropdownItems"
  />
  <ElePopconfirm
    :width="200"
    :triggerKeys="[]"
    :persistent="false"
    placement="top-end"
    v-bind="popconfirmProps"
    ref="popconfirmRef"
    :virtualTriggering="true"
    :virtualRef="popconfirmVirtualRef"
  />
</template>

<script lang="ts" setup>
  import EleModalRender from '../ele-modal-render/index';
  import { useModalRenderProvider } from '../ele-modal-render/util';
  import EleDropdown from '../ele-dropdown/index.vue';
  import { useDropdownProvider } from '../ele-dropdown-provider/util';
  import ElePopconfirm from '../ele-popconfirm/index.vue';
  import { usePopconfirmProvider } from '../ele-popconfirm-provider/util';

  defineOptions({ name: 'EleApp' });

  /** 弹窗操作 */
  const {
    modals,
    openModal,
    closeModal,
    closeAllModal,
    removeModal,
    updateModalVisible,
    updateModalProps
  } = useModalRenderProvider();

  /** 下拉菜单操作 */
  const {
    dropdownRef,
    dropdownVirtualRef,
    dropdownItems,
    dropdownProps,
    openDropdown
  } = useDropdownProvider();

  /** 气泡确认框操作 */
  const {
    popconfirmRef,
    popconfirmVirtualRef,
    popconfirmProps,
    openPopconfirm
  } = usePopconfirmProvider();

  defineExpose({
    // 弹窗操作
    openModal,
    closeModal,
    closeAllModal,
    updateModalProps,
    // 下拉菜单操作
    openDropdown,
    // 气泡确认框操作
    openPopconfirm
  });
</script>
