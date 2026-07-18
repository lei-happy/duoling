<template>
  <ele-page class="module-overview">
    <overview-hero
      :title="moduleTitle"
      :positioning="positioning"
      :description="config?.description"
      :illustration="config?.heroIllustration"
      :hero-icon="config?.heroIcon"
      :accent-color="config?.accentColor"
      :quick-actions="config?.quickActions"
      @navigate="navigate"
    />

    <section v-if="workflow?.length" class="overview-section">
      <div class="overview-section__head">
        <h3 class="overview-section__title">工作流程</h3>
        <span class="overview-section__hint">点击任一环节可直达对应功能</span>
      </div>
      <overview-workflow :steps="workflow" @navigate="navigate" />
    </section>

    <section v-if="moduleCards.length" class="overview-section">
      <div class="overview-section__head">
        <h3 class="overview-section__title">模块导航</h3>
        <span class="overview-section__hint">
          共 {{ moduleCards.length }} 个子模块
        </span>
      </div>
      <overview-module-grid :cards="moduleCards" @navigate="navigate" />
    </section>

    <section v-if="tips?.length" class="overview-section overview-tips">
      <div class="overview-section__head">
        <h3 class="overview-section__title">使用提示</h3>
      </div>
      <ul class="overview-tips__list">
        <li v-for="(tip, index) in tips" :key="index">{{ tip }}</li>
      </ul>
    </section>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
  import { useUserStore } from '@/store/modules/user';
  import { resolveOverviewConfig } from '@/config/module-overview';
  import type { OverviewModuleCard } from '@/config/module-overview/types';
  import OverviewHero from './components/overview-hero.vue';
  import OverviewWorkflow from './components/overview-workflow.vue';
  import OverviewModuleGrid from './components/overview-module-grid.vue';

  defineOptions({ name: 'ModuleOverview' });

  const route = useRoute();
  const router = useRouter();
  const userStore = useUserStore();

  /** 当前模块 key：优先取注入的 meta.overviewModule，兜底从路径解析 */
  const moduleKey = computed(() => {
    const metaKey = route.meta?.overviewModule as string | undefined;
    if (metaKey) {
      return metaKey;
    }
    return route.path.replace(/^\//, '').replace(/\/overview$/, '');
  });

  /** 当前模块在菜单中的一级节点 */
  const moduleNode = computed<MenuItem | undefined>(() => {
    const modulePath = `/${moduleKey.value}`;
    return (userStore.menus ?? []).find((m) => m.path === modulePath);
  });

  /** 模块总览配置 */
  const config = computed(() => resolveOverviewConfig(moduleKey.value));

  const moduleTitle = computed(
    () => config.value?.title || moduleNode.value?.meta?.title || '模块总览'
  );

  const positioning = computed(
    () =>
      config.value?.positioning ||
      `${moduleTitle.value}集中管理本模块的各项功能，可从下方模块导航快速进入。`
  );

  const workflow = computed(() => config.value?.workflow);
  const tips = computed(() => config.value?.tips);

  /** 子模块卡片：主体来自真实菜单 children，文案/图标由配置补充 */
  const moduleCards = computed<OverviewModuleCard[]>(() => {
    const children = moduleNode.value?.children ?? [];
    const overrides = config.value?.moduleCards ?? [];
    return children
      .filter(
        (child) =>
          !!child.path &&
          child.path !== route.path &&
          !child.meta?.hide &&
          !child.meta?.overviewModule
      )
      .map((child) => {
        const override = overrides.find((o) => o.path === child.path);
        return {
          title: child.meta?.title,
          desc: override?.desc,
          icon: override?.icon || 'default',
          path: child.redirect || child.path
        };
      });
  });

  const navigate = (path: string) => {
    if (path) {
      router.push(path).catch(() => {});
    }
  };
</script>

<style lang="scss" scoped>
  .module-overview {
    :deep(.overview-section) + .overview-section {
      margin-top: 16px;
    }
  }

  .overview-section {
    margin-top: 16px;
    padding: 20px 24px;
    border-radius: 12px;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
  }

  .overview-section__head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
  }

  .overview-section__title {
    position: relative;
    margin: 0;
    padding-left: 12px;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 15px;
      border-radius: 2px;
      background: var(--el-color-primary);
    }
  }

  .overview-section__hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .overview-tips__list {
    margin: 0;
    padding-left: 20px;
    color: var(--el-text-color-regular);

    li {
      line-height: 2;
      font-size: 13px;
    }
  }
</style>
