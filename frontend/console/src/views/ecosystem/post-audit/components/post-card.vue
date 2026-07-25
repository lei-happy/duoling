<!--
  审核队列的一张挂牌卡片

  按 04 §2.5：一屏能看完一条挂牌的关键信息，正常情况下不用点进详情就能下结论。
  所以线路、时间窗、台数、报价、发布方、预检标记都直接铺在卡上，
  详情只留给需要核对联系方式、车辆证照、历史流水的那少数几条。
-->
<template>
  <div
    class="eco-post-card"
    :class="[
      `is-urgency-${row.urgency}`,
      { 'is-active': active, 'is-selected': selected }
    ]"
    @click="emit('focus')"
  >
    <div class="eco-post-card__head">
      <el-checkbox
        v-if="selectable"
        :model-value="selected"
        @click.stop
        @change="(v: any) => emit('update:selected', !!v)"
      />
      <el-tag
        size="small"
        :disable-transitions="true"
        :type="row.post.postType === 1 ? 'warning' : 'success'"
      >
        {{ row.post.postTypeLabel }}
      </el-tag>
      <span class="eco-post-card__title">{{ row.post.title }}</span>
      <el-tag size="small" :disable-transitions="true" type="info">
        {{ row.post.statusLabel }}
      </el-tag>
      <el-tag
        v-if="showAuditStatus"
        size="small"
        :disable-transitions="true"
        type="info"
      >
        {{ row.post.auditStatusLabel }}
      </el-tag>
      <el-tag
        size="small"
        :disable-transitions="true"
        :type="urgencyTagType"
        class="eco-post-card__urgency"
      >
        {{ waitedText }}
      </el-tag>
    </div>

    <div class="eco-post-card__facts">
      <span class="eco-post-card__route">{{ routeText }}</span>
      <span>{{ windowText }}</span>
      <span>{{ quantityText }}</span>
      <span>{{ priceText }}</span>
    </div>

    <div class="eco-post-card__meta">
      <span>
        {{ row.post.ownerTenantName || row.post.ownerTenantCode }}
        <template v-if="row.post.publisherName">
          · {{ row.post.publisherName }}
        </template>
      </span>
      <span>{{ sourceText }}</span>
      <span>{{ row.post.postNo }}</span>
      <span v-if="row.post.submittedAt">进队 {{ row.post.submittedAt }}</span>
      <span v-if="mode === 'spot' && row.post.listedAt">
        上架 {{ row.post.listedAt }}
      </span>
    </div>

    <div
      v-if="flags.length || row.post.sourceChanged === 1"
      class="eco-post-card__flags"
    >
      <el-tag
        v-if="row.post.sourceChanged === 1"
        size="small"
        type="danger"
        :disable-transitions="true"
      >
        来源单据发布后被改过
      </el-tag>
      <el-tag
        v-for="f in flags"
        :key="f.code"
        size="small"
        type="warning"
        :disable-transitions="true"
      >
        {{ f.label }}
      </el-tag>
    </div>

    <div v-if="row.post.auditReason" class="eco-post-card__reason">
      上一轮驳回：{{ row.post.auditReason }}
    </div>

    <div class="eco-post-card__actions" @click.stop>
      <template v-if="mode === 'pending'">
        <el-button type="primary" size="small" @click="emit('approve')">
          通过
        </el-button>
        <el-button type="danger" size="small" plain @click="emit('reject')">
          驳回
        </el-button>
      </template>
      <template v-else-if="mode === 'spot'">
        <el-button type="primary" size="small" @click="emit('spot-pass')">
          抽检通过
        </el-button>
        <el-button type="danger" size="small" plain @click="emit('spot-fail')">
          抽检不通过
        </el-button>
      </template>
      <template v-else>
        <el-button
          v-if="canForceDelist"
          type="danger"
          size="small"
          plain
          @click="emit('force-delist')"
        >
          强制下架
        </el-button>
      </template>
      <el-button size="small" text type="primary" @click="emit('detail')">
        看完整信息
      </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type { AuditQueueRow } from '@/api/ecosystem/audit/model';

  const props = withDefaults(
    defineProps<{
      row: AuditQueueRow;
      /** pending-待审 spot-抽检 all-全量检索 */
      mode?: 'pending' | 'spot' | 'all';
      selectable?: boolean;
      selected?: boolean;
      active?: boolean;
      /** 预检标记编码 → 中文名，由 /options 下发 */
      flagLabels?: Record<string, string>;
    }>(),
    { mode: 'pending', selectable: false, selected: false, active: false }
  );

  const emit = defineEmits<{
    (e: 'update:selected', value: boolean): void;
    (e: 'focus'): void;
    (e: 'detail'): void;
    (e: 'approve'): void;
    (e: 'reject'): void;
    (e: 'force-delist'): void;
    (e: 'spot-pass'): void;
    (e: 'spot-fail'): void;
  }>();

  const showAuditStatus = computed(() => props.mode !== 'pending');

  /** 只有展示中（PostStatus.LISTED = 3）的挂牌才有「下架」这个动作可言 */
  const canForceDelist = computed(() => props.row.post.status === 3);

  const urgencyTagType = computed(() => {
    if (props.row.urgency >= 2) return 'danger';
    if (props.row.urgency === 1) return 'warning';
    return 'info';
  });

  const waitedText = computed(() => {
    const minutes = props.row.waitedMinutes || 0;
    const spent =
      minutes >= 60
        ? `${Math.floor(minutes / 60)} 小时 ${minutes % 60} 分`
        : `${minutes} 分钟`;
    return `${props.row.urgencyLabel}·已等 ${spent}`;
  });

  const flags = computed(() =>
    (props.row.post.precheckFlags || []).map((code) => ({
      code,
      label: props.flagLabels?.[code] || code
    }))
  );

  const place = (
    province?: string | null,
    city?: string | null,
    district?: string | null
  ) => {
    const parts = [city || province, district].filter(Boolean);
    return parts.length ? parts.join(' ') : province || '—';
  };

  const routeText = computed(() => {
    const post = props.row.post;
    const from = place(post.fromProvince, post.fromCity, post.fromDistrict);
    if (post.anyDirection === 1) {
      return `${from} → 不限方向`;
    }
    const to = place(post.toProvince, post.toCity, post.toDistrict);
    return `${from} → ${to}`;
  });

  const windowText = computed(() => {
    const { windowStart, windowEnd } = props.row.post;
    if (!windowStart && !windowEnd) return '时间待定';
    const short = (v?: string | null) => (v ? v.slice(5, 16) : '');
    if (windowStart && windowEnd) {
      return `${short(windowStart)} 至 ${short(windowEnd)}`;
    }
    return short(windowStart || windowEnd);
  });

  const quantityText = computed(() => {
    const { totalQuantity, quantityUnit } = props.row.post;
    if (totalQuantity == null) return '数量未填';
    return `${totalQuantity} ${quantityUnit || '台'}`;
  });

  const priceText = computed(() => {
    const { priceAmount, priceType } = props.row.post;
    if (priceType === 4 || priceAmount == null) return '价格面议';
    const unit =
      priceType === 2 ? '元/台' : priceType === 3 ? '元/公里' : '元包车';
    return `${priceAmount} ${unit}`;
  });

  const sourceText = computed(() =>
    props.row.post.sourceType === 1 ? '来自系统单据' : '手工填写'
  );
</script>

<style lang="scss" scoped>
  .eco-post-card {
    padding: 12px 14px;
    border: 1px solid var(--el-border-color-lighter);
    border-left-width: 3px;
    border-radius: 6px;
    cursor: pointer;
    transition: box-shadow 0.2s;

    & + & {
      margin-top: 10px;
    }

    &:hover {
      box-shadow: var(--el-box-shadow-lighter);
    }

    &.is-active {
      border-color: var(--el-color-primary);
      background: var(--el-color-primary-light-9);
    }

    &.is-selected {
      background: var(--el-color-primary-light-9);
    }

    &.is-urgency-1 {
      border-left-color: var(--el-color-warning);
    }

    &.is-urgency-2 {
      border-left-color: var(--el-color-danger);
    }
  }

  .eco-post-card__head {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .eco-post-card__title {
    flex: 1;
    min-width: 200px;
    overflow: hidden;
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
    text-overflow: ellipsis;
    color: var(--el-text-color-primary);
  }

  .eco-post-card__urgency {
    margin-left: auto;
  }

  .eco-post-card__facts {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 18px;
    margin-top: 10px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-post-card__route {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .eco-post-card__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 14px;
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-post-card__flags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
  }

  .eco-post-card__reason {
    margin-top: 8px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-color-warning);
  }

  .eco-post-card__actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 10px;
  }
</style>
