<!-- 线路主视觉：起点 → 终点。大厅卡片上第一眼看的就是这一块 -->
<template>
  <div class="eco-route" :class="{ 'is-compact': compact }">
    <div class="eco-route__end">
      <div class="eco-route__city">{{ fromCity || fromProvince || '—' }}</div>
      <div v-if="fromDetail" class="eco-route__detail">{{ fromDetail }}</div>
    </div>
    <div class="eco-route__arrow">
      <span class="eco-route__line"></span>
      <span v-if="mileage" class="eco-route__mileage">{{ mileage }}</span>
    </div>
    <div class="eco-route__end is-to">
      <div class="eco-route__city">{{ toText }}</div>
      <div v-if="toDetail" class="eco-route__detail">{{ toDetail }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';

  const props = withDefaults(
    defineProps<{
      fromProvince?: string | null;
      fromCity?: string | null;
      fromDistrict?: string | null;
      fromName?: string | null;
      toProvince?: string | null;
      toCity?: string | null;
      toDistrict?: string | null;
      toName?: string | null;
      /** 1-接受任意流向（运力挂牌常用） */
      anyDirection?: number;
      /** 运力的多个期望流向 */
      destinations?: { province?: string; city?: string }[];
      /** 参考里程，有就标在箭头上 */
      referenceMileage?: number | null;
      compact?: boolean;
    }>(),
    { compact: false }
  );

  /**
   * 终点文案
   *
   * 运力挂牌的终点常常不是一个点：可能接受任意流向，也可能填了三五个期望城市。
   * 这里按「任意流向 > 多目的地 > 单一终点」降级，不让界面出现空白箭头。
   */
  const toText = computed(() => {
    if (props.anyDirection) {
      return '任意流向';
    }
    const dests = props.destinations ?? [];
    if (dests.length > 1) {
      const first = dests[0]?.city || dests[0]?.province || '';
      return `${first} 等 ${dests.length} 地`;
    }
    if (dests.length === 1) {
      return dests[0]?.city || dests[0]?.province || '—';
    }
    return props.toCity || props.toProvince || '—';
  });

  const fromDetail = computed(
    () => props.fromName || props.fromDistrict || props.fromProvince || ''
  );

  const toDetail = computed(() => {
    if (props.anyDirection) {
      return '哪边有货都行';
    }
    const dests = props.destinations ?? [];
    if (dests.length > 1) {
      return dests
        .slice(0, 3)
        .map((d) => d.city || d.province)
        .filter(Boolean)
        .join('、');
    }
    return props.toName || props.toDistrict || props.toProvince || '';
  });

  const mileage = computed(() =>
    props.referenceMileage ? `${Math.round(props.referenceMileage)} km` : ''
  );
</script>

<style lang="scss" scoped>
  .eco-route {
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }

  .eco-route__end {
    flex: 0 1 auto;
    min-width: 0;
  }

  .eco-route__end.is-to {
    text-align: right;
  }

  .eco-route__city {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--el-text-color-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .eco-route__detail {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .eco-route__arrow {
    flex: 1 1 auto;
    min-width: 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 11px;
  }

  .eco-route__line {
    position: relative;
    display: block;
    width: 100%;
    height: 1px;
    background: var(--el-border-color);

    &::after {
      content: '';
      position: absolute;
      right: 0;
      top: -3px;
      width: 6px;
      height: 6px;
      border-top: 1px solid var(--el-border-color-darker);
      border-right: 1px solid var(--el-border-color-darker);
      transform: rotate(45deg);
    }
  }

  .eco-route__mileage {
    margin-top: 2px;
    font-size: 11px;
    line-height: 1.4;
    color: var(--el-text-color-placeholder);
  }

  .eco-route.is-compact {
    .eco-route__city {
      font-size: 15px;
    }
    .eco-route__arrow {
      padding-top: 9px;
    }
  }
</style>
