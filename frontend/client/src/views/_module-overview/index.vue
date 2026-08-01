<template>
  <ele-page class="module-overview">
    <overview-hero
      :title="moduleTitle"
      :positioning="positioning"
      :description="config?.description"
      :illustration="config?.heroIllustration"
      :aspect-ratio="config?.heroAspectRatio"
      :hero-icon="config?.heroIcon"
      :accent-color="config?.accentColor"
    />

    <section class="overview-pref">
      <div class="overview-pref__row">
        <div class="overview-pref__text">
          <div class="overview-pref__title">下次进入本模块时先打开总览</div>
          <div class="overview-pref__hint">
            仅影响当前模块；关闭后进入本模块会直达第一个业务页，需要时仍可在侧栏打开总览
          </div>
        </div>
        <el-switch
          v-model="showOverview"
          :disabled="prefSaving"
          @change="onShowOverviewChange"
        />
      </div>
    </section>

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
  import { computed, ref, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
  import { useUserStore } from '@/store/modules/user';
  import { saveWorkplaceConfigNow } from '@/api/home/workbench/quick-action';
  import { resolveOverviewConfig } from '@/config/module-overview';
  import type { OverviewModuleCard } from '@/config/module-overview/types';
  import {
    applyModuleOverviewRedirectPreference,
    syncRouterModuleRedirects
  } from '@/utils/menu-util';
  import {
    isShowModuleOverviewEnabled,
    setModuleOverviewPreference
  } from '@/utils/workplace-config';
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
    return route.path.replace(/^\//, '').replace(/\/overview(-home)?$/, '');
  });

  const showOverview = ref(
    isShowModuleOverviewEnabled(
      userStore.info?.workplaceConfig,
      moduleKey.value
    )
  );
  const prefSaving = ref(false);

  watch(
    [() => userStore.info?.workplaceConfig, moduleKey],
    ([config, key]) => {
      if (prefSaving.value) {
        return;
      }
      showOverview.value = isShowModuleOverviewEnabled(config, key);
    }
  );

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

  const onShowOverviewChange = async (value: string | number | boolean) => {
    const next = value === true;
    const prev = !next;
    const key = moduleKey.value;
    prefSaving.value = true;
    const configToSave = setModuleOverviewPreference(
      userStore.info?.workplaceConfig,
      key,
      next
    );
    try {
      await saveWorkplaceConfigNow(configToSave);
      if (userStore.info) {
        userStore.info.workplaceConfig = configToSave;
      }
      applyModuleOverviewRedirectPreference(userStore.menus, (module) =>
        isShowModuleOverviewEnabled(configToSave, module)
      );
      syncRouterModuleRedirects(userStore.menus, router);
      EleMessage.success({ message: '已记住你对本模块的选择', plain: true });
    } catch (e: any) {
      showOverview.value = prev;
      EleMessage.error({
        message: e?.message || '保存失败，请稍后重试',
        plain: true
      });
    } finally {
      prefSaving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .module-overview {
    :deep(.overview-section) + .overview-section {
      margin-top: 16px;
    }
  }

  .overview-pref {
    margin-top: 12px;
    padding: 14px 20px;
    border-radius: 12px;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
  }

  .overview-pref__row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }

  .overview-pref__text {
    min-width: 0;
  }

  .overview-pref__title {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    line-height: 1.4;
  }

  .overview-pref__hint {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
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
