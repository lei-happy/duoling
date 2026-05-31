<!-- 快捷操作 -->
<template>
  <ele-card
    header="快捷操作"
    shadow="never"
    :body-style="{ padding: '16px 16px 12px' }"
    class="quick-action-card-wrap"
  >
    <template #extra>
      <ele-dropdown
        :items="menuItems"
        :icon-props="{ size: 15 }"
        placement="bottom-end"
        class="quick-action-more"
        :popper-options="{
          strategy: 'fixed',
          modifiers: [{ name: 'offset', options: { offset: [12, 12] } }]
        }"
        @command="handleMenuCommand"
      >
        <el-icon style="outline: none">
          <MoreOutlined style="transform: scale(1.1)" />
        </el-icon>
      </ele-dropdown>
    </template>
    <el-empty
      v-if="!displayedItems.length"
      description="暂无快捷操作，可通过右上角菜单添加"
      :image-size="64"
      class="quick-action-empty"
    />
    <el-row v-else :gutter="12" ref="wrapRef" class="quick-action-row">
      <el-col
        v-for="item in displayedItems"
        :key="item.key"
        :md="3"
        :sm="6"
        :xs="12"
      >
        <component
          :is="item.type === 'external' ? 'a' : 'router-link'"
          v-bind="getLinkProps(item)"
          class="quick-action-item"
        >
          <div
            class="quick-action-item__icon"
            :style="{ '--action-accent': item.color || '#69c0ff' }"
          >
            <el-icon class="quick-action-item__icon-inner">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <div class="quick-action-item__title">{{ item.title }}</div>
        </component>
      </el-col>
    </el-row>
    <quick-action-picker
      v-model="pickerVisible"
      :available="availableToAdd"
      :selected="selectedConfigs"
      :quick-action-max="quickActionMax"
      @add="handleAdd"
      @remove="handleRemove"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
  import SortableJs from 'sortablejs';
  import type { ElRow } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    PlusCircleOutlined,
    AppstoreAddOutlined,
    LogOutlined,
    ShoppingOutlined,
    UserOutlined,
    ControlOutlined,
    CopyOutlined,
    TagOutlined,
    MailOutlined,
    MoreOutlined,
    EditOutlined
  } from '@/components/icons';
  import QuickActionPicker from './quick-action-picker.vue';
  import { useQuickActions } from '../quick-action/use-quick-actions';
  import type { QuickActionItem } from '../quick-action/types';

  defineOptions({
    components: {
      PlusCircleOutlined,
      AppstoreAddOutlined,
      LogOutlined,
      ShoppingOutlined,
      UserOutlined,
      ControlOutlined,
      CopyOutlined,
      TagOutlined,
      MailOutlined,
      MoreOutlined,
      EditOutlined,
      QuickActionPicker
    }
  });

  const {
    displayedItems,
    availableToAdd,
    pickerVisible,
    quickActionMax,
    initFromUser,
    addAction,
    removeAction,
    reorder,
    reset,
    openPicker
  } = useQuickActions();

  const menuItems = [
    {
      title: '管理快捷操作',
      command: 'manage',
      icon: EditOutlined
    }
  ];

  const selectedConfigs = computed(() =>
    displayedItems.value.map(({ to: _to, ...config }) => config)
  );

  const wrapRef = ref<InstanceType<typeof ElRow> | null>(null);
  let sortableIns: SortableJs | null = null;

  const setupSortable = () => {
    if (sortableIns) {
      sortableIns.destroy();
      sortableIns = null;
    }
    if (!wrapRef.value?.$el || !displayedItems.value.length) {
      return;
    }
    sortableIns = new SortableJs(wrapRef.value.$el, {
      animation: 300,
      delay: 150,
      delayOnTouchOnly: true,
      onUpdate: ({ oldIndex, newIndex }) => {
        if (typeof oldIndex === 'number' && typeof newIndex === 'number') {
          reorder(oldIndex, newIndex);
        }
      },
      setData: () => {}
    });
  };

  const handleMenuCommand = (command: string) => {
    if (command === 'manage') {
      openPicker();
    }
  };

  const getLinkProps = (item: QuickActionItem) => {
    if (item.type === 'external') {
      return {
        href: item.path,
        target: '_blank',
        rel: 'noopener noreferrer'
      };
    }
    return { to: item.to };
  };

  const handleAdd = (key: string) => {
    if (displayedItems.value.length >= quickActionMax) {
      EleMessage.warning({
        message: `最多添加 ${quickActionMax} 个快捷操作`,
        plain: true
      });
      return;
    }
    addAction(key);
    EleMessage.success({ message: '已添加', plain: true });
  };

  const handleRemove = (key: string) => {
    removeAction(key);
    EleMessage.success({ message: '已移除', plain: true });
  };

  onMounted(() => {
    initFromUser();
    nextTick(setupSortable);
  });

  watch(displayedItems, () => {
    nextTick(setupSortable);
  });

  onBeforeUnmount(() => {
    if (sortableIns) {
      sortableIns.destroy();
      sortableIns = null;
    }
  });

  defineExpose({ reset });
</script>

<style lang="scss" scoped>
  .quick-action-card-wrap {
    :deep(.ele-card-header) {
      padding: 14px 16px;
    }
  }

  .quick-action-more {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    font-size: 14px;
    border-radius: 6px;
    margin: 0 -10px 0 0;
    cursor: pointer;
    transition: all 0.2s;

    & > .el-icon {
      width: 26px;
      height: 26px;
    }

    &:hover {
      color: var(--el-text-color-regular);
      background: var(--el-fill-color-light);
    }
  }

  .quick-action-empty {
    padding: 8px 0 4px;
  }

  .quick-action-row {
    margin-bottom: -4px;
  }

  .quick-action-item {
    display: block;
    margin-bottom: 12px;
    padding: 14px 8px 12px;
    text-align: center;
    text-decoration: none;
    color: inherit;
    user-select: none;
    border-radius: 10px;
    border: 1px solid transparent;
    background: var(--el-fill-color-blank);
    transition:
      transform 0.22s ease,
      box-shadow 0.22s ease,
      border-color 0.22s ease,
      background-color 0.22s ease;

    &__icon {
      width: 48px;
      height: 48px;
      margin: 0 auto 10px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: color-mix(in srgb, var(--action-accent) 12%, transparent);
      transition:
        transform 0.22s ease,
        background-color 0.22s ease,
        box-shadow 0.22s ease;
    }

    &__icon-inner {
      font-size: 26px;
      color: var(--action-accent);

      :deep(svg) {
        stroke-width: 2.5;
      }
    }

    &__title {
      font-size: 13px;
      line-height: 1.4;
      color: var(--el-text-color-regular);
      transition: color 0.22s ease;
    }

    &:hover {
      transform: translateY(-2px);
      border-color: color-mix(in srgb, var(--action-accent) 28%, transparent);
      background: var(--el-bg-color);
      box-shadow:
        0 4px 12px rgba(0, 0, 0, 0.06),
        0 1px 3px rgba(0, 0, 0, 0.04);

      .quick-action-item__icon {
        transform: scale(1.06);
        background: color-mix(in srgb, var(--action-accent) 18%, transparent);
        box-shadow: 0 4px 10px color-mix(in srgb, var(--action-accent) 22%, transparent);
      }

      .quick-action-item__title {
        color: var(--el-text-color-primary);
      }
    }

    &:active {
      transform: translateY(0);
    }
  }

  .el-col.sortable-chosen .quick-action-item {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: var(--el-color-primary-light-7);
  }

  .el-col.sortable-ghost {
    opacity: 0.35;
  }

  .el-col.sortable-fallback .quick-action-item {
    opacity: 1 !important;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
  }
</style>
