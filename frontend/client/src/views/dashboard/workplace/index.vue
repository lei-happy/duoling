<template>
  <ele-page class="workplace-page">
    <profile-card />
    <link-card ref="linkCardRef" />
    <el-row :gutter="16" ref="wrapRef">
      <el-col
        v-for="(item, index) in data"
        :key="item.name"
        :md="item.md"
        :sm="item.sm"
        :xs="item.xs"
      >
        <component
          :is="item.name"
          :title="item.title"
          @command="(command: Command) => handleCommand(command, index)"
        />
      </el-col>
    </el-row>
    <ele-card :body-style="{ padding: 0 }" style="overflow: hidden">
      <div class="workplace-bottom">
        <el-link
          type="primary"
          :icon="PlusCircleOutlined"
          underline="never"
          class="workplace-button"
          @click="add"
        >
          添加卡片
        </el-link>
        <el-divider direction="vertical" style="margin: 0" />
        <el-link
          type="primary"
          :icon="UndoOutlined"
          underline="never"
          class="workplace-button"
          @click="reset"
        >
          重置布局
        </el-link>
      </div>
    </ele-card>
    <!-- 添加卡片弹窗 -->
    <ele-modal :width="680" v-model="visible" title="未添加的卡片">
      <el-row :gutter="16" style="margin-top: -16px">
        <el-col
          v-for="item in notAddedData"
          :key="item.name"
          :md="8"
          :sm="12"
          :xs="24"
        >
          <ele-card
            bordered
            :header="item.title"
            :header-style="{ padding: '8px 14px', fontSize: '14px' }"
            :body-style="{ padding: '32px 0', textAlign: 'center' }"
            style="margin-top: 16px"
          >
            <el-button
              plain
              round
              size="small"
              type="primary"
              @click="addView(item)"
            >
              添加
            </el-button>
          </ele-card>
        </el-col>
      </el-row>
      <el-empty
        v-if="!notAddedData.length"
        description="已添加所有视图"
        :image-size="80"
      />
    </ele-modal>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
  import SortableJs from 'sortablejs';
  import type { ElRow } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { PlusCircleOutlined, UndoOutlined } from '@/components/icons';
  import ProfileCard from './components/profile-card.vue';
  import LinkCard from './components/link-card.vue';
  import type { Command } from './model';
  import ActivitiesCard from './components/activities-card.vue';
  import TodoCard from './components/todo-card.vue';

  defineOptions({
    name: 'DashboardWorkplace',
    components: {
      ActivitiesCard,
      TodoCard
    }
  });

  /** 版本号：用于在默认布局变更后让用户重新套用 DEFAULT */
  const CACHE_KEY = 'workplace-layout-v4';

  interface ViewItem {
    name: string;
    title: string;
    md: number;
    sm: number;
    xs: number;
  }

  /** 默认布局（与产品示意一致：待办 + 最新动态；其他类型后续按需加入 DEFAULT） */
  const DEFAULT: ViewItem[] = [
    {
      name: 'todo-card',
      title: '我的待办',
      md: 16,
      sm: 24,
      xs: 24
    },
    {
      name: 'activities-card',
      title: '最新动态',
      md: 8,
      sm: 24,
      xs: 24
    }
  ];

  /** 获取缓存的数据（顺序以缓存为准，但合并 DEFAULT 中的栅格与标题；待办卡片固定置顶） */
  const getCacheData = (): ViewItem[] => {
    const cache = localStorage.getItem(CACHE_KEY);
    try {
      const temp: ViewItem[] | null = cache ? JSON.parse(cache) : null;
      if (temp?.length) {
        const order = temp.map((t) => t.name);
        const data: ViewItem[] = [];
        for (const name of order) {
          const def = DEFAULT.find((d) => d.name === name);
          if (def) {
            data.push({ ...def });
          }
        }
        const todoIdx = data.findIndex((d) => d.name === 'todo-card');
        if (todoIdx > 0) {
          const [t] = data.splice(todoIdx, 1);
          data.unshift(t);
        }
        return data.length ? data : [...DEFAULT];
      }
    } catch (e) {
      console.error(e);
    }
    return [...DEFAULT];
  };

  /** 卡片数据 */
  const data = ref<ViewItem[]>(getCacheData());

  /** 弹窗是否打开 */
  const visible = ref(false);

  /** 快捷方式卡片 */
  const linkCardRef = ref<InstanceType<typeof LinkCard> | null>(null);

  /** 容器 */
  const wrapRef = ref<InstanceType<typeof ElRow> | null>(null);

  /** 拖拽排序实例 */
  let sortableIns: SortableJs | null = null;

  /** 未添加的数据 */
  const notAddedData = computed(() => {
    return DEFAULT.filter((d) => !data.value.some((t) => t.name === d.name));
  });

  /** 添加 */
  const add = () => {
    visible.value = true;
  };

  /** 重置布局 */
  const reset = () => {
    data.value = [...DEFAULT];
    cacheData();
    linkCardRef.value?.reset?.();
    EleMessage.success({ message: '已重置', plain: true });
  };

  /** 缓存布局 */
  const cacheData = () => {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data.value));
  };

  /** 编辑卡片 */
  const handleCommand = (command: Command, index: number) => {
    switch (command) {
      case 'refresh': // 刷新
        EleMessage.info({ message: '点击了刷新', plain: true });
        break;
      case 'edit': // 编辑
        EleMessage.info({ message: '点击了编辑', plain: true });
        break;
      case 'remove': // 删除
        ElMessageBox.confirm(
          `确定要删除“${data.value[index].title}”卡片吗?`,
          '系统提示',
          { type: 'warning', draggable: true }
        )
          .then(() => {
            data.value = data.value.filter((_d, i) => i !== index);
            cacheData();
          })
          .catch(() => {});
        break;
    }
  };

  /** 添加视图 */
  const addView = (item: ViewItem) => {
    data.value.push(item);
    cacheData();
    EleMessage.success({ message: '已添加', plain: true });
  };

  onMounted(() => {
    // 卡片支持拖动排序
    sortableIns = new SortableJs(wrapRef.value?.$el, {
      handle: '.ele-card-header',
      filter: '.demo-more-icon',
      animation: 300,
      delay: 150,
      delayOnTouchOnly: true,
      onUpdate: ({ oldIndex, newIndex }) => {
        if (typeof oldIndex === 'number' && typeof newIndex === 'number') {
          const temp = [...data.value];
          temp.splice(newIndex, 0, temp.splice(oldIndex, 1)[0]);
          data.value = temp;
          cacheData();
        }
      },
      setData: () => {},
      forceFallback: true
    });
  });

  onBeforeUnmount(() => {
    sortableIns && sortableIns.destroy();
    sortableIns = null;
  });
</script>

<style lang="scss" scoped>
  .workplace-page {
    :deep(.ele-card-header) {
      user-select: none;
      cursor: move;
    }

    :deep(.el-col) {
      &.sortable-chosen > .ele-card {
        box-shadow: 0 2px 16px 0 rgba(0, 0, 0, 0.2);
      }

      &.sortable-ghost {
        opacity: 0;
      }

      &.sortable-fallback {
        opacity: 1 !important;
      }
    }
  }

  /* 底部按钮 */
  .workplace-bottom {
    display: flex;
    align-items: center;

    .workplace-button {
      flex: 1;
      padding: 10px 0;
      transition: background-color 0.2s;

      &:hover {
        background: hsla(0, 0%, 60%, 0.05);
      }

      :deep(.el-icon) {
        font-size: 15px;
        margin: -1px 6px 0 0;
      }
    }
  }
</style>
