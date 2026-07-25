<!--
  挂牌详情抽屉

  同一个抽屉服务两种场景，靠 `mine` 区分：
  - 在大厅里看别人的（走大厅接口，会记一次浏览，字段按可见层级裁剪）
  - 在「我发布的」里看自己的（走 my-posts 接口，不限状态，多一块热度反馈与审核结论）

  做成抽屉而不是页面：用户的动线是「在卡片流里连着看好几条」，跳页面会丢掉
  列表位置和已经翻到的页码。
-->
<template>
  <ele-drawer
    :size="720"
    :title="mine ? '我的挂牌' : '信息详情'"
    :model-value="visible"
    :body-style="{ paddingBottom: '8px' }"
    @update:model-value="updateVisible"
    @open="load"
  >
    <div v-loading="loading" class="eco-detail">
      <template v-if="post">
        <div class="eco-detail__head">
          <div class="eco-detail__title">{{ post.title }}</div>
          <div class="eco-detail__meta">
            <eco-post-status-tag
              v-if="mine"
              :status="post.status"
              :valid-until="post.validUntil"
            />
            <span class="eco-detail__no">编号 {{ post.postNo }}</span>
            <span v-if="post.listedAt">发布于 {{ post.listedAt }}</span>
            <span v-if="post.validUntil">展示到 {{ post.validUntil }}</span>
          </div>
        </div>

        <!-- 被驳回时，第一眼要看到原因和该怎么改 -->
        <el-alert
          v-if="mine && post.status === PostStatus.REJECTED"
          type="error"
          :closable="false"
          show-icon
          class="eco-detail__alert"
          title="这条信息没通过审核"
          :description="
            post.auditReason
              ? `原因：${post.auditReason}。改好后点「提交审核」再试一次。`
              : '改好后点「提交审核」再试一次。'
          "
        />
        <el-alert
          v-else-if="mine && post.status === PostStatus.AUDITING"
          type="warning"
          :closable="false"
          show-icon
          class="eco-detail__alert"
          title="正在等平台审核"
          description="通常 2 小时内完成，通过后同行就能看到了。这期间不能编辑，需要改的话先停止展示。"
        />
        <el-alert
          v-else-if="mine && post.status === PostStatus.DELISTED"
          type="info"
          :closable="false"
          show-icon
          class="eco-detail__alert"
          title="已停止展示"
          :description="delistText"
        />

        <ele-card :bordered="true" :body-style="{ padding: '16px' }">
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
          <div class="eco-detail__price-row">
            <span class="eco-detail__price">{{ priceLabel }}</span>
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
              v-if="post.priceIncludeTax"
              size="small"
              type="info"
              effect="plain"
              :disable-transitions="true"
            >
              含税
            </el-tag>
          </div>
        </ele-card>

        <!-- 联系方式：这一块是撮合的关键，位置刻意靠上 -->
        <ele-card
          class="eco-detail__block"
          header="联系方式"
          :bordered="true"
          :body-style="{ padding: '16px' }"
        >
          <template v-if="post.contactPhone">
            <div class="eco-detail__contact">
              <span class="eco-detail__contact-name">
                {{ post.contactName || '联系人' }}
              </span>
              <span class="eco-detail__contact-phone">
                {{ post.contactPhone }}
              </span>
              <el-button link type="primary" @click="copyPhone">复制</el-button>
            </div>
            <div v-if="post.contactBackup" class="eco-detail__contact-backup">
              备用号码 {{ post.contactBackup }}
            </div>
          </template>
          <template v-else>
            <div class="eco-detail__locked">{{ lockedTip }}</div>
            <el-button
              v-if="!canContact"
              type="primary"
              plain
              @click="emit('upgrade')"
            >
              了解专业版
            </el-button>
          </template>
        </ele-card>

        <!-- 关键信息 -->
        <ele-card
          class="eco-detail__block"
          :header="postType === PostType.CARGO ? '货源信息' : '车辆与档期'"
          :bordered="true"
          :body-style="{ padding: '16px' }"
        >
          <el-descriptions :column="2" border size="small">
            <template v-if="postType === PostType.CARGO">
              <el-descriptions-item label="台数">
                {{
                  post.totalQuantity
                    ? `${post.totalQuantity} ${post.quantityUnit || '台'}`
                    : '—'
                }}
              </el-descriptions-item>
              <el-descriptions-item label="装车时间">
                {{ post.windowStart || '可协商' }}
              </el-descriptions-item>
              <el-descriptions-item label="预计到达">
                {{ post.arriveTime || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="结算方式">
                {{ settleText }}
              </el-descriptions-item>
              <el-descriptions-item label="车型要求">
                {{ truckRequireText }}
              </el-descriptions-item>
              <el-descriptions-item label="其他">
                {{ cargoFlagText }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="post.viaPoints?.length"
                label="途经"
                :span="2"
              >
                {{ post.viaPoints.join(' → ') }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="post.otherRequirements"
                label="补充说明"
                :span="2"
              >
                {{ post.otherRequirements }}
              </el-descriptions-item>
            </template>
            <template v-else>
              <el-descriptions-item label="车型">
                {{ capacityTruckText }}
              </el-descriptions-item>
              <el-descriptions-item label="可用时间">
                {{ capacityWindowText }}
              </el-descriptions-item>
              <el-descriptions-item label="车牌">
                {{ post.plateNumber || post.plateMasked || '认证后可见' }}
              </el-descriptions-item>
              <el-descriptions-item label="司机">
                {{ driverText }}
              </el-descriptions-item>
              <el-descriptions-item label="随时可发车">
                {{ post.departureReadyAt || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="接货半径">
                {{ post.pickupRadius ? `${post.pickupRadius} km` : '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="其他">
                {{ capacityFlagText }}
              </el-descriptions-item>
              <el-descriptions-item label="擅长货类">
                {{ post.goodAtCategories?.join('、') || '—' }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="post.servicePromise"
                label="服务承诺"
                :span="2"
              >
                {{ post.servicePromise }}
              </el-descriptions-item>
            </template>
          </el-descriptions>

          <div v-if="cargoItems.length" class="eco-detail__items">
            <div class="eco-detail__items-title">货物明细</div>
            <el-table :data="cargoItems" size="small" border>
              <el-table-column prop="brand" label="品牌" min-width="120" />
              <el-table-column prop="series" label="车系" min-width="140" />
              <el-table-column
                prop="quantity"
                label="台数"
                width="80"
                align="right"
              />
            </el-table>
          </div>
        </ele-card>

        <!-- 发布方 -->
        <ele-card
          v-if="!mine"
          class="eco-detail__block"
          header="发布方"
          :bordered="true"
          :body-style="{ padding: '16px' }"
        >
          <eco-tenant-badge
            :tenant-name="post.ownerTenantName"
            :masked-name="post.ownerMaskedName"
            :credit="post.credit"
            :verified="(post.viewerLevel ?? 1) >= 2"
          />
          <div v-if="post.credit?.topTags?.length" class="eco-detail__tags">
            <el-tag
              v-for="tag in post.credit.topTags"
              :key="tag"
              size="small"
              type="success"
              effect="plain"
              :disable-transitions="true"
            >
              {{ tag }}
            </el-tag>
          </div>
        </ele-card>

        <!-- 仅发布方可见：热度反馈 -->
        <ele-card
          v-if="mine"
          class="eco-detail__block"
          header="这条信息的热度"
          :bordered="true"
          :body-style="{ padding: '16px' }"
        >
          <div class="eco-detail__heat">{{ heatText }}</div>
          <div v-if="heatProvinces" class="eco-detail__heat-sub">
            {{ heatProvinces }}
          </div>
          <el-alert
            v-if="heatAdvice"
            type="info"
            :closable="false"
            show-icon
            class="eco-detail__advice"
            :title="heatAdvice"
          />
        </ele-card>

        <!-- 仅发布方可见：公开范围 -->
        <ele-card
          v-if="mine"
          class="eco-detail__block"
          header="公开范围"
          :bordered="true"
          :body-style="{ padding: '16px' }"
        >
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="企业名">
              {{
                post.visibilityLevel === VisibilityLevel.ANONYMOUS
                  ? '所有人可见'
                  : '仅认证企业可见'
              }}
            </el-descriptions-item>
            <el-descriptions-item label="联系方式">
              {{
                post.contactVisibility === VisibilityLevel.CERTIFIED
                  ? '认证企业可直接看到'
                  : '对方发起合作后互相可见'
              }}
            </el-descriptions-item>
            <el-descriptions-item label="屏蔽名单">
              {{ post.applyBlockRule ? '按企业名片的屏蔽名单生效' : '未启用' }}
            </el-descriptions-item>
          </el-descriptions>
        </ele-card>
      </template>
      <el-empty
        v-else-if="!loading"
        :image-size="72"
        description="这条信息已经看不到了，可能已被停止展示"
      />
    </div>

    <template v-if="mine && post" #footer>
      <div class="eco-detail__footer">
        <el-button v-if="canEdit" type="primary" @click="emit('edit', post)">
          编辑
        </el-button>
        <el-button v-if="canSubmit" type="primary" @click="doSubmit">
          提交审核
        </el-button>
        <el-button v-if="canExtend" @click="emit('extend', post)">
          延长展示
        </el-button>
        <el-button v-if="canRelist" @click="doRelist">重新上架</el-button>
        <el-button v-if="canDelist" type="danger" plain @click="doDelist">
          {{ delistLabel }}
        </el-button>
        <el-button @click="updateVisible(false)">关闭</el-button>
      </div>
    </template>
  </ele-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getHallDetail } from '@/api/ecosystem/hall';
  import { getMyPostDetail } from '@/api/ecosystem/post';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import {
    CooperationType,
    DELIST_REASON_LABELS,
    EDITABLE_STATUSES,
    PostStatus,
    PostType,
    SUBMITTABLE_STATUSES,
    VisibilityLevel,
    priceText
  } from '@/config/ecosystem/enums';
  import EcoRouteArrow from './eco-route-arrow.vue';
  import EcoTenantBadge from './eco-tenant-badge.vue';
  import EcoPostStatusTag from './eco-post-status-tag.vue';
  import { usePostActions } from './use-post-actions';

  const props = withDefaults(
    defineProps<{
      visible: boolean;
      postId?: number | null;
      postType: number;
      /** true 走「我发布的」接口：不限状态，多一块热度与审核结论 */
      mine?: boolean;
      /** 当前租户是否有主动联系同行的能力（pro） */
      canContact?: boolean;
    }>(),
    { mine: false, canContact: false }
  );

  const emit = defineEmits<{
    (e: 'update:visible', visible: boolean): void;
    (e: 'upgrade'): void;
    (e: 'edit', post: EcoPost): void;
    (e: 'extend', post: EcoPost): void;
    (e: 'done'): void;
  }>();

  const { submit, delist, relist } = usePostActions();

  const loading = ref(false);
  const post = ref<EcoPost | null>(null);

  const postType = computed(() => post.value?.postType ?? props.postType);

  const load = async () => {
    if (!props.postId) {
      post.value = null;
      return;
    }
    loading.value = true;
    try {
      post.value = props.mine
        ? await getMyPostDetail(props.postId)
        : await getHallDetail(props.postType, props.postId);
    } catch (e: any) {
      post.value = null;
      EleMessage.error({
        message: e?.message ?? '没能打开这条信息，刷新一下试试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const updateVisible = (value: boolean) => {
    emit('update:visible', value);
  };

  const priceLabel = computed(() => {
    const p = post.value;
    if (!p) {
      return '';
    }
    if (p.priceRange) {
      return `${p.priceRange}${p.priceNegotiable ? '（可议）' : ''}`;
    }
    return priceText(p.priceType, p.priceAmount, p.priceNegotiable);
  });

  /**
   * 联系方式拿不到时说清楚原因
   *
   * 三种原因对用户来说是三件不同的事：版本不够、没认证、发布方设置了洽谈后可见。
   * 混成一句「暂无权限查看」会让人不知道下一步该做什么。
   */
  const lockedTip = computed(() => {
    if (!props.canContact) {
      return '这家的联系方式要专业版才能拿到。升级后可以主动发起合作，对方响应后你们互相可见。';
    }
    if ((post.value?.viewerLevel ?? 1) < 2) {
      return '完成企业认证后才能看到联系方式。认证由平台核验营业执照，一般 1 个工作日内完成。';
    }
    return '发布方设置为「开始洽谈后互相可见」。主动发起合作的功能马上开放，你也可以先把自己的信息发布上来，让对方找到你。';
  });

  const settleText = computed(() => {
    const p = post.value;
    if (!p?.settleType) {
      return '面谈';
    }
    const map: Record<number, string> = { 1: '现结', 2: '月结', 3: '预付' };
    const base = map[p.settleType] || '面谈';
    return p.prepayRatio ? `${base}（预付 ${p.prepayRatio}%）` : base;
  });

  const truckRequireText = computed(() => {
    const p = post.value;
    const parts: string[] = [];
    if (p?.requireTruckTypes?.length) {
      parts.push(p.requireTruckTypes.join('、'));
    }
    if (p?.requireSlotMin) {
      parts.push(
        p.requireSlotMax && p.requireSlotMax !== p.requireSlotMin
          ? `${p.requireSlotMin}-${p.requireSlotMax} 位`
          : `${p.requireSlotMin} 位`
      );
    }
    return parts.join(' · ') || '不限';
  });

  const cargoFlagText = computed(() => {
    const p = post.value;
    const parts: string[] = [];
    if (p?.allowSplit) parts.push('可拆单');
    if (p?.requireInsurance) parts.push('需投保');
    if (p?.timeNegotiable) parts.push('时间可协商');
    if (p?.freqDesc) parts.push(p.freqDesc);
    return parts.join(' · ') || '—';
  });

  const capacityTruckText = computed(() => {
    const p = post.value;
    if (!p) {
      return '—';
    }
    const parts: string[] = [];
    if (p.slotCount) parts.push(`${p.slotCount} 位`);
    if (p.truckType) parts.push(p.truckType);
    if (p.truckLength) parts.push(`${p.truckLength} 米`);
    if (p.hasTrailer) parts.push('带挂');
    return parts.join(' · ') || '—';
  });

  const capacityWindowText = computed(() => {
    const p = post.value;
    if (!p?.windowStart) {
      return '面谈';
    }
    return p.windowEnd
      ? `${p.windowStart} ~ ${p.windowEnd}`
      : `${p.windowStart} 起`;
  });

  const driverText = computed(() => {
    const p = post.value;
    if (!p?.driverDisplay) {
      return '认证后可见';
    }
    const parts = [p.driverDisplay];
    if (p.driverYears) parts.push(`${p.driverYears} 年驾龄`);
    if (p.driverOrderCount) parts.push(`承运 ${p.driverOrderCount} 单`);
    return parts.join(' · ');
  });

  const capacityFlagText = computed(() => {
    const p = post.value;
    const parts: string[] = [];
    if (p?.canInvoice) {
      parts.push(p.invoiceType ? `可开${p.invoiceType}` : '可开票');
    }
    if (p?.hasInsurance) parts.push('已投保');
    return parts.join(' · ') || '—';
  });

  const cargoItems = computed(() =>
    postType.value === PostType.CARGO ? (post.value?.cargoItems ?? []) : []
  );

  const delistText = computed(() => {
    const p = post.value;
    const reason = p?.delistReason
      ? DELIST_REASON_LABELS[p.delistReason]
      : undefined;
    const remark = p?.delistRemark ? `（${p.delistRemark}）` : '';
    return reason
      ? `${reason}${remark}。需要继续找同行的话，点「重新上架」再过一次审核。`
      : '需要继续找同行的话，点「重新上架」再过一次审核。';
  });

  const heatText = computed(() => {
    const stats = post.value?.viewerStats;
    if (!stats || !stats.viewerTenantCount) {
      return '这几天还没有同行看过。刚发布的信息需要一点时间被看到。';
    }
    const base = `近 ${stats.days} 天有 ${stats.viewerTenantCount} 家同行看过，共 ${stats.viewCount} 次`;
    return stats.intentCount
      ? `${base}，${stats.intentCount} 家想合作`
      : `${base}`;
  });

  const heatProvinces = computed(() => {
    const list = post.value?.viewerStats?.topProvinces ?? [];
    if (!list.length) {
      return '';
    }
    return (
      '主要来自 ' +
      list.map((p) => `${p.province} ${p.tenantCount} 家`).join('、')
    );
  });

  /** 看的人不少却没人联系，给一条能立刻执行的建议，而不是干巴巴的数字 */
  const heatAdvice = computed(() => {
    const stats = post.value?.viewerStats;
    if (!stats || post.value?.status !== PostStatus.LISTED) {
      return '';
    }
    if (stats.viewerTenantCount >= 5 && !stats.intentCount) {
      return '有不少同行看过但还没人联系，可以试试调整报价，或者把展示时间延长几天。';
    }
    return '';
  });

  const status = computed(() => post.value?.status ?? -1);
  const canEdit = computed(
    () => EDITABLE_STATUSES.includes(status.value) && !!post.value?.sourceId
  );
  const canSubmit = computed(() => SUBMITTABLE_STATUSES.includes(status.value));
  /**
   * 草稿与被驳回的挂牌也能「下架」（状态机允许），但对用户来说那不是停止展示
   * ——它从来没展示过。文案跟着状态变，否则用户会以为自己点错了按钮。
   */
  const canDelist = computed(() =>
    (
      [
        PostStatus.LISTED,
        PostStatus.AUDITING,
        PostStatus.REJECTED,
        PostStatus.DRAFT
      ] as number[]
    ).includes(status.value)
  );
  const delistLabel = computed(() =>
    status.value === PostStatus.DRAFT || status.value === PostStatus.REJECTED
      ? '不发了'
      : '停止展示'
  );
  const canRelist = computed(() => status.value === PostStatus.DELISTED);
  const canExtend = computed(() => status.value === PostStatus.LISTED);

  const afterAction = () => {
    emit('done');
    load();
  };

  const doSubmit = () => post.value && submit(post.value, afterAction);
  const doDelist = () => post.value && delist(post.value, afterAction);
  const doRelist = () => post.value && relist(post.value, afterAction);

  const copyPhone = async () => {
    const phone = post.value?.contactPhone;
    if (!phone) {
      return;
    }
    try {
      await navigator.clipboard.writeText(phone);
      EleMessage.success({ message: '号码已复制', plain: true });
    } catch {
      EleMessage.warning({
        message: '这个浏览器不支持一键复制，手动选中号码即可',
        plain: true
      });
    }
  };

  defineExpose({ reload: load });
</script>

<style lang="scss" scoped>
  .eco-detail__head {
    margin-bottom: 12px;
  }

  .eco-detail__title {
    font-size: 17px;
    font-weight: 600;
    line-height: 1.5;
    color: var(--el-text-color-primary);
  }

  .eco-detail__meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__alert {
    margin-bottom: 12px;
  }

  .eco-detail__block {
    margin-top: 12px;
  }

  .eco-detail__price-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
  }

  .eco-detail__price {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-color-danger);
  }

  .eco-detail__contact {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .eco-detail__contact-name {
    color: var(--el-text-color-regular);
  }

  .eco-detail__contact-phone {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: var(--el-text-color-primary);
  }

  .eco-detail__contact-backup {
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__locked {
    margin-bottom: 12px;
    line-height: 1.7;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__items {
    margin-top: 14px;
  }

  .eco-detail__items-title {
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-detail__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 8px;
  }

  .eco-detail__heat {
    line-height: 1.7;
    color: var(--el-text-color-primary);
  }

  .eco-detail__heat-sub {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__advice {
    margin-top: 12px;
  }

  .eco-detail__footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
