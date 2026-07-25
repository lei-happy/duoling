<!-- 计划列表：商品车明细（只读，含车系图与客户/线路摘要） -->
<template>
  <el-dialog
    :model-value="visible"
    width="640px"
    draggable
    align-center
    append-to-body
    destroy-on-close
    :close-on-click-modal="true"
    class="waybill-cargoes-detail-dialog"
    :show-close="true"
    @update:model-value="updateVisible"
  >
    <template #header>
      <div class="wcd-header">
        <div class="wcd-header__title">商品车明细</div>
        <div v-if="waybillNo" class="wcd-header__sub-row">
          <span class="wcd-header__sub">{{ waybillNo }}</span>
          <el-button
            v-if="canCopyWaybillNo"
            type="primary"
            link
            class="wcd-header__copy"
            :icon="DocumentCopy"
            aria-label="复制计划号"
            @click.stop="copyWaybillNo"
          />
        </div>
      </div>
    </template>

    <div v-if="waybill" class="wcd-body">
      <div class="wcd-summary">
        <div class="wcd-summary__customer">
          <el-icon class="wcd-summary__icon"><User /></el-icon>
          <span class="wcd-summary__customer-text">{{ customerDisplay }}</span>
        </div>
        <div class="wcd-summary__route">
          <span class="wcd-route-chip wcd-route-chip--from">
            <el-icon><Location /></el-icon>
            <span class="wcd-route-chip__text">{{ originDisplay }}</span>
          </span>
          <span class="wcd-route-arrow" aria-hidden="true">→</span>
          <span class="wcd-route-chip wcd-route-chip--to">
            <el-icon><Location /></el-icon>
            <span class="wcd-route-chip__text">{{ destDisplay }}</span>
          </span>
        </div>
        <div class="wcd-summary__meta">
          <span class="wcd-pill"> 共 {{ totalUnits }} 台 </span>
        </div>
      </div>

      <el-scrollbar
        v-if="displayRows.length"
        max-height="420px"
        class="wcd-scroll"
      >
        <ul class="wcd-list">
          <li v-for="(row, idx) in displayRows" :key="idx" class="wcd-card">
            <div class="wcd-card__thumb">
              <el-image
                v-if="imageSrc(row)"
                :src="imageSrc(row)"
                fit="cover"
                class="wcd-card__img"
                lazy
              >
                <template #error>
                  <div class="wcd-card__placeholder">
                    <el-icon :size="28"><Picture /></el-icon>
                    <span>暂无图片</span>
                  </div>
                </template>
              </el-image>
              <div v-else class="wcd-card__placeholder">
                <el-icon :size="28"><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
              <span class="wcd-card__qty">×{{ row.quantity }}</span>
            </div>
            <div class="wcd-card__info">
              <div class="wcd-card__line wcd-card__line--strong">
                {{ row.vehicleBrand }}
                <span v-if="row.vehicleModel" class="wcd-card__slash">/</span>
                {{ row.vehicleModel }}
              </div>
              <div class="wcd-card__line wcd-card__line--muted">
                品牌 · 车型
              </div>
              <div
                v-if="row.vin"
                class="wcd-card__line wcd-card__line--vin"
                :title="row.vin"
              >
                <span class="wcd-card__vin-text">VIN {{ row.vin }}</span>
                <el-button
                  type="primary"
                  link
                  class="wcd-card__vin-copy"
                  :icon="DocumentCopy"
                  title="复制 VIN"
                  aria-label="复制 VIN"
                  @click.stop="copyVin(row.vin)"
                />
              </div>
            </div>
          </li>
        </ul>
      </el-scrollbar>
      <el-empty v-else description="暂无商品车明细" class="wcd-empty" />
    </div>

    <template #footer>
      <el-button type="primary" @click="updateVisible(false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import {
    DocumentCopy,
    Location,
    User,
    Picture
  } from '@element-plus/icons-vue';
  import type { Waybill } from '@/api/waybill/model';
  import { EleMessage } from 'ele-admin-plus';

  defineOptions({ name: 'WaybillCargoesDetail' });

  const props = defineProps<{
    visible: boolean;
    waybill: Waybill | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const updateVisible = (v: boolean) => {
    emit('update:visible', v);
  };

  const waybillNo = computed(() => props.waybill?.waybillNo?.trim() || '');

  /** 汇总类副标题不展示复制（如「N 张计划」「任务 xxx」） */
  const canCopyWaybillNo = computed(() => {
    const t = waybillNo.value;
    if (!t) return false;
    if (t.includes('张计划') || t.startsWith('任务')) return false;
    return true;
  });

  const copyText = async (
    raw: string | undefined | null,
    emptyTip: string,
    successTip: string
  ) => {
    const t = raw?.trim();
    if (!t) {
      EleMessage.warning({ message: emptyTip, plain: true });
      return;
    }
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(t);
      } else {
        const ta = document.createElement('textarea');
        ta.value = t;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      EleMessage.success({ message: successTip, plain: true });
    } catch {
      EleMessage.error({ message: '复制失败，请重试', plain: true });
    }
  };

  const copyWaybillNo = () =>
    copyText(waybillNo.value, '无可复制的计划号', '已复制计划号');

  const copyVin = (vin?: string | null) =>
    copyText(vin, '无可复制的 VIN', '已复制 VIN');

  const customerDisplay = computed(() => {
    const n = props.waybill?.customerName?.trim();
    return n || '未填写客户';
  });

  const originDisplay = computed(() => {
    const o = props.waybill?.origin?.trim();
    return o || '—';
  });

  const destDisplay = computed(() => {
    const d = props.waybill?.destination?.trim();
    return d || '—';
  });

  interface DisplayRow {
    vehicleBrand: string;
    vehicleModel: string;
    quantity: number;
    vin?: string | null;
    seriesImage?: string | null;
  }

  /** 与基础数据车系预览一致：相对路径补前缀，外链原样 */
  function resolveMediaUrl(p?: string | null): string {
    const s = p?.trim();
    if (!s) return '';
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    return s.startsWith('/') ? s : `/${s}`;
  }

  function imageSrc(row: DisplayRow): string {
    return resolveMediaUrl(row.seriesImage);
  }

  const displayRows = computed<DisplayRow[]>(() => {
    const w = props.waybill;
    if (!w) return [];

    const raw = w.cargoes ?? [];
    if (raw.length) {
      const sorted = [...raw].sort(
        (a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0)
      );
      return sorted.map((line) => ({
        vehicleBrand: line.vehicleBrand?.trim() || '—',
        vehicleModel: line.vehicleModel?.trim() || '—',
        quantity: line.quantity ?? 0,
        vin: line.vin?.trim() || null,
        seriesImage: line.seriesImage
      }));
    }

    const qty = w.quantity ?? 0;
    const brand = (w.vehicleBrand ?? '').trim();
    const model = (w.vehicleModel ?? '').trim();
    if (qty > 0 || brand || model) {
      return [
        {
          vehicleBrand: brand || '—',
          vehicleModel: model || '—',
          quantity: qty,
          vin: null,
          seriesImage: w.primarySeriesImage
        }
      ];
    }
    return [];
  });

  const totalUnits = computed(() =>
    displayRows.value.reduce((s, r) => s + (r.quantity || 0), 0)
  );
</script>

<style scoped>
  .wcd-header {
    padding-right: 28px;
  }

  .wcd-header__title {
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--el-text-color-primary);
  }

  .wcd-header__sub-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
    flex-wrap: wrap;
  }

  .wcd-header__sub {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    font-family: ui-monospace, monospace;
  }

  .wcd-header__copy {
    padding: 0 4px;
    min-height: auto;
    font-size: 16px;
  }

  .wcd-body {
    margin-top: -6px;
  }

  .wcd-summary {
    padding: 16px 18px;
    border-radius: 12px;
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-light) 48%,
      var(--el-bg-color) 100%
    );
    border: 1px solid var(--el-border-color-lighter);
    margin-bottom: 16px;
  }

  .wcd-summary__customer {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 10px;
  }

  .wcd-summary__icon {
    margin-top: 2px;
    color: var(--el-color-primary);
    flex-shrink: 0;
  }

  .wcd-summary__customer-text {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.4;
  }

  .wcd-summary__route {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 10px;
    margin-bottom: 12px;
  }

  .wcd-route-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    max-width: 100%;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 13px;
    background: var(--el-bg-color-overlay);
    border: 1px solid var(--el-border-color-extra-light);
    color: var(--el-text-color-regular);
  }

  .wcd-route-chip .el-icon {
    flex-shrink: 0;
    color: var(--el-color-primary);
  }

  .wcd-route-chip__text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .wcd-route-arrow {
    color: var(--el-text-color-placeholder);
    font-size: 14px;
    user-select: none;
  }

  .wcd-summary__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .wcd-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    background: var(--el-color-primary);
    color: var(--el-color-white);
  }

  .wcd-pill--muted {
    background: var(--el-fill-color-dark);
    color: var(--el-text-color-secondary);
    font-weight: 400;
  }

  .wcd-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .wcd-card {
    display: flex;
    gap: 14px;
    padding: 12px 14px;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    transition:
      border-color 0.15s ease,
      box-shadow 0.15s ease;
  }

  .wcd-card:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .wcd-card__thumb {
    position: relative;
    flex-shrink: 0;
    width: 120px;
    height: 80px;
    border-radius: 8px;
    overflow: hidden;
    background: var(--el-fill-color-light);
  }

  .wcd-card__img {
    width: 120px;
    height: 80px;
    display: block;
  }

  .wcd-card__placeholder {
    width: 120px;
    height: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: var(--el-text-color-placeholder);
    font-size: 11px;
    background: linear-gradient(
      180deg,
      var(--el-fill-color) 0%,
      var(--el-fill-color-light) 100%
    );
  }

  .wcd-card__qty {
    position: absolute;
    right: 6px;
    bottom: 5px;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: #fff;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(4px);
  }

  .wcd-card__info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
  }

  .wcd-card__line--strong {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.35;
  }

  .wcd-card__slash {
    margin: 0 2px;
    color: var(--el-text-color-placeholder);
    font-weight: 400;
  }

  .wcd-card__line--muted {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .wcd-card__line--vin {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    max-width: 100%;
    font-size: 12px;
    font-family: ui-monospace, monospace;
    color: var(--el-text-color-regular);
  }

  .wcd-card__vin-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .wcd-card__vin-copy {
    flex-shrink: 0;
    padding: 2px 4px;
    min-height: auto;
  }

  .wcd-empty {
    padding: 24px 0;
  }
</style>

<style>
  .waybill-cargoes-detail-dialog .el-dialog__header {
    padding-bottom: 8px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    margin-right: 0;
  }

  .waybill-cargoes-detail-dialog .el-dialog__body {
    padding-top: 12px;
  }
</style>
