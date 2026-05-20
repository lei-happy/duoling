<template>
  <ele-page>
    <ele-card>
      <el-result
        icon="info"
        title="财务对账"
        sub-title="该功能模块正在开发中，敬请期待"
      >
        <template #extra>
          <div
            style="
              color: var(--el-text-color-secondary);
              line-height: 1.8;
              text-align: left;
              max-width: 400px;
              margin: 0 auto;
            "
          >
            <p>规划功能：</p>
            <ul>
              <li>应收应付对账</li>
              <li>差异分析与调整</li>
              <li>对账单导出</li>
              <li>发票管理</li>
            </ul>
          </div>
        </template>
      </el-result>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  defineOptions({ name: 'FinanceReconciliation' });
</script>
