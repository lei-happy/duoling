<template>
  <article class="capacity-card" :class="statusCardClass">
    <!-- L1 状态 -->
    <header class="capacity-card__status-bar">
      <div class="capacity-card__status-tags">
        <el-tag size="small" :type="statusTagType" effect="dark">
          {{ statusLabel }}
        </el-tag>
      </div>
      <el-dropdown trigger="click" @command="onCommand">
        <button
          type="button"
          class="capacity-card__menu-btn"
          aria-label="更多操作"
          @click.stop
        >
          <el-icon :size="15"><MoreOutlined /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="unbind">
              <span class="capacity-card__menu-danger">下车</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </header>

    <!-- L2 驾驶员 -->
    <section class="capacity-card__driver">
      <div class="capacity-card__portrait">
        <el-image
          v-if="avatarUrl"
          :src="avatarUrl"
          fit="cover"
          class="capacity-card__portrait-image"
        >
          <template #error>
            <div class="capacity-card__portrait-placeholder">
              <el-icon :size="26"><UserOutlined /></el-icon>
            </div>
          </template>
          <template #placeholder>
            <div class="capacity-card__portrait-placeholder">
              <el-icon :size="26"><UserOutlined /></el-icon>
            </div>
          </template>
        </el-image>
        <div v-else class="capacity-card__portrait-placeholder">
          <el-icon :size="26"><UserOutlined /></el-icon>
        </div>
      </div>
      <div class="capacity-card__driver-info">
        <h3 class="capacity-card__name" :title="item.driverName">
          {{ item.driverName || '—' }}
        </h3>
        <p class="capacity-card__phone">{{ item.driverPhone || '—' }}</p>
        <p class="capacity-card__dept" :title="item.departmentName">
          {{ item.departmentName || '—' }}
        </p>
      </div>
    </section>

    <!-- L3 车辆 -->
    <section class="capacity-card__vehicle">
      <div
        v-if="item.plateNumber || item.trailerPlateNumber"
        class="capacity-card__plates"
      >
        <plate-number-tag
          v-if="item.plateNumber"
          size="large"
          :text="item.plateNumber"
          :category="item.plateCategory"
        />
        <template v-if="item.trailerPlateNumber">
          <span class="capacity-card__plate-sep" aria-hidden="true">·</span>
          <plate-number-tag
            :text="item.trailerPlateNumber"
            :category="item.trailerPlateCategory"
          />
        </template>
      </div>
      <span v-else class="capacity-card__vehicle-empty">暂无车牌</span>
    </section>

    <!-- L4 其他 -->
    <footer v-if="hasMeta" class="capacity-card__meta">
      <div class="capacity-card__meta-tags">
        <dict-data
          v-if="item.vehicleType"
          type="tag"
          :code="dictCodeVehicleType"
          :model-value="item.vehicleType"
          :component-props="{ size: 'small', effect: 'plain' }"
        />
      </div>
      <time
        v-if="item.boundAt"
        class="capacity-card__meta-time"
        :datetime="item.boundAt"
      >
        {{ boundAtLabel }}
      </time>
    </footer>
  </article>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { UserOutlined, MoreOutlined } from '@/components/icons';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import DictData from '@/components/DictData/index.vue';
  import { resolveUploadUrl } from '@/utils/upload-url';
  import { formatDateTime } from '@/utils/date-util';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';

  const dictCodeVehicleType = DICT_CODE_VEHICLE_TYPE;

  const props = defineProps<{
    item: Capacity;
  }>();

  const emit = defineEmits<{
    (e: 'unbind', item: Capacity): void;
  }>();

  const avatarUrl = computed(() => {
    const raw = props.item.driverAvatar?.trim();
    return raw ? resolveUploadUrl(raw) : '';
  });

  const statusMeta = computed(() => {
    switch (props.item.operationStatus) {
      case 1:
        return {
          className: 'capacity-card--op-available',
          label: '可接单',
          tagType: 'success' as const
        };
      case 2:
        return {
          className: 'capacity-card--op-busy',
          label: '忙碌',
          tagType: 'warning' as const
        };
      case 3:
        return {
          className: 'capacity-card--op-leave',
          label: '休假',
          tagType: 'info' as const
        };
      case 4:
        return {
          className: 'capacity-card--op-stopped',
          label: '停运',
          tagType: 'danger' as const
        };
      default:
        return {
          className: 'capacity-card--op-unknown',
          label: '状态未知',
          tagType: 'info' as const
        };
    }
  });

  const statusCardClass = computed(() => statusMeta.value.className);
  const statusLabel = computed(() => statusMeta.value.label);
  const statusTagType = computed(() => statusMeta.value.tagType);

  const hasMeta = computed(
    () => !!props.item.vehicleType || !!props.item.boundAt
  );

  const boundAtLabel = computed(() => {
    if (!props.item.boundAt) {
      return '';
    }
    return `${formatDateTime(props.item.boundAt)} 上车`;
  });

  const onCommand = (command: string) => {
    if (command === 'unbind') {
      emit('unbind', props.item);
    }
  };
</script>

<style scoped>
  .capacity-card {
    display: flex;
    flex-direction: column;
    min-height: 100%;
    border-radius: 10px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    box-sizing: border-box;
    overflow: hidden;
    transition:
      box-shadow 0.2s ease,
      transform 0.2s ease,
      border-color 0.2s ease;
  }

  .capacity-card:hover {
    border-color: var(--el-border-color);
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    transform: translateY(-1px);
  }

  .capacity-card--op-available {
    --capacity-accent: var(--el-color-success);
    --capacity-accent-bg: var(--el-color-success-light-9);
  }

  .capacity-card--op-busy {
    --capacity-accent: var(--el-color-warning);
    --capacity-accent-bg: var(--el-color-warning-light-9);
  }

  .capacity-card--op-leave {
    --capacity-accent: var(--el-color-info);
    --capacity-accent-bg: var(--el-color-info-light-9);
  }

  .capacity-card--op-stopped {
    --capacity-accent: var(--el-color-danger);
    --capacity-accent-bg: var(--el-color-danger-light-9);
  }

  .capacity-card--op-unknown {
    --capacity-accent: var(--el-text-color-secondary);
    --capacity-accent-bg: var(--el-fill-color-light);
  }

  /* L1 状态 */
  .capacity-card__status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 10px;
    background: var(--capacity-accent-bg);
    border-bottom: 1px solid var(--el-border-color-extra-light);
  }

  .capacity-card__status-tags :deep(.el-tag) {
    font-weight: 600;
    border: none;
  }

  .capacity-card__status-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    min-width: 0;
    flex: 1;
  }

  .capacity-card__menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    padding: 0;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    flex-shrink: 0;
    transition:
      background 0.2s,
      color 0.2s;
  }

  .capacity-card__menu-btn:hover {
    background: rgba(255, 255, 255, 0.8);
    color: var(--el-text-color-primary);
  }

  .capacity-card__menu-danger {
    color: var(--el-color-danger);
  }

  /* L2 驾驶员 */
  .capacity-card__driver {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
  }

  .capacity-card__portrait {
    flex-shrink: 0;
    width: 54px;
    aspect-ratio: 3 / 4;
    border-radius: 6px;
    overflow: hidden;
    background: var(--el-fill-color-light);
    box-shadow: inset 0 0 0 1px var(--el-border-color-lighter);
  }

  .capacity-card__portrait-image {
    width: 100%;
    height: 100%;
    display: block;
  }

  .capacity-card__portrait-image :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
  }

  .capacity-card__portrait-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    background: linear-gradient(
      165deg,
      var(--el-fill-color-blank) 0%,
      var(--el-fill-color-light) 100%
    );
  }

  .capacity-card__driver-info {
    flex: 1;
    min-width: 0;
  }

  .capacity-card__name {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.35;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .capacity-card__phone {
    margin: 3px 0 0;
    font-size: 12px;
    line-height: 1.4;
    color: var(--el-text-color-regular);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .capacity-card__dept {
    margin: 2px 0 0;
    font-size: 12px;
    line-height: 1.4;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* L3 车辆 */
  .capacity-card__vehicle {
    margin: 0 10px;
    padding: 8px 10px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
    border: 1px solid var(--el-border-color-extra-light);
  }

  .capacity-card__plates {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 4px 6px;
  }

  .capacity-card__plate-sep {
    font-size: 16px;
    font-weight: 700;
    line-height: 1;
    color: var(--el-text-color-placeholder);
    user-select: none;
  }

  .capacity-card__vehicle-empty {
    display: block;
    text-align: center;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  /* L4 其他 */
  .capacity-card__meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    margin-top: auto;
    padding: 8px 12px 10px;
  }

  .capacity-card__meta-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    min-width: 0;
  }

  .capacity-card__meta-time {
    flex-shrink: 0;
    font-size: 10px;
    color: var(--el-text-color-placeholder);
    white-space: nowrap;
  }
</style>
