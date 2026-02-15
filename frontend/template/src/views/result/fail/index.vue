<template>
  <ele-page :multi-card="false">
    <ele-card :body-style="{ paddingLeft: '12px', paddingRight: '12px' }">
      <el-result icon="error" title="提交失败">
        <template #sub-title>
          <ele-text type="placeholder">
            请核对并修改以下信息后，再重新提交。
          </ele-text>
        </template>
      </el-result>
      <div style="text-align: center">
        <el-button type="primary">返回修改</el-button>
        <el-button>重新提交</el-button>
      </div>
      <div
        style="
          max-width: 760px;
          padding: 18px 24px;
          background: hsla(0, 0%, 60%, 0.1);
          border-radius: var(--el-border-radius-base);
          margin: 26px auto;
        "
      >
        <div>您提交的内容有如下错误:</div>
        <div style="margin-top: 12px">
          <ele-text type="danger" :icon="CloseCircleOutlined" tag="span" />
          <span>&nbsp;您的账户已被冻结&nbsp;</span>
          <el-link
            type="primary"
            underline="never"
            style="display: inline; vertical-align: 0"
          >
            <span>立即解冻</span>
            <el-icon :size="14">
              <ArrowRight />
            </el-icon>
          </el-link>
        </div>
        <div style="margin-top: 12px">
          <ele-text type="danger" :icon="CloseCircleOutlined" tag="span" />
          <span>&nbsp;您的账户还不具备申请资格&nbsp;</span>
          <el-link
            type="primary"
            underline="never"
            style="display: inline; vertical-align: 0"
          >
            <span>立即升级</span>
            <el-icon :size="14">
              <ArrowRight />
            </el-icon>
          </el-link>
        </div>
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { CloseCircleOutlined, ArrowRight } from '@/components/icons';

  defineOptions({ name: 'ResultFail' });
</script>
