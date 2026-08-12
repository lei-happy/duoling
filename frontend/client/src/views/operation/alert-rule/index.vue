<!--
  预警规则配置

  两个视图对应阈值三层模型的后两层：
    默认阈值 = 全公司通用的那把尺子（覆盖代码里的系统默认值）
    覆盖规则 = 按客户 / 线路 / 里程 / 车型 / 承运方式划出的例外

  改动落到 biz_task_alert_rule，下一轮预警计算即生效，无需重启服务。
-->
<template>
  <ele-page>
    <ele-card :body-style="{ padding: '18px 20px 12px' }">
      <div class="alert-rule-page">
        <header class="alert-rule-page__head">
          <div
            class="alert-rule-page__seg"
            role="tablist"
            aria-label="预警规则视图"
          >
            <button
              type="button"
              role="tab"
              class="alert-rule-page__seg-btn"
              :class="{ 'is-active': activeTab === 'defaults' }"
              :aria-selected="activeTab === 'defaults'"
              @click="activeTab = 'defaults'"
            >
              默认阈值
            </button>
            <button
              type="button"
              role="tab"
              class="alert-rule-page__seg-btn"
              :class="{ 'is-active': activeTab === 'overrides' }"
              :aria-selected="activeTab === 'overrides'"
              @click="activeTab = 'overrides'"
            >
              覆盖规则
            </button>
          </div>
          <p class="alert-rule-page__lead">
            {{
              activeTab === 'defaults'
                ? '全公司通用的阈值。改完下一轮扫描即生效。想给某个客户单独放宽或收紧，切到「覆盖规则」。'
                : '给某个客户、某条线路或某种车单独放宽或收紧。没配覆盖时，全部任务都走默认阈值。'
            }}
          </p>
        </header>

        <div class="alert-rule-page__body">
          <rule-defaults
            v-if="loadedTabs.has('defaults')"
            v-show="activeTab === 'defaults'"
          />
          <rule-overrides
            v-if="loadedTabs.has('overrides')"
            v-show="activeTab === 'overrides'"
          />
        </div>
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import RuleDefaults from './components/rule-defaults.vue';
  import RuleOverrides from './components/rule-overrides.vue';

  defineOptions({ name: 'OperationAlertRule' });

  const activeTab = ref('defaults');
  /** 懒加载：没点开的 Tab 不发请求 */
  const loadedTabs = ref(new Set<string>(['defaults']));

  watch(activeTab, (tab) => {
    loadedTabs.value.add(tab);
    loadedTabs.value = new Set(loadedTabs.value);
  });
</script>

<style lang="scss" scoped>
  .alert-rule-page {
    &__head {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
    }

    &__seg {
      display: inline-flex;
      padding: 3px;
      border-radius: 10px;
      background: var(--el-fill-color);
    }

    &__seg-btn {
      margin: 0;
      padding: 6px 14px;
      border: none;
      border-radius: 8px;
      background: transparent;
      color: var(--el-text-color-regular);
      font-size: 13px;
      font-weight: 500;
      line-height: 1.3;
      cursor: pointer;
      transition:
        background 140ms ease,
        color 140ms ease,
        box-shadow 140ms ease,
        transform 100ms ease-out;

      &.is-active {
        background: var(--el-bg-color);
        color: var(--el-text-color-primary);
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1);
      }

      &:hover:not(.is-active) {
        color: var(--el-text-color-primary);
      }

      &:active {
        transform: scale(0.97);
      }

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: 1px;
      }
    }

    &__lead {
      margin: 0;
      font-size: 13px;
      line-height: 1.6;
      color: var(--el-text-color-secondary);
    }

    &__body {
      padding: 12px 0 8px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .alert-rule-page__seg-btn {
      transition: none;
    }
  }
</style>
