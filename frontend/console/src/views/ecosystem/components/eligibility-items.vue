<!-- 免审白名单资格：逐条列出达标情况 -->
<template>
  <div class="eco-eligibility">
    <el-alert
      :type="data.eligible ? 'success' : 'info'"
      :closable="false"
      show-icon
      :title="
        data.summary ||
        (data.eligible ? '已满足自动准入条件' : '暂不满足自动准入条件')
      "
    />
    <ul class="eco-eligibility__list">
      <li
        v-for="item in data.items"
        :key="item.code"
        :class="{ 'is-failed': !item.passed }"
      >
        <el-icon v-if="item.passed" class="eco-eligibility__icon is-pass">
          <CircleCheckFilled />
        </el-icon>
        <el-icon v-else class="eco-eligibility__icon is-fail">
          <CircleCloseFilled />
        </el-icon>
        <span class="eco-eligibility__label">{{ item.label }}</span>
        <el-tag
          v-if="!item.passed && item.blocking"
          size="small"
          type="danger"
          :disable-transitions="true"
        >
          人工也不能绕
        </el-tag>
        <div v-if="item.detail" class="eco-eligibility__detail">
          {{ item.detail }}
        </div>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
  import {
    CircleCheckFilled,
    CircleCloseFilled
  } from '@element-plus/icons-vue';
  import type { AuditEligibility } from '@/api/ecosystem/audit/model';

  defineProps<{ data: AuditEligibility }>();
</script>

<style lang="scss" scoped>
  .eco-eligibility__list {
    margin: 10px 0 0;
    padding: 0;
    list-style: none;
  }

  .eco-eligibility__list > li {
    padding: 6px 0;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-regular);

    & + li {
      border-top: 1px solid var(--el-border-color-lighter);
    }

    &.is-failed .eco-eligibility__label {
      color: var(--el-text-color-primary);
    }
  }

  .eco-eligibility__icon {
    margin-right: 6px;
    vertical-align: -2px;

    &.is-pass {
      color: var(--el-color-success);
    }

    &.is-fail {
      color: var(--el-color-danger);
    }
  }

  .eco-eligibility__label {
    margin-right: 6px;
  }

  .eco-eligibility__detail {
    margin: 2px 0 0 22px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
