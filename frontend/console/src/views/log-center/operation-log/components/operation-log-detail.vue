<!-- 详情弹窗 -->
<template>
  <el-descriptions
    v-if="data"
    :border="true"
    :column="mobile ? 1 : 2"
    class="detail-table"
  >
    <el-descriptions-item label="租户">
      <div>{{ tenantDisplayName }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="租户编码">
      <div>{{ data.tenantCode || '-' }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作用户">
      <div>{{ operatorDisplayName }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作模块">
      <div>{{ data.module }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作类型">
      <div>{{ data.action }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作描述">
      <div>{{ data.description }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="IP地址">
      <div>{{ data.ip }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作时间">
      <div>{{ formatDateTime(data.createdAt) }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求耗时">
      <div v-if="data.elapsedTime != null">{{ data.elapsedTime }}ms</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求方式">
      <div>{{ data.requestMethod }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求状态">
      <el-tag
        v-if="data.status === 1"
        size="small"
        type="success"
        :disable-transitions="true"
      >
        成功
      </el-tag>
      <el-tag
        v-else-if="data.status === 0"
        size="small"
        type="danger"
        :disable-transitions="true"
      >
        失败
      </el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="请求地址" :span="2">
      <div style="word-break: break-all">{{ data.requestUrl }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求参数" :span="2">
      <ele-ellipsis :max-line="4" :tooltip="ellipsisTooltipProps">
        {{ data.requestBody }}
      </ele-ellipsis>
    </el-descriptions-item>
    <el-descriptions-item label="响应结果" :span="2">
      <ele-ellipsis :max-line="4" :tooltip="ellipsisTooltipProps">
        {{ data.responseBody }}
      </ele-ellipsis>
    </el-descriptions-item>
  </el-descriptions>
</template>

<script lang="ts" setup>
  import { computed, reactive } from 'vue';
  import type { EleTooltipProps } from 'ele-admin-plus/es/ele-app/plus';
  import type { TenantOperationLog } from '@/api/log-center/model';
  import { formatDateTime } from '@/utils/date-util';
  import { useMobile } from '@/utils/use-mobile';

  const props = defineProps<{
    data: TenantOperationLog;
  }>();

  const tenantDisplayName = computed(() => {
    const name = props.data?.tenantShortName?.trim();
    if (name) return name;
    return props.data?.tenantCode?.trim() || '-';
  });

  const operatorDisplayName = computed(() => {
    const name = props.data?.realName?.trim();
    if (name) return name;
    return props.data?.username?.trim() || '-';
  });

  const ellipsisTooltipProps = reactive<EleTooltipProps>({
    popperStyle: {
      width: '580px',
      maxWidth: '90%',
      wordBreak: 'break-all'
    },
    bodyStyle: {
      maxWidth: 'calc(100vw - 32px)',
      maxHeight: '252px',
      overflowY: 'auto',
      '--ele-scrollbar-color': '#5e5e5e',
      '--ele-scrollbar-hover-color': '#707070',
      '--ele-scrollbar-size': '8px'
    },
    offset: 4,
    placement: 'top'
  });

  const { mobile } = useMobile();
</script>

<style lang="scss" scoped>
  .detail-table :deep(td.el-descriptions__label.el-descriptions__cell) {
    width: 88px;
    text-align: right;
    font-weight: normal;
  }

  .detail-table :deep(.el-descriptions__content > div) {
    max-height: 100%;
  }
</style>
