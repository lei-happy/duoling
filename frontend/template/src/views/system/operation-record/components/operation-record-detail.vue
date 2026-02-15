<!-- 详情弹窗 -->
<template>
  <el-descriptions
    v-if="data"
    :border="true"
    :column="mobile ? 1 : 2"
    class="detail-table"
  >
    <el-descriptions-item label="操作人">
      <div>{{ data.nickname }}({{ data.username }})</div>
    </el-descriptions-item>
    <el-descriptions-item label="IP地址">
      <div>{{ data.ip }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作模块">
      <div>{{ data.module }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作功能">
      <div>{{ data.description }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="操作时间">
      <div>{{ data.createTime }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求耗时">
      <div v-if="!isNaN(data.spendTime)">{{ data.spendTime / 1000 }}s</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求方式">
      <div>{{ data.requestMethod }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求状态">
      <el-tag
        v-if="data.status === 0"
        size="small"
        type="success"
        :disable-transitions="true"
      >
        正常
      </el-tag>
      <el-tag
        v-else-if="data.status === 1"
        size="small"
        type="danger"
        :disable-transitions="true"
      >
        异常
      </el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="请求地址" :span="2">
      <div style="word-break: break-all">{{ data.url }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="调用方法" :span="2">
      <div style="word-break: break-all">{{ data.method }}</div>
    </el-descriptions-item>
    <el-descriptions-item label="请求参数" :span="2">
      <ele-ellipsis :max-line="4" :tooltip="ellipsisTooltipProps">
        {{ data.params }}
      </ele-ellipsis>
    </el-descriptions-item>
    <el-descriptions-item v-if="data.status === 0" label="返回结果" :span="2">
      <ele-ellipsis :max-line="4" :tooltip="ellipsisTooltipProps">
        {{ data.result }}
      </ele-ellipsis>
    </el-descriptions-item>
    <el-descriptions-item v-else label="异常信息" :span="2">
      <ele-ellipsis :max-line="4" :tooltip="ellipsisTooltipProps">
        {{ data.error }}
      </ele-ellipsis>
    </el-descriptions-item>
  </el-descriptions>
</template>

<script lang="ts" setup>
  import { reactive } from 'vue';
  import type { EleTooltipProps } from 'ele-admin-plus/es/ele-app/plus';
  import type { OperationRecord } from '@/api/system/operation-record/model';
  import { useMobile } from '@/utils/use-mobile';

  defineProps<{
    /** 修改回显的数据 */
    data: OperationRecord;
  }>();

  /** 文字省略组件的提示组件的属性 */
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

  /** 是否是移动端 */
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
