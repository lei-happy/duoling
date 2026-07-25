<!--
  审核详情抽屉：判断依据一次给全

  接口一次返回挂牌全字段、预检结论、源单核验、发布方档案、流水与时效
  （见后端 audit_facade.detail 的注释），所以这里不再分块请求——
  审核员在几个 loading 之间来回等的时候，最容易凭不完整的信息点通过。
-->
<template>
  <ele-drawer
    :size="880"
    title="挂牌审核详情"
    v-model="visible"
    :body-style="{ paddingBottom: '8px' }"
  >
    <div v-loading="loading" class="eco-detail">
      <template v-if="detail">
        <div class="eco-detail__head">
          <div class="eco-detail__title">{{ post.title }}</div>
          <div class="eco-detail__tags">
            <el-tag
              size="small"
              :disable-transitions="true"
              :type="post.postType === 1 ? 'warning' : 'success'"
            >
              {{ post.postTypeLabel }}
            </el-tag>
            <el-tag size="small" type="info" :disable-transitions="true">
              {{ post.statusLabel }}
            </el-tag>
            <el-tag size="small" type="info" :disable-transitions="true">
              {{ post.auditStatusLabel }}
            </el-tag>
            <el-tag
              v-if="detail.sla"
              size="small"
              :disable-transitions="true"
              :type="
                detail.sla.urgency >= 2
                  ? 'danger'
                  : detail.sla.urgency === 1
                    ? 'warning'
                    : 'info'
              "
            >
              {{ detail.sla.urgencyLabel }}
              <template v-if="detail.sla.deadline">
                · 应在 {{ detail.sla.deadline }} 前处理
              </template>
            </el-tag>
          </div>
          <div class="eco-detail__meta">
            {{ post.postNo }} · 进队 {{ post.submittedAt || '—' }} · 浏览
            {{ post.viewCount ?? 0 }} 次 · 洽谈 {{ post.intentCount ?? 0 }} 条
          </div>
        </div>

        <!-- 预检与源单：先看这两块，决定要不要细看内容 -->
        <div class="eco-detail__risk">
          <el-alert
            :type="precheckAlertType"
            :closable="false"
            show-icon
            :title="precheckTitle"
          >
            <ul v-if="flagLabelList.length" class="eco-detail__flags">
              <li v-for="f in flagLabelList" :key="f">{{ f }}</li>
            </ul>
          </el-alert>
          <el-alert
            :type="sourceAlertType"
            :closable="false"
            show-icon
            :title="detail.sourceCheck.hint"
            style="margin-top: 8px"
          >
            <div class="eco-detail__source">
              <span v-if="detail.sourceCheck.hasSource">
                源单 ID {{ detail.sourceCheck.sourceId }} · 快照于
                {{ detail.sourceCheck.snapshotAt || '—' }}
              </span>
              <span v-if="detail.sourceCheck.sourceChangedAt">
                · 源单于 {{ detail.sourceCheck.sourceChangedAt }} 被修改
              </span>
            </div>
          </el-alert>
        </div>

        <el-tabs v-model="activeTab" class="eco-detail__tabs">
          <el-tab-pane label="挂牌内容" name="content">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="线路">
                {{ routeText }}
              </el-descriptions-item>
              <el-descriptions-item label="装车时间">
                {{ post.windowStart || '—' }} 至 {{ post.windowEnd || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="数量">
                {{ post.totalQuantity ?? '—' }} {{ post.quantityUnit || '' }}
                <template v-if="post.remainingQuantity != null">
                  （剩余 {{ post.remainingQuantity }}）
                </template>
              </el-descriptions-item>
              <el-descriptions-item label="报价">
                {{ priceText }}
                <template v-if="post.priceNegotiable === 1">· 可议价</template>
                <template v-if="post.priceIncludeTax === 1">· 含税</template>
              </el-descriptions-item>
              <el-descriptions-item label="有效期">
                {{ post.validFrom || '—' }} 至 {{ post.validUntil || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="来源">
                {{ post.sourceType === 1 ? '系统单据带出' : '手工填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="联系人">
                {{ post.contactName || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="联系电话">
                {{ post.contactPhone || '—' }}
                <template v-if="post.contactBackup">
                  / {{ post.contactBackup }}
                </template>
              </el-descriptions-item>
              <el-descriptions-item label="可见范围">
                {{ visibilityText }}
              </el-descriptions-item>
              <el-descriptions-item label="联系方式可见">
                {{ contactVisibilityText }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="post.destinations && post.destinations.length"
                label="多目的地"
                :span="2"
              >
                {{
                  post.destinations
                    .map((d) => [d.province, d.city].filter(Boolean).join(''))
                    .join('、')
                }}
              </el-descriptions-item>
            </el-descriptions>

            <el-descriptions
              v-if="post.cargo"
              :column="2"
              border
              size="small"
              title="货源明细"
              class="eco-detail__ext"
            >
              <el-descriptions-item label="货物">
                {{ post.cargo.cargoName || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="车况">
                {{ post.cargo.vehicleCondition === 2 ? '二手车' : '新车' }}
              </el-descriptions-item>
              <el-descriptions-item label="重量 / 体积">
                {{ post.cargo.cargoWeight ?? '—' }} 吨 /
                {{ post.cargo.cargoVolume ?? '—' }} 方
              </el-descriptions-item>
              <el-descriptions-item label="参考里程">
                {{ post.cargo.referenceMileage ?? '—' }} 公里
              </el-descriptions-item>
              <el-descriptions-item label="车型要求">
                {{ joinList(post.cargo.requireTruckTypes) }}
              </el-descriptions-item>
              <el-descriptions-item label="板位要求">
                {{ post.cargo.requireSlotMin ?? '—' }} ~
                {{ post.cargo.requireSlotMax ?? '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="允许拆单">
                {{ post.cargo.allowSplit === 1 ? '允许' : '不允许' }}
              </el-descriptions-item>
              <el-descriptions-item label="要求保险">
                {{ post.cargo.requireInsurance === 1 ? '要求' : '不要求' }}
              </el-descriptions-item>
              <el-descriptions-item label="其他要求" :span="2">
                {{ post.cargo.otherRequirements || '—' }}
              </el-descriptions-item>
            </el-descriptions>

            <el-descriptions
              v-if="post.capacity"
              :column="2"
              border
              size="small"
              title="运力明细"
              class="eco-detail__ext"
            >
              <el-descriptions-item label="车牌">
                {{ post.capacity.plateNumber || '—' }}
                <span class="eco-detail__hint">
                  （大厅展示 {{ post.capacity.plateMasked || '—' }}）
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="司机">
                {{ post.capacity.driverName || '—' }}
                <span class="eco-detail__hint">
                  （大厅展示 {{ post.capacity.driverDisplay || '—' }}）
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="车型 / 板位">
                {{ post.capacity.truckType || '—' }} /
                {{ post.capacity.slotCount ?? '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="车长 / 核载">
                {{ post.capacity.truckLength ?? '—' }} 米 /
                {{ post.capacity.ratedLoad ?? '—' }} 吨
              </el-descriptions-item>
              <el-descriptions-item label="挂车">
                {{
                  post.capacity.hasTrailer === 1
                    ? post.capacity.trailerPlateNumber || '有'
                    : '无'
                }}
              </el-descriptions-item>
              <el-descriptions-item label="可开发票">
                {{
                  post.capacity.canInvoice === 1
                    ? post.capacity.invoiceType || '可开'
                    : '不可开'
                }}
              </el-descriptions-item>
              <el-descriptions-item label="保险">
                {{ post.capacity.hasInsurance === 1 ? '在保' : '无 / 已过期' }}
              </el-descriptions-item>
              <el-descriptions-item label="可出发时间">
                {{ post.capacity.departureReadyAt || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="服务承诺" :span="2">
                {{ post.capacity.servicePromise || '—' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="发布方档案" name="owner">
            <tenant-profile :profile="ownerProfile" @changed="reload" />
          </el-tab-pane>

          <el-tab-pane name="trail">
            <template #label>
              流转流水
              <span
                v-if="detail.auditTrail.length"
                class="eco-detail__tab-count"
              >
                {{ detail.auditTrail.length }}
              </span>
            </template>
            <el-timeline v-if="detail.auditTrail.length">
              <el-timeline-item
                v-for="item in detail.auditTrail"
                :key="item.id"
                :timestamp="item.createdAt || ''"
                placement="top"
              >
                <div class="eco-detail__trail-title">
                  {{ item.actionLabel }}
                  <span class="eco-detail__hint">
                    {{ item.operatorTypeLabel }}
                    {{ item.operatorName || '' }}
                  </span>
                </div>
                <div
                  v-if="item.fromStatusLabel || item.toStatusLabel"
                  class="eco-detail__hint"
                >
                  {{ item.fromStatusLabel || '—' }} →
                  {{ item.toStatusLabel || '—' }}
                </div>
                <div
                  v-if="item.reason || item.reasonLabel"
                  class="eco-detail__trail-reason"
                >
                  {{ item.reasonLabel ? `【${item.reasonLabel}】` : '' }}
                  {{ item.reason || '' }}
                </div>
                <div
                  v-if="changedFieldText(item.changedFields)"
                  class="eco-detail__hint"
                >
                  改动：{{ changedFieldText(item.changedFields) }}
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else :image-size="72" description="还没有流转记录" />
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <template #footer>
      <div class="eco-detail__footer">
        <el-button @click="visible = false">关闭</el-button>
        <template v-if="detail && isPending">
          <el-button type="danger" plain @click="emitAction('reject')">
            驳回
          </el-button>
          <el-button type="primary" @click="emitAction('approve')">
            通过并上架
          </el-button>
        </template>
        <template v-else-if="detail && isSpotCheck">
          <el-button type="danger" plain @click="emitAction('spot-fail')">
            抽检不通过
          </el-button>
          <el-button type="primary" @click="emitAction('spot-pass')">
            抽检通过
          </el-button>
        </template>
        <template v-else-if="detail && isListed">
          <el-button type="danger" plain @click="emitAction('force-delist')">
            强制下架
          </el-button>
        </template>
      </div>
    </template>
  </ele-drawer>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getAuditDetail } from '@/api/ecosystem/audit';
  import type { AuditDetail, AuditPost } from '@/api/ecosystem/audit/model';
  import TenantProfile from '@/views/ecosystem/components/tenant-profile.vue';

  const props = defineProps<{
    postId?: number | null;
    /** 预检标记编码 → 中文名 */
    flagLabels?: Record<string, string>;
  }>();

  const emit = defineEmits<{
    (
      e: 'action',
      name: 'approve' | 'reject' | 'force-delist' | 'spot-pass' | 'spot-fail',
      post: AuditPost
    ): void;
  }>();

  const visible = defineModel<boolean>({ default: false });

  const loading = ref(false);
  const detail = ref<AuditDetail | null>(null);
  const activeTab = ref('content');

  const post = computed(() => detail.value?.post ?? ({} as any));

  const ownerProfile = computed(() =>
    detail.value
      ? {
          tenant: detail.value.ownerContext,
          eligibility: detail.value.whitelistEligibility
        }
      : null
  );

  const isPending = computed(() => post.value.auditStatus === 1);
  const isSpotCheck = computed(() => post.value.auditStatus === 4);
  const isListed = computed(() => post.value.status === 3);

  const flagLabelList = computed(() =>
    (detail.value?.precheck.flags || []).map(
      (code) => props.flagLabels?.[code] || code
    )
  );

  const precheckAlertType = computed(() => {
    if (detail.value?.precheck.hasBlocking) return 'error';
    return flagLabelList.value.length ? 'warning' : 'success';
  });

  const precheckTitle = computed(() => {
    const count = flagLabelList.value.length;
    if (!count) return '自动预检没有发现可疑点';
    return `自动预检标了 ${count} 处，请重点核对`;
  });

  const sourceAlertType = computed(() => {
    const consistent = detail.value?.sourceCheck.sourceConsistent;
    if (consistent === false) return 'error';
    if (consistent === null) return 'info';
    return 'success';
  });

  const routeText = computed(() => {
    const p = post.value;
    const from = [p.fromCity || p.fromProvince, p.fromDistrict]
      .filter(Boolean)
      .join(' ');
    if (p.anyDirection === 1) {
      return `${from || '—'} → 不限方向`;
    }
    const to = [p.toCity || p.toProvince, p.toDistrict]
      .filter(Boolean)
      .join(' ');
    return `${from || '—'} → ${to || '—'}`;
  });

  const priceText = computed(() => {
    const { priceAmount, priceType } = post.value;
    if (priceType === 4 || priceAmount == null) return '价格面议';
    const unit =
      priceType === 2 ? '元/台' : priceType === 3 ? '元/公里' : '元包车';
    return `${priceAmount} ${unit}`;
  });

  const visibilityText = computed(() => {
    const level = post.value.visibilityLevel;
    if (level === 2) return '仅认证企业可见';
    if (level === 3) return '仅指定企业可见';
    return '所有企业可见';
  });

  const contactVisibilityText = computed(() =>
    post.value.contactVisibility === 1 ? '发起洽谈后可见' : '双方确认洽谈后可见'
  );

  const joinList = (value: any) => {
    if (Array.isArray(value)) {
      return value.length ? value.join('、') : '—';
    }
    return value || '—';
  };

  /** 编辑流水里的 changed_fields 是 {字段: {from, to}}，这里只给个概览 */
  const changedFieldText = (fields: any) => {
    if (!fields || typeof fields !== 'object') {
      return '';
    }
    const keys = Object.keys(fields);
    return keys.length ? keys.join('、') : '';
  };

  const load = (id?: number | null) => {
    if (!id) {
      detail.value = null;
      return;
    }
    loading.value = true;
    getAuditDetail(id)
      .then((data) => {
        loading.value = false;
        detail.value = data;
      })
      .catch((e) => {
        loading.value = false;
        detail.value = null;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const reload = () => load(props.postId);

  watch(
    () => [visible.value, props.postId] as const,
    ([open, id]) => {
      if (open) {
        activeTab.value = 'content';
        load(id);
      }
    },
    { immediate: true }
  );

  const emitAction = (
    name: 'approve' | 'reject' | 'force-delist' | 'spot-pass' | 'spot-fail'
  ) => {
    if (!detail.value) {
      return;
    }
    emit('action', name, detail.value.post);
    visible.value = false;
  };

  defineExpose({ reload });
</script>

<style lang="scss" scoped>
  .eco-detail {
    min-height: 200px;
  }

  .eco-detail__title {
    font-size: 16px;
    font-weight: 600;
    line-height: 1.5;
    color: var(--el-text-color-primary);
  }

  .eco-detail__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
  }

  .eco-detail__meta {
    margin-top: 6px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__risk {
    margin-top: 14px;
  }

  .eco-detail__flags {
    margin: 4px 0 0;
    padding-left: 18px;
    font-size: 13px;
    line-height: 1.7;
  }

  .eco-detail__source {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__tabs {
    margin-top: 8px;
  }

  .eco-detail__ext {
    margin-top: 16px;
  }

  .eco-detail__tab-count {
    margin-left: 4px;
    padding: 0 6px;
    border-radius: 9px;
    font-size: 12px;
    background: var(--el-fill-color-dark);
    color: var(--el-text-color-regular);
  }

  .eco-detail__hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-detail__trail-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .eco-detail__trail-reason {
    margin-top: 2px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-color-warning);
  }

  .eco-detail__footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
