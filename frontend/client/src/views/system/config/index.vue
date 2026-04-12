<template>
  <ele-page :multi-card="false">
    <ele-card :body-style="{ padding: 0, overflow: 'hidden' }">
      <ele-split-panel
        space="0px"
        size="200px"
        :allow-collapse="mobile"
        v-model:collapse="sideCollapse"
        :custom-style="{
          borderWidth: '0 1px 0 0',
          padding: '10px 0',
          background: 'none'
        }"
        :body-style="{ padding: '16px 20px 20px 16px', overflow: 'hidden' }"
        :collapse-style="{ marginLeft: '4px' }"
        style="min-height: 480px; border-radius: var(--ele-card-radius)"
      >
        <ele-loading
          :loading="loading && !configs.length"
          :style="{ flex: '1', minHeight: '200px', padding: '0 0 8px 0' }"
        >
          <ele-menus
            v-if="menuItems.length"
            ref="menuRef"
            :items="menuItems"
            :default-active="activeGroup"
            class="config-side-menu"
            @select="handleMenuSelect"
          />
        </ele-loading>
        <template #body>
          <ele-loading :loading="loading">
            <transition name="slide-right" mode="out-in">
              <ele-card
                v-if="currentGroup"
                :key="currentGroup.name"
                class="config-group-card"
                :header="currentGroup.label"
                :header-style="configGroupCardHeaderStyle"
                :body-style="configGroupCardBodyStyle"
              >
                <component
                  :is="resolveGroupPanel(currentGroup.name)"
                  :items="currentGroup.items"
                  @config-change="handleChange"
                />
              </ele-card>
              <ele-card v-else-if="!loading" :body-style="{ padding: '40px' }">
                <el-empty description="暂无配置项" />
              </ele-card>
            </transition>
          </ele-loading>
        </template>
      </ele-split-panel>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import type { Component } from 'vue';
  import { ref, computed, watch, nextTick } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleMenusInstance } from 'ele-admin-plus/es/ele-app/plus';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import { listConfigs, updateConfig } from '@/api/system/config';
  import type { SystemConfig } from '@/api/system/config/model';
  import { useMobile } from '@/utils/use-mobile';
  import GenericGroupSettings from './components/generic-group-settings.vue';
  import WaybillSettings from './components/waybill-settings.vue';
  import { GROUP_LABELS } from './constants';

  defineOptions({ name: 'SystemConfig' });

  /** 与正文左右对齐，并收紧标题区上、左留白 */
  const configGroupCardHeaderStyle = {
    padding: '6px 16px 10px'
  };
  const configGroupCardBodyStyle = {
    padding: '10px 16px 16px'
  };

  const groupPanels: Record<string, Component> = {
    waybill: WaybillSettings
  };

  const resolveGroupPanel = (name: string) =>
    groupPanels[name] ?? GenericGroupSettings;

  const loading = ref(false);
  const configs = ref<SystemConfig[]>([]);
  const activeGroup = ref('');
  const menuRef = ref<EleMenusInstance>(null);
  const { mobile } = useMobile();
  const sideCollapse = ref(mobile.value);

  watch(
    mobile,
    (m) => {
      if (m) {
        sideCollapse.value = true;
      }
    },
    { immediate: true }
  );

  const groups = computed(() => {
    const map = new Map<string, SystemConfig[]>();
    for (const c of configs.value) {
      const g = c.configGroup || 'default';
      if (!map.has(g)) map.set(g, []);
      map.get(g)!.push(c);
    }
    return Array.from(map.entries()).map(([name, items]) => ({
      name,
      label: GROUP_LABELS[name] || name,
      items
    }));
  });

  const menuItems = computed<MenuItem[]>(() =>
    groups.value.map((g) => ({
      index: g.name,
      title: g.label
    }))
  );

  const currentGroup = computed(() =>
    groups.value.find((g) => g.name === activeGroup.value)
  );

  const handleMenuSelect = (index: string) => {
    activeGroup.value = index;
    if (mobile.value) {
      sideCollapse.value = true;
    }
  };

  watch(
    () => groups.value.map((g) => g.name),
    (names) => {
      if (!names.length) {
        activeGroup.value = '';
        return;
      }
      if (!names.includes(activeGroup.value)) {
        activeGroup.value = names[0];
      }
      nextTick(() => {
        menuRef.value?.updateActiveIndex?.(activeGroup.value);
        menuRef.value?.scrollToActive?.();
      });
    },
    { immediate: true }
  );

  const query = () => {
    loading.value = true;
    listConfigs()
      .then((data) => {
        configs.value = data ?? [];
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      })
      .finally(() => {
        loading.value = false;
      });
  };

  const handleChange = (item: SystemConfig, val: string) => {
    const oldValue = item.configValue;
    item.configValue = val;
    updateConfig(item.configKey, val)
      .then(() => {
        EleMessage.success({ message: '保存成功', plain: true });
      })
      .catch((e) => {
        item.configValue = oldValue;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  query();
</script>

<style scoped>
  .config-side-menu {
    width: 100%;
    background: none;
    border: none;
  }

  /* 标题与下方表单项共用同一水平起点，避免标题区默认 padding 过大 */
  .config-group-card :deep(.ele-card-title) {
    line-height: 1.35;
  }
</style>
