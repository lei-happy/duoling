<template>
  <ele-page>
    <ele-card>
      <el-result
        icon="info"
        title="应付管理"
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
              <li>应付账单自动生成</li>
              <li>付款登记与核销</li>
              <li>驾驶员运费结算</li>
              <li>应付账龄分析</li>
            </ul>
          </div>
        </template>
      </el-result>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  defineOptions({ name: 'FinancePayable' });
</script>
