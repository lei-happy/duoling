<!-- 计划列表 / 任务台账：商品车明细（只读） -->
<template>
  <inspect-dialog
    :visible="visible"
    title="商品车明细"
    :subtitle="waybillNo"
    :copyable-subtitle="canCopyWaybillNo"
    copy-subtitle-success="已复制计划号"
    copy-subtitle-empty="无可复制的计划号"
    copy-subtitle-label="复制计划号"
    width="640px"
    @update:visible="updateVisible"
  >
    <div v-if="waybill">
      <section class="wbi-hero" aria-label="线路摘要">
        <div class="wbi-hero__who">{{ customerDisplay }}</div>
        <div class="wbi-hero__route">
          <div class="wbi-hero__end">
            <span class="wbi-hero__kicker">起运</span>
            <span class="wbi-hero__city">{{ originDisplay }}</span>
          </div>
          <div class="wbi-hero__spine" aria-hidden="true">
            <span class="wbi-hero__rail"></span>
          </div>
          <div class="wbi-hero__end wbi-hero__end--to">
            <span class="wbi-hero__kicker">送达</span>
            <span class="wbi-hero__city">{{ destDisplay }}</span>
          </div>
          <div class="wbi-hero__stamp" :title="`${totalUnits} 台`">
            <span class="wbi-hero__stamp-num">{{ totalUnits }}</span>
            <span class="wbi-hero__stamp-unit">台</span>
          </div>
        </div>
      </section>

      <section class="wbi-section">
        <h3 class="wbi-section__title">商品车</h3>
        <div v-if="displayRows.length" class="wbi-group">
          <div
            v-for="(row, idx) in displayRows"
            :key="`${row.vin || 'row'}-${idx}`"
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

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
    </template>
  </inspect-dialog>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { Picture } from '@element-plus/icons-vue';
  import type { Waybill } from '@/api/waybill/model';
  import InspectDialog from '@/components/InspectDialog/index.vue';
  import InspectCopyButton from '@/components/InspectDialog/copy-button.vue';

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
