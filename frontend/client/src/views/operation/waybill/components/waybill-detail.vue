<!--
  计划详情弹框（只读）

  展示：
  - 线路摘要：客户、起运 / 送达、台数
  - 计划信息：时间、经销商、金额、备注
  - 任务挂接：总台数 / 已分配 / 剩余
  - 商品车明细：品牌、车型、VIN、台数

  不提供编辑/删除；改关键字段请先到任务台账处理挂接。
-->
<template>
  <inspect-dialog
    :visible="visible"
    title="计划详情"
    :subtitle="waybill?.waybillNo || ''"
    :copyable-subtitle="!!waybill?.waybillNo"
    copy-subtitle-success="已复制计划号"
    copy-subtitle-empty="无可复制的计划号"
    copy-subtitle-label="复制计划号"
    :loading="loading"
    @update:visible="(v: boolean) => emit('update:visible', v)"
  >
    <template #header-extra>
      <waybill-status-tag v-if="waybill" :status="waybill.status" />
      <el-tag
        v-if="waybill?.hasActiveTaskItems"
        type="warning"
        effect="plain"
        size="small"
      >
        有任务占用
      </el-tag>
    </template>

    <div v-if="waybill" class="wbd">
      <section class="wbi-hero" aria-label="线路摘要">
        <div class="wbi-hero__who">
          {{ waybill.customerName?.trim() || '未填写客户' }}
        </div>
        <div class="wbi-hero__route">
          <div class="wbi-hero__end">
            <span class="wbi-hero__kicker">起运</span>
            <span class="wbi-hero__city">{{
              waybill.origin?.trim() || '—'
            }}</span>
          </div>
          <div class="wbi-hero__spine" aria-hidden="true">
            <span class="wbi-hero__rail"></span>
          </div>
          <div class="wbi-hero__end wbi-hero__end--to">
            <span class="wbi-hero__kicker">送达</span>
            <span class="wbi-hero__city">{{
              waybill.destination?.trim() || '—'
            }}</span>
          </div>
          <div class="wbi-hero__stamp" :title="`${totalQuantity} 台`">
            <span class="wbi-hero__stamp-num">{{ totalQuantity }}</span>
            <span class="wbi-hero__stamp-unit">台</span>
          </div>
        </div>
      </section>

      <section class="wbi-section">
        <h3 class="wbi-section__title">计划信息</h3>
        <div class="wbi-group">
          <div class="wbi-row">
            <span class="wbi-row__label">计费金额</span>
            <span class="wbi-row__value">{{
              formatAmount(waybill.freightAmount)
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">计划下发</span>
            <span class="wbi-row__value">{{
              formatDateTime(waybill.planIssueTime) || '—'
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">要求装车</span>
            <span class="wbi-row__value">{{
              formatDateTime(waybill.requiredLoadTime) || '—'
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">要求送达</span>
            <span class="wbi-row__value">{{
              formatDateTime(waybill.requiredDeliverTime) || '—'
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">创建时间</span>
            <span class="wbi-row__value">{{
              formatDateTime(waybill.createdAt) || '—'
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">经销商</span>
            <span class="wbi-row__value">{{ dealerText }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">备注</span>
            <span
              class="wbi-row__value"
              :class="{ 'wbi-row__value--muted': !waybill.remark }"
            >
              {{ waybill.remark || '无' }}
            </span>
          </div>
        </div>
      </section>

      <section class="wbi-section">
        <h3 class="wbi-section__title">任务挂接</h3>
        <div class="wbi-group">
          <div class="wbi-row">
            <span class="wbi-row__label">总台数</span>
            <span class="wbi-row__value">{{ totalQuantity }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">已分配</span>
            <span class="wbi-row__value">{{
              waybill.allocatedQuantity ?? 0
            }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">剩余可分配</span>
            <span class="wbi-row__value">{{ remainingQuantity }}</span>
          </div>
          <div class="wbi-row">
            <span class="wbi-row__label">活跃挂接</span>
            <span class="wbi-row__value">
              <el-tag
                v-if="waybill.hasActiveTaskItems"
                type="warning"
                size="small"
              >
                有占用
              </el-tag>
              <el-tag v-else type="info" size="small" effect="plain">无</el-tag>
            </span>
          </div>
        </div>
        <p v-if="waybill.hasActiveTaskItems" class="wbi-note">
          有任务占用时，台数和起终地不能改。如需调整，请先到「任务台账」取消挂接。
        </p>
      </section>

      <section class="wbi-section">
        <h3 class="wbi-section__title">商品车明细</h3>
        <div v-if="cargoRows.length" class="wbi-group">
          <div
            v-for="(row, idx) in cargoRows"
            :key="row.id ?? `${row.vin || 'row'}-${idx}`"
            class="wbi-vehicle"
          >
            <div class="wbi-vehicle__thumb">
              <el-image
                v-if="imageSrc(row)"
                :src="imageSrc(row)"
                fit="cover"
                class="wbi-vehicle__img"
                lazy
              >
                <template #error>
                  <div class="wbi-vehicle__ph">
                    <el-icon :size="20"><Picture /></el-icon>
                    <span>暂无图片</span>
                  </div>
                </template>
              </el-image>
              <div v-else class="wbi-vehicle__ph">
                <el-icon :size="20"><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
              <span class="wbi-vehicle__qty">×{{ row.quantity }}</span>
            </div>
            <div class="wbi-vehicle__info">
              <div class="wbi-vehicle__name">
                {{ row.vehicleBrand }}
                <template v-if="row.vehicleModel">
                  / {{ row.vehicleModel }}
                </template>
              </div>
              <div v-if="row.vin" class="wbi-vehicle__vin">
                <span class="wbi-vehicle__vin-text">VIN {{ row.vin }}</span>
                <inspect-copy-button
                  :text="row.vin"
                  success-tip="已复制 VIN"
                  empty-tip="无可复制的 VIN"
                  aria-label="复制 VIN"
                />
              </div>
            </div>
          </div>
        </div>
        <div v-else class="wbi-group">
          <el-empty description="暂无商品车明细" :image-size="72" />
        </div>
      </section>
    </div>
    <el-empty
      v-else-if="!loading"
      description="没有找到这份计划"
      :image-size="80"
    />

    <template #footer>
      <el-button @click="emit('update:visible', false)">关闭</el-button>
    </template>
  </inspect-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { Picture } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getWaybill } from '@/api/waybill';
  import type { Waybill, WaybillCargoLine } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';
  import InspectDialog from '@/components/InspectDialog/index.vue';
  import InspectCopyButton from '@/components/InspectDialog/copy-button.vue';
  import WaybillStatusTag from './waybill-status-tag.vue';

  defineOptions({ name: 'WaybillDetail' });

  const props = defineProps<{
    visible: boolean;
    waybillId: number | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  const loading = ref(false);
  const waybill = ref<Waybill | null>(null);

  interface CargoRow {
    id?: number;
    vehicleBrand: string;
    vehicleModel: string;
    quantity: number;
    vin?: string | null;
    seriesImage?: string | null;
  }

  const cargoRows = computed<CargoRow[]>(() => {
    const raw = waybill.value?.cargoes ?? [];
    if (raw.length) {
      return [...raw]
        .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
        .map((line: WaybillCargoLine) => ({
          id: line.id,
          vehicleBrand: line.vehicleBrand?.trim() || '—',
          vehicleModel: line.vehicleModel?.trim() || '',
          quantity: line.quantity ?? 0,
          vin: line.vin?.trim() || null,
          seriesImage: line.seriesImage
        }));
    }
    const w = waybill.value;
    if (!w) return [];
    const brand = w.vehicleBrand?.trim() || '';
    const model = w.vehicleModel?.trim() || '';
    const qty = w.quantity ?? 0;
    if (!brand && !model && !qty) return [];
    return [
      {
        vehicleBrand: brand || '—',
        vehicleModel: model,
        quantity: qty,
        vin: null,
        seriesImage: w.primarySeriesImage
      }
    ];
  });

  const totalQuantity = computed(() =>
    cargoRows.value.reduce((acc, c) => acc + Number(c.quantity || 0), 0)
  );
  const remainingQuantity = computed(
    () => totalQuantity.value - Number(waybill.value?.allocatedQuantity ?? 0)
  );

  const dealerText = computed(() => {
    const w = waybill.value;
    if (!w) return '—';
    const parts = [w.dealerName, w.dealerContact, w.dealerPhone]
      .map((s) => s?.trim())
      .filter(Boolean);
    return parts.length ? parts.join(' · ') : '—';
  });

  const formatAmount = (v?: number | null) => {
    if (v === null || v === undefined) return '—';
    return `¥ ${Number(v).toFixed(2)}`;
  };

  const resolveMediaUrl = (p?: string | null): string => {
    const s = p?.trim();
    if (!s) return '';
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    return s.startsWith('/') ? s : `/${s}`;
  };

  const imageSrc = (row: CargoRow): string => resolveMediaUrl(row.seriesImage);

  watch(
    () => [props.visible, props.waybillId] as const,
    async ([v, id]) => {
      if (!v) {
        waybill.value = null;
        return;
      }
      if (!id) return;
      loading.value = true;
      try {
        waybill.value = await getWaybill(id);
      } catch (e: unknown) {
        const msg = (e as { message?: string }).message || '加载失败，请重试';
        EleMessage.error({ message: msg, plain: true });
      } finally {
        loading.value = false;
      }
    },
    { immediate: true }
  );
</script>
