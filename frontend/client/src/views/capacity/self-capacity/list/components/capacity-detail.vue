<template>
  <div class="capacity-detail" :class="statusCardClass">
    <div class="capacity-detail__header">
      <h3 class="capacity-detail__title">运力详情</h3>
    </div>

    <div class="capacity-detail__body">
      <!-- 身份主区：大图 + 右侧信息铺满，避免与下方重复 -->
      <section class="capacity-detail__profile">
        <div class="capacity-detail__portrait">
          <el-image
            v-if="avatarUrl"
            :src="avatarUrl"
            :preview-src-list="[avatarUrl]"
            :preview-teleported="true"
            :z-index="previewZIndex"
            fit="contain"
            class="capacity-detail__portrait-image"
          >
            <template #error>
              <div class="capacity-detail__portrait-placeholder">
                <el-icon :size="48"><UserOutlined /></el-icon>
                <span>暂无照片</span>
              </div>
            </template>
            <template #placeholder>
              <div class="capacity-detail__portrait-placeholder">
                <el-icon :size="48"><UserOutlined /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-else class="capacity-detail__portrait-placeholder">
            <el-icon :size="48"><UserOutlined /></el-icon>
            <span>暂无照片</span>
          </div>
        </div>

        <div class="capacity-detail__identity">
          <div class="capacity-detail__identity-top">
            <h4 class="capacity-detail__name">
              {{ data?.driverName || '—' }}
            </h4>
            <span class="capacity-detail__badge">{{ statusLabel }}</span>
          </div>

          <dl class="capacity-detail__grid">
            <div class="capacity-detail__cell">
              <dt>手机号</dt>
              <dd class="is-mono">{{ data?.driverPhone || '—' }}</dd>
            </div>
            <div class="capacity-detail__cell">
              <dt>所属部门</dt>
              <dd>{{ data?.departmentName || '—' }}</dd>
            </div>
            <div class="capacity-detail__cell">
              <dt>上车时间</dt>
              <dd class="is-mono">{{ boundAtLabel || '—' }}</dd>
            </div>
            <div class="capacity-detail__cell">
              <dt>车型</dt>
              <dd>
                <dict-data
                  v-if="data?.vehicleType"
                  type="text"
                  :code="dictCodeVehicleType"
                  :model-value="data.vehicleType"
                />
                <template v-else>—</template>
              </dd>
            </div>
            <div class="capacity-detail__cell">
              <dt>主车牌</dt>
              <dd>
                <plate-number-tag
                  v-if="data?.plateNumber"
                  :text="data.plateNumber"
                  :category="data.plateCategory"
                  size="large"
                />
                <template v-else>—</template>
              </dd>
            </div>
            <div class="capacity-detail__cell">
              <dt>挂车牌</dt>
              <dd>
                <plate-number-tag
                  v-if="data?.trailerPlateNumber"
                  :text="data.trailerPlateNumber"
                  :category="data.trailerPlateCategory"
                  size="large"
                />
                <template v-else>—</template>
              </dd>
            </div>
            <div
              v-if="data?.remark"
              class="capacity-detail__cell is-full"
            >
              <dt>备注</dt>
              <dd>{{ data.remark }}</dd>
            </div>
          </dl>
        </div>
      </section>

      <el-tabs v-model="activeTab" class="capacity-detail__tabs">
        <el-tab-pane label="车辆历史" name="vehicle">
          <el-empty description="暂无车辆历史数据" :image-size="72" />
        </el-tab-pane>
        <el-tab-pane label="驾驶员历史" name="driver">
          <el-empty description="暂无驾驶员历史数据" :image-size="72" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { UserOutlined } from '@/components/icons';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import DictData from '@/components/DictData/index.vue';
  import { resolveUploadUrl } from '@/utils/upload-url';
  import { formatDateTime } from '@/utils/date-util';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';

  const dictCodeVehicleType = DICT_CODE_VEHICLE_TYPE;

  /** 高于 FlipModal 默认 z-index(3000)，避免预览沉到弹框下层 */
  const previewZIndex = 4000;

  const props = defineProps<{
    data: Capacity | null;
  }>();

  const activeTab = ref('vehicle');

  watch(
    () => props.data,
    (val) => {
      if (val) {
        activeTab.value = 'vehicle';
      }
    }
  );

  const avatarUrl = computed(() => {
    const raw = props.data?.driverAvatar?.trim();
    return raw ? resolveUploadUrl(raw) : '';
  });

  const statusMeta = computed(() => {
    switch (props.data?.operationStatus) {
      case 1:
        return { className: 'is-op-available', label: '空闲' };
      case 2:
        return { className: 'is-op-intask', label: '运输中' };
      case 3:
        return { className: 'is-op-resting', label: '休假' };
      case 4:
        return { className: 'is-op-stopped', label: '停运' };
      case 5:
        return { className: 'is-op-maintenance', label: '维修保养中' };
      default:
        return { className: 'is-op-unknown', label: '状态未知' };
    }
  });

  const statusCardClass = computed(() => statusMeta.value.className);
  const statusLabel = computed(() => statusMeta.value.label);

  const boundAtLabel = computed(() => {
    if (!props.data?.boundAt) return '';
    return formatDateTime(props.data.boundAt, '');
  });
</script>

<style scoped>
  .capacity-detail {
    --detail-accent: var(--el-color-primary);
    --detail-soft-bg: var(--el-color-primary-light-9);

    display: flex;
    flex-direction: column;
    max-height: 86vh;
  }

  .capacity-detail.is-op-available {
    --detail-accent: var(--el-color-success);
    --detail-soft-bg: var(--el-color-success-light-9);
  }
  .capacity-detail.is-op-intask {
    --detail-accent: var(--el-color-primary);
    --detail-soft-bg: var(--el-color-primary-light-9);
  }
  .capacity-detail.is-op-resting {
    --detail-accent: #64748b;
    --detail-soft-bg: rgba(100, 116, 139, 0.1);
  }
  .capacity-detail.is-op-stopped {
    --detail-accent: var(--el-color-danger);
    --detail-soft-bg: var(--el-color-danger-light-9);
  }
  .capacity-detail.is-op-maintenance {
    --detail-accent: var(--el-color-warning);
    --detail-soft-bg: var(--el-color-warning-light-9);
  }
  .capacity-detail.is-op-unknown {
    --detail-accent: var(--el-text-color-placeholder);
    --detail-soft-bg: var(--el-fill-color-light);
  }

  .capacity-detail__header {
    flex-shrink: 0;
    padding: 18px 48px 14px 24px;
    border-bottom: 1px solid var(--el-border-color-extra-light);
  }

  .capacity-detail__title {
    margin: 0;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--el-text-color-primary);
  }

  .capacity-detail__body {
    flex: 1;
    min-height: 320px;
    padding: 20px 24px 24px;
    overflow: auto;
  }

  /* —— Profile —— */
  .capacity-detail__profile {
    display: flex;
    gap: 20px;
    align-items: stretch;
    padding: 16px;
    margin-bottom: 18px;
    border-radius: 14px;
    border: 1px solid var(--el-border-color-lighter);
    background: linear-gradient(
      135deg,
      color-mix(in srgb, var(--detail-soft-bg) 70%, var(--el-bg-color)) 0%,
      var(--el-bg-color) 55%
    );
  }

  .capacity-detail__portrait {
    flex-shrink: 0;
    width: 168px;
    aspect-ratio: 3 / 4;
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(
      160deg,
      color-mix(in srgb, var(--detail-accent) 10%, var(--el-fill-color-light)),
      var(--el-fill-color-light)
    );
    box-shadow:
      inset 0 0 0 1px var(--el-border-color-extra-light),
      0 4px 14px rgba(15, 23, 42, 0.06);
  }

  .capacity-detail__portrait-image {
    width: 100%;
    height: 100%;
    display: block;
    cursor: zoom-in;
  }

  .capacity-detail__portrait-image :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center center;
  }

  .capacity-detail__portrait-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: color-mix(
      in srgb,
      var(--detail-accent) 40%,
      var(--el-text-color-placeholder)
    );
    font-size: 12px;
  }

  .capacity-detail__identity {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .capacity-detail__identity-top {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px 10px;
  }

  .capacity-detail__name {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: 0.01em;
    color: var(--el-text-color-primary);
  }

  .capacity-detail__badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.45;
    color: var(--detail-accent);
    background: color-mix(in srgb, var(--detail-accent) 14%, transparent);
    white-space: nowrap;
  }

  .capacity-detail__grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px 20px;
    margin: 0;
    flex: 1;
  }

  .capacity-detail__cell {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }

  .capacity-detail__cell.is-full {
    grid-column: 1 / -1;
  }

  .capacity-detail__cell dt {
    margin: 0;
    font-size: 12px;
    line-height: 1.3;
    color: var(--el-text-color-secondary);
  }

  .capacity-detail__cell dd {
    margin: 0;
    font-size: 14px;
    line-height: 1.4;
    color: var(--el-text-color-primary);
    word-break: break-all;
  }

  .capacity-detail__cell dd.is-mono {
    font-variant-numeric: tabular-nums;
    font-weight: 500;
  }

  /* —— Tabs —— */
  .capacity-detail__tabs :deep(.el-tabs__header) {
    margin-bottom: 14px;
  }

  @media (max-width: 640px) {
    .capacity-detail__profile {
      flex-direction: column;
      align-items: center;
    }

    .capacity-detail__portrait {
      width: 148px;
    }

    .capacity-detail__identity {
      width: 100%;
    }

    .capacity-detail__identity-top {
      justify-content: center;
    }

    .capacity-detail__grid {
      grid-template-columns: 1fr;
    }
  }
</style>
