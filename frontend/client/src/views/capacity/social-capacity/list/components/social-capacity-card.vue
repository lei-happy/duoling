<template>
  <article class="sc-card" :class="statusCardClass">
    <!-- L1 状态 -->
    <header class="sc-card__status-bar">
      <div class="sc-card__status-tags">
        <el-tag size="small" :type="capacityStatusTagType" effect="dark">
          {{ capacityStatusLabel }}
        </el-tag>
        <el-tag
          v-if="showApprovalPill"
          size="small"
          :type="approvalStatusTagType"
          effect="dark"
        >
          {{ approvalStatusLabel }}
        </el-tag>
      </div>
      <el-dropdown trigger="click" @command="onCommand">
        <button
          type="button"
          class="sc-card__menu-btn"
          aria-label="更多操作"
          @click.stop
        >
          <el-icon :size="15"><MoreOutlined /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="menu in menuItems"
              :key="menu.key"
              :command="menu.key"
              :divided="menu.divided"
            >
              <span :class="{ 'sc-card__menu-danger': menu.danger }">{{
                menu.title
              }}</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </header>

    <!-- L2 驾驶员 -->
    <section class="sc-card__driver">
      <div class="sc-card__portrait">
        <el-image
          v-if="avatarUrl"
          :src="avatarUrl"
          fit="cover"
          class="sc-card__portrait-image"
        >
          <template #error>
            <div class="sc-card__portrait-placeholder">
              <el-icon :size="26"><UserOutlined /></el-icon>
            </div>
          </template>
          <template #placeholder>
            <div class="sc-card__portrait-placeholder">
              <el-icon :size="26"><UserOutlined /></el-icon>
            </div>
          </template>
        </el-image>
        <div v-else class="sc-card__portrait-placeholder">
          <el-icon :size="26"><UserOutlined /></el-icon>
        </div>
      </div>
      <div class="sc-card__driver-info">
        <h3 class="sc-card__name" :title="item.driverName">
          {{ item.driverName || '—' }}
        </h3>
        <p class="sc-card__phone">{{ item.driverPhone || '—' }}</p>
        <p class="sc-card__affiliation" :title="item.socialCode">
          {{ item.socialCode || '—' }}
        </p>
      </div>
    </section>

    <!-- L3 车辆 -->
    <section class="sc-card__vehicle">
      <div
        v-if="item.plateNumber || item.trailerPlateNumber"
        class="sc-card__plates"
      >
        <plate-number-tag
          v-if="item.plateNumber"
          size="large"
          :text="item.plateNumber"
          :category="item.plateCategory"
        />
        <template v-if="item.trailerPlateNumber">
          <span class="sc-card__plate-sep" aria-hidden="true">·</span>
          <plate-number-tag :text="item.trailerPlateNumber" />
        </template>
      </div>
      <span v-else class="sc-card__vehicle-empty">暂无车牌</span>
    </section>

    <!-- L4 其他 -->
    <footer v-if="hasMeta" class="sc-card__meta">
      <div class="sc-card__meta-tags">
        <span
          v-if="item.ratingLevel"
          class="sc-card__meta-tag sc-card__meta-tag--rating"
        >
          {{ ratingLabel }}级
        </span>
        <dict-data
          v-if="item.vehicleTypeLabel"
          type="tag"
          :code="dictCodeVehicleType"
          :model-value="item.vehicleTypeLabel"
          :component-props="{ size: 'small', effect: 'plain' }"
        />
      </div>
      <time
        v-if="item.createdAt"
        class="sc-card__meta-time"
        :datetime="item.createdAt"
      >
        {{ createdAtLabel }}
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
  import type { SocialCapacityListItem } from '@/api/capacity/social-capacity/list/model';

  const dictCodeVehicleType = DICT_CODE_VEHICLE_TYPE;

  export interface SocialCapacityCardMenuItem {
    key: string;
    title: string;
    danger?: boolean;
    divided?: boolean;
  }

  const props = defineProps<{
    item: SocialCapacityListItem;
    menuItems: SocialCapacityCardMenuItem[];
  }>();

  const emit = defineEmits<{
    (e: 'action', key: string, item: SocialCapacityListItem): void;
  }>();

  const avatarUrl = computed(() => {
    const raw = props.item.driverAvatar?.trim();
    return raw ? resolveUploadUrl(raw) : '';
  });

  const capacityStatusMeta = computed(() => {
    switch (props.item.status) {
      case 1:
        return {
          className: 'sc-card--capacity-active',
          label: '正常',
          tagType: 'success' as const
        };
      case 2:
        return {
          className: 'sc-card--capacity-disabled',
          label: '停用',
          tagType: 'warning' as const
        };
      case 3:
        return {
          className: 'sc-card--capacity-blacklist',
          label: '黑名单',
          tagType: 'danger' as const
        };
      default:
        return {
          className: 'sc-card--capacity-inactive',
          label: '未生效',
          tagType: 'info' as const
        };
    }
  });

  const approvalStatusMeta = computed(() => {
    switch (props.item.approvalStatus) {
      case 0:
        return { label: '草稿', tagType: 'info' as const };
      case 1:
        return { label: '待审核', tagType: 'warning' as const };
      case 3:
        return { label: '已驳回', tagType: 'danger' as const };
      default:
        return { label: '—', tagType: 'info' as const };
    }
  });

  const showApprovalPill = computed(() => props.item.approvalStatus !== 2);

  const statusCardClass = computed(() => capacityStatusMeta.value.className);
  const capacityStatusLabel = computed(() => capacityStatusMeta.value.label);
  const capacityStatusTagType = computed(
    () => capacityStatusMeta.value.tagType
  );
  const approvalStatusLabel = computed(() => approvalStatusMeta.value.label);
  const approvalStatusTagType = computed(
    () => approvalStatusMeta.value.tagType
  );

  const ratingLabel = computed(() => {
    switch (props.item.ratingLevel) {
      case 1:
        return 'A';
      case 2:
        return 'B';
      case 3:
        return 'C';
      case 4:
        return 'D';
      default:
        return '—';
    }
  });

  const hasMeta = computed(
    () =>
      !!props.item.ratingLevel ||
      !!props.item.vehicleTypeLabel ||
      !!props.item.createdAt
  );

  const createdAtLabel = computed(() => {
    if (!props.item.createdAt) {
      return '';
    }
    return formatDateTime(props.item.createdAt);
  });

  const onCommand = (key: string) => {
    emit('action', key, props.item);
  };
</script>

<style scoped>
  .sc-card {
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

  .sc-card:hover {
    border-color: var(--el-border-color);
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    transform: translateY(-1px);
  }

  .sc-card--capacity-active {
    --sc-accent: var(--el-color-success);
    --sc-accent-bg: var(--el-color-success-light-9);
  }

  .sc-card--capacity-disabled {
    --sc-accent: var(--el-color-warning);
    --sc-accent-bg: var(--el-color-warning-light-9);
  }

  .sc-card--capacity-blacklist {
    --sc-accent: var(--el-color-danger);
    --sc-accent-bg: var(--el-color-danger-light-9);
  }

  .sc-card--capacity-inactive {
    --sc-accent: var(--el-text-color-secondary);
    --sc-accent-bg: var(--el-fill-color-light);
  }

  /* L1 状态 */
  .sc-card__status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 10px;
    background: var(--sc-accent-bg);
    border-bottom: 1px solid var(--el-border-color-extra-light);
  }

  .sc-card__status-tags :deep(.el-tag) {
    font-weight: 600;
    border: none;
  }

  .sc-card__status-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    min-width: 0;
    flex: 1;
  }

  .sc-card__menu-btn {
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

  .sc-card__menu-btn:hover {
    background: rgba(255, 255, 255, 0.8);
    color: var(--el-text-color-primary);
  }

  .sc-card__menu-danger {
    color: var(--el-color-danger);
  }

  /* L2 驾驶员 */
  .sc-card__driver {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
  }

  .sc-card__portrait {
    flex-shrink: 0;
    width: 54px;
    aspect-ratio: 3 / 4;
    border-radius: 6px;
    overflow: hidden;
    background: var(--el-fill-color-light);
    box-shadow: inset 0 0 0 1px var(--el-border-color-lighter);
  }

  .sc-card__portrait-image {
    width: 100%;
    height: 100%;
    display: block;
  }

  .sc-card__portrait-image :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
  }

  .sc-card__portrait-placeholder {
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

  .sc-card__driver-info {
    flex: 1;
    min-width: 0;
  }

  .sc-card__name {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.35;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sc-card__phone {
    margin: 3px 0 0;
    font-size: 12px;
    line-height: 1.4;
    color: var(--el-text-color-regular);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sc-card__affiliation {
    margin: 2px 0 0;
    font-size: 12px;
    line-height: 1.4;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* L3 车辆 */
  .sc-card__vehicle {
    margin: 0 10px;
    padding: 8px 10px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
    border: 1px solid var(--el-border-color-extra-light);
  }

  .sc-card__plates {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 4px 6px;
  }

  .sc-card__plate-sep {
    font-size: 16px;
    font-weight: 700;
    line-height: 1;
    color: var(--el-text-color-placeholder);
    user-select: none;
  }

  .sc-card__vehicle-empty {
    display: block;
    text-align: center;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  /* L4 其他 */
  .sc-card__meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    margin-top: auto;
    padding: 8px 12px 10px;
  }

  .sc-card__meta-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    min-width: 0;
  }

  .sc-card__meta-tag {
    display: inline-flex;
    align-items: center;
    padding: 0 6px;
    border-radius: 4px;
    font-size: 11px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
    border: 1px solid var(--el-border-color-extra-light);
    white-space: nowrap;
  }

  .sc-card__meta-tag--rating {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary-light-8);
    font-weight: 600;
  }

  .sc-card__meta-time {
    flex-shrink: 0;
    font-size: 10px;
    color: var(--el-text-color-placeholder);
    white-space: nowrap;
  }
</style>
