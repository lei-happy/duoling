<!--
  发布方标识：名字 + 认证标 + 信誉

  卡片上必须回答「这家靠不靠谱」，否则用户没有判断依据，只能全部点开看。
  信誉数据在样本不足时后端不下发数字，这里对应显示「新加入」而不是 0%。
-->
<template>
  <div class="eco-tenant">
    <div class="eco-tenant__name-line">
      <span class="eco-tenant__name">{{ displayName }}</span>
      <el-tag
        v-if="verified"
        size="small"
        type="success"
        effect="plain"
        :disable-transitions="true"
      >
        已认证
      </el-tag>
      <el-tag
        v-else-if="showNewcomer"
        size="small"
        type="info"
        effect="plain"
        :disable-transitions="true"
      >
        新加入
      </el-tag>
    </div>
    <div class="eco-tenant__credit">{{ creditText }}</div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { EcoCredit } from '@/api/ecosystem/hall/model';

  const props = withDefaults(
    defineProps<{
      /** 企业全称，按挂牌的可见范围可能为空 */
      tenantName?: string | null;
      /** 脱敏名，所有层级都有 */
      maskedName?: string | null;
      credit?: EcoCredit | null;
      /** 是否已完成企业认证。列表接口没有单独字段时用信誉块兜底 */
      verified?: boolean;
    }>(),
    { verified: false }
  );

  const displayName = computed(
    () => props.tenantName || props.maskedName || '同行企业'
  );

  const showNewcomer = computed(() => !!props.credit?.isNewcomer);

  /**
   * 信誉一行说清三件事：做过多少单、评价多少分、多久回消息
   *
   * 响应速度对撮合尤其重要——报价再合适，对方三天不回也没用。
   */
  const creditText = computed(() => {
    const c = props.credit;
    if (!c) {
      return '还没有合作记录';
    }
    const parts: string[] = [];
    if (c.dealCompletedCount) {
      parts.push(`已完成 ${c.dealCompletedCount} 单`);
    }
    if (c.avgScore != null) {
      parts.push(`评分 ${c.avgScore.toFixed(1)}`);
    }
    if (c.completeRate != null) {
      parts.push(`完成率 ${Math.round(c.completeRate)}%`);
    }
    if (c.avgRespondMinutes != null && c.avgRespondMinutes > 0) {
      const minutes = c.avgRespondMinutes;
      parts.push(
        minutes < 60
          ? `${Math.round(minutes)} 分钟内回复`
          : `${Math.max(1, Math.round(minutes / 60))} 小时内回复`
      );
    }
    return parts.length ? parts.join(' · ') : '还没有合作记录';
  });
</script>

<style lang="scss" scoped>
  .eco-tenant__name-line {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
  }

  .eco-tenant__name {
    font-size: 13px;
    color: var(--el-text-color-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .eco-tenant__credit {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
