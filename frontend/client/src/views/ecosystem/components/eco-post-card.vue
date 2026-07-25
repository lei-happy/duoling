<!--
  大厅挂牌卡片

  信息顺序照着找货 / 找车方的决策顺序排（05 §3.1）：
  线路 → 货量或车况 → 时间 → 价格 → 这家靠不靠谱 → 热度与行动。
  顺序调换会让人每张卡片都要重新找一遍关键信息。

  两个大厅共用这一个卡片：差异只有中间那块「关键事实」。做成两个组件的结果是
  某次给货源卡片加了标签、运力卡片忘了加，同一个大厅出现两种视觉语言。
-->
<template>
  <div class="eco-card" @click="emit('detail')">
    <div v-if="post.isTop" class="eco-card__top-flag">置顶</div>

    <eco-route-arrow
      :from-province="post.fromProvince"
      :from-city="post.fromCity"
      :from-district="post.fromDistrict"
      :from-name="post.fromName"
      :to-province="post.toProvince"
      :to-city="post.toCity"
      :to-district="post.toDistrict"
      :to-name="post.toName"
      :any-direction="post.anyDirection"
      :destinations="post.destinations"
      :reference-mileage="post.referenceMileage"
    />

    <div class="eco-card__facts">
      <div class="eco-card__fact-main">{{ mainFact }}</div>
      <div class="eco-card__fact-sub">{{ subFact }}</div>
    </div>

    <div class="eco-card__time">
      <el-icon><Clock /></el-icon>
      <span>{{ timeText }}</span>
    </div>

    <div class="eco-card__price">{{ priceLabel }}</div>

    <div class="eco-card__tags">
      <el-tag
        v-if="post.cooperationType === CooperationType.LONG_TERM"
        size="small"
        type="primary"
        effect="plain"
        :disable-transitions="true"
      >
        长期合作
      </el-tag>
      <el-tag
        v-for="tag in extraTags"
        :key="tag"
        size="small"
        type="info"
        effect="plain"
        :disable-transitions="true"
      >
        {{ tag }}
      </el-tag>
    </div>

    <el-divider class="eco-card__divider" />

    <eco-tenant-badge
      :tenant-name="post.ownerTenantName"
      :masked-name="post.ownerMaskedName"
      :credit="post.credit"
      :verified="verified"
    />

    <div class="eco-card__footer">
      <span class="eco-card__heat">{{ heatText }}</span>
      <el-button
        v-if="canContact"
        type="primary"
        size="small"
        @click.stop="emit('detail')"
      >
        {{ postType === PostType.CARGO ? '我要接单' : '我要用车' }}
      </el-button>
      <el-button v-else size="small" @click.stop="emit('upgrade')">
        升级后可联系
      </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { Clock } from '@element-plus/icons-vue';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import {
    CooperationType,
    PostType,
    priceText
  } from '@/config/ecosystem/enums';
  import EcoRouteArrow from './eco-route-arrow.vue';
  import EcoTenantBadge from './eco-tenant-badge.vue';

  const props = defineProps<{
    post: EcoPost;
    /** 当前租户是否有主动联系同行的能力（pro） */
    canContact: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'detail'): void;
    (e: 'upgrade'): void;
  }>();

  const postType = computed(() => props.post.postType);

  /** 发布方是否已认证：列表接口不单独下发，用能看到区县这类认证层字段反推 */
  const verified = computed(() => (props.post.viewerLevel ?? 1) >= 2);

  /** 第一行关键事实：货源看装多少台，运力看什么车 */
  const mainFact = computed(() => {
    const p = props.post;
    if (p.postType === PostType.CARGO) {
      const quantity = p.totalQuantity
        ? `${p.totalQuantity} ${p.quantityUnit || '台'}`
        : '台数待确认';
      const remain =
        p.remainingQuantity != null &&
        p.totalQuantity != null &&
        p.remainingQuantity < p.totalQuantity
          ? `（还剩 ${p.remainingQuantity}）`
          : '';
      return `${quantity}${remain}`;
    }
    const slots = p.slotCount ? `${p.slotCount} 位` : '';
    const truck = p.truckType || '轿运车';
    const count =
      p.truckQuantity && p.truckQuantity > 1 ? ` × ${p.truckQuantity} 台` : '';
    return `${slots}${truck}${count}`.trim();
  });

  /** 第二行：货源列品牌车系，运力列车况与司机 */
  const subFact = computed(() => {
    const p = props.post;
    if (p.postType === PostType.CARGO) {
      const items = (p.cargoItems ?? [])
        .map((i) => [i.brand, i.series].filter(Boolean).join(' '))
        .filter(Boolean);
      if (items.length) {
        return items.slice(0, 2).join('、') + (items.length > 2 ? ' 等' : '');
      }
      return p.cargoName || '商品车';
    }
    const parts: string[] = [];
    if (p.hasTrailer) {
      parts.push('带挂');
    }
    if (p.driverDisplay) {
      parts.push(
        p.driverYears
          ? `${p.driverDisplay} · ${p.driverYears} 年驾龄`
          : p.driverDisplay
      );
    }
    if (p.plateMasked) {
      parts.push(p.plateMasked);
    }
    return parts.join(' · ') || '车辆信息认证后可见';
  });

  /** 时间：货源说什么时候装车，运力说什么时候有空 */
  const timeText = computed(() => {
    const p = props.post;
    if (p.postType === PostType.CARGO) {
      if (!p.windowStart) {
        return '装车时间可协商';
      }
      return `${shortTime(p.windowStart)} 装车${p.timeNegotiable ? ' · 可协商' : ''}`;
    }
    if (!p.windowStart) {
      return '可用时间面谈';
    }
    return p.windowEnd
      ? `${shortTime(p.windowStart)} ~ ${shortTime(p.windowEnd)} 可用`
      : `${shortTime(p.windowStart)} 起可用`;
  });

  const priceLabel = computed(() => {
    const p = props.post;
    // 未认证的查看方拿不到具体金额，后端给的是区间
    if (p.priceRange) {
      return `${p.priceRange}${p.priceNegotiable ? '（可议）' : ''}`;
    }
    return priceText(p.priceType, p.priceAmount, p.priceNegotiable);
  });

  const extraTags = computed(() => {
    const p = props.post;
    const tags: string[] = [];
    if (p.postType === PostType.CARGO) {
      if (p.allowSplit) tags.push('可拆单');
      if (p.requireInsurance) tags.push('需投保');
      if (p.requireSlotMin) {
        tags.push(
          p.requireSlotMax && p.requireSlotMax !== p.requireSlotMin
            ? `需 ${p.requireSlotMin}-${p.requireSlotMax} 位车`
            : `需 ${p.requireSlotMin} 位车`
        );
      }
    } else {
      if (p.canInvoice) tags.push('可开票');
      if (p.hasInsurance) tags.push('已投保');
      if (p.pickupRadius) tags.push(`${p.pickupRadius} km 内可接`);
    }
    return tags.slice(0, 3);
  });

  /**
   * 热度
   *
   * 「已有 3 人想合作」是推动人下决心的关键信息；但未认证层拿不到这两个数字，
   * 此时说「刚刚发布 / 3 小时前活跃」也比空着好——至少说明信息是新的。
   */
  const heatText = computed(() => {
    const p = props.post;
    if (p.intentCount) {
      return `${p.intentCount} 人想合作`;
    }
    const at = p.lastActiveAt || p.listedAt;
    return at ? `${sinceText(at)}发布` : '';
  });

  function shortTime(value: string) {
    // 后端给的是 'YYYY-MM-DD HH:mm'，卡片上省掉年份，够用且更短
    const m = /^(\d{4})-(\d{2})-(\d{2})(?:\s+(\d{2}):(\d{2}))?/.exec(value);
    if (!m) {
      return value;
    }
    const [, , month, day, hour, minute] = m;
    const date = `${Number(month)}月${Number(day)}日`;
    return hour ? `${date} ${hour}:${minute}` : date;
  }

  function sinceText(value: string) {
    const time = new Date(value.replace(/-/g, '/')).getTime();
    if (!Number.isFinite(time)) {
      return '';
    }
    const minutes = Math.floor((Date.now() - time) / 60000);
    if (minutes < 60) {
      return '刚刚';
    }
    if (minutes < 60 * 24) {
      return `${Math.floor(minutes / 60)} 小时前`;
    }
    return `${Math.floor(minutes / 60 / 24)} 天前`;
  }
</script>

<style lang="scss" scoped>
  .eco-card {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 16px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background: var(--el-bg-color-overlay);
    cursor: pointer;
    transition:
      border-color 0.2s,
      box-shadow 0.2s,
      transform 0.2s;

    &:hover {
      border-color: var(--el-color-primary-light-5);
      box-shadow: 0 6px 18px rgb(0 0 0 / 8%);
      transform: translateY(-2px);
    }
  }

  .eco-card__top-flag {
    position: absolute;
    top: 0;
    right: 0;
    padding: 1px 8px;
    font-size: 11px;
    color: #fff;
    background: var(--el-color-warning);
    border-radius: 0 8px 0 8px;
  }

  .eco-card__facts {
    margin-top: 14px;
  }

  .eco-card__fact-main {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .eco-card__fact-sub {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .eco-card__time {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-card__price {
    margin-top: 6px;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-color-danger);
  }

  .eco-card__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 8px;
    min-height: 24px;
  }

  .eco-card__divider {
    margin: 10px 0;
  }

  .eco-card__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: 12px;
  }

  .eco-card__heat {
    font-size: 12px;
    color: var(--el-color-warning);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
