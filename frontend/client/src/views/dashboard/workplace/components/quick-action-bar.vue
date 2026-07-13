<!-- 快捷操作 -->
<template>
  <ele-card
    shadow="never"
    class="quick-card"
    :body-style="{ padding: '0 20px 14px' }"
  >
    <template #header>
      <div class="quick-header">
        <span class="quick-title">快捷操作</span>
      </div>
    </template>
    <el-row :gutter="8" ref="wrapRef" class="quick-action-row">
      <el-col
        v-for="item in displayedItems"
        :key="item.key"
        :md="3"
        :sm="6"
        :xs="8"
        class="quick-action-sortable"
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
            <img
              v-if="item.image"
              :src="item.image"
              :alt="item.title"
              class="quick-action-item__img"
            />
            <el-icon v-else class="quick-action-item__icon-inner">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <div class="quick-action-item__title">{{ item.title }}</div>
        </component>
      </el-col>
      <el-col :md="3" :sm="6" :xs="8">
        <div
          class="quick-action-item quick-action-manage"
          role="button"
          tabindex="0"
          @click="openPicker"
          @keydown.enter="openPicker"
        >
          <div class="quick-action-item__icon">
            <el-icon class="quick-action-item__icon-inner">
              <EditOutlined />
            </el-icon>
          </div>
          <div class="quick-action-item__title">管理</div>
        </div>
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
      draggable: '.quick-action-sortable',
      onUpdate: ({ oldIndex, newIndex }) => {
        if (typeof oldIndex === 'number' && typeof newIndex === 'number') {
          reorder(oldIndex, newIndex);
        }
      },
      setData: () => {}
    });
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
  .quick-card {
    border-radius: 12px;
    height: 190px;
    display: flex;
    flex-direction: column;

    /* 移除标题下分割线 */
    :deep(.ele-card-header) {
      border-bottom: none;
    }

    /* body 撑满并使图标+文字整体垂直居中 */
    :deep(.ele-card-body) {
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
  }

  .quick-header {
    display: flex;
    align-items: center;
  }

  .quick-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .quick-action-row {
    width: 100%;
  }

  .quick-action-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 4px;
    text-align: center;
    text-decoration: none;
    color: inherit;
    user-select: none;
    border-radius: 10px;
    transition:
      transform 0.22s ease,
      background-color 0.22s ease;

    &__icon {
      width: 50px;
      height: 50px;
      margin-bottom: 8px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      background: linear-gradient(
        135deg,
        color-mix(in srgb, var(--action-accent) 92%, white) 0%,
        var(--action-accent) 100%
      );
      box-shadow: 0 6px 14px
        color-mix(in srgb, var(--action-accent) 32%, transparent);
      transition:
        transform 0.22s ease,
        box-shadow 0.22s ease;
    }

    &__img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    &__icon-inner {
      font-size: 26px;
      color: #fff;

      :deep(svg) {
        stroke-width: 2.2;
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

      .quick-action-item__icon {
        transform: scale(1.05);
        box-shadow: 0 8px 18px
          color-mix(in srgb, var(--action-accent) 42%, transparent);
      }

      .quick-action-item__title {
        color: var(--el-text-color-primary);
      }
    }

    &:active {
      transform: translateY(0);
    }
  }

  .quick-action-manage {
    cursor: pointer;
    --action-accent: var(--el-text-color-placeholder);

    .quick-action-item__icon {
      background: var(--el-fill-color-light);
      box-shadow: none;
    }

    .quick-action-item__icon-inner {
      color: var(--el-text-color-secondary);
    }

    &:hover {
      .quick-action-item__icon {
        background: var(--el-fill-color);
        box-shadow: none;
      }

      .quick-action-item__icon-inner {
        color: var(--el-text-color-regular);
      }
    }
  }

  .el-col.sortable-chosen .quick-action-item {
    background: var(--el-fill-color-light);
  }

  .el-col.sortable-ghost {
    opacity: 0.35;
  }

  .el-col.sortable-fallback .quick-action-item {
    opacity: 1 !important;
  }
</style>
