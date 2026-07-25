<template>
  <div class="sc-card-wrapper" @click="handleCardClick">
    <article class="sc-card" :class="statusCardClass">
      <!-- 身份区：头像 + 姓名/手机/状态 + 更多 -->
      <header class="sc-card__header">
        <div class="sc-card__portrait">
          <el-image
            v-if="avatarUrl"
            :src="avatarUrl"
            fit="contain"
            class="sc-card__portrait-image"
          >
            <template #error>
              <div class="sc-card__portrait-placeholder">
                <el-icon :size="28"><UserOutlined /></el-icon>
              </div>
            </template>
            <template #placeholder>
              <div class="sc-card__portrait-placeholder">
                <el-icon :size="28"><UserOutlined /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-else class="sc-card__portrait-placeholder">
            <el-icon :size="28"><UserOutlined /></el-icon>
          </div>
        </div>

        <div class="sc-card__main">
          <div class="sc-card__title-row">
            <h3 class="sc-card__name" :title="item.driverName">
              {{ item.driverName || '—' }}
            </h3>
            <el-dropdown trigger="click" @command="onCommand">
              <button
                type="button"
                class="sc-card__menu-btn"
                aria-label="更多操作"
                @click.stop
              >
                <el-icon :size="16"><MoreOutlined /></el-icon>
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
          </div>
          <p class="sc-card__phone">{{ item.driverPhone || '—' }}</p>
          <div class="sc-card__badges">
            <span class="sc-card__badge">{{ capacityStatusLabel }}</span>
            <span
              v-if="showApprovalPill"
              class="sc-card__badge sc-card__badge--approval"
              :class="`sc-card__badge--approval-${approvalTone}`"
            >
              {{ approvalStatusLabel }}
            </span>
          </div>
        </div>
      </header>

      <!-- 车辆信息 -->
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
            <span class="sc-card__plate-plus">+</span>
            <plate-number-tag :text="item.trailerPlateNumber" />
          </template>
        </div>
        <span v-else class="sc-card__vehicle-empty">暂无车辆信息</span>

        <div
          v-if="item.vehicleTypeLabel || item.ratingLevel"
          class="sc-card__vehicle-tags"
        >
          <span v-if="item.ratingLevel" class="sc-card__rating">
            {{ ratingLabel }}级
          </span>
          <dict-data
            v-if="item.vehicleTypeLabel"
            type="tag"
            :code="dictCodeVehicleType"
            :model-value="item.vehicleTypeLabel"
            :component-props="{ size: 'small', type: 'info', effect: 'plain' }"
          />
        </div>
      </section>

      <!-- 底部：创建时间；编号弱化右置 -->
      <footer v-if="hasFooter" class="sc-card__footer">
        <span v-if="item.createdAt" class="sc-card__meta">
          <span class="sc-card__meta-label">创建</span>
          <span class="sc-card__meta-value">{{ createdAtLabel }}</span>
        </span>
        <span
          v-if="item.socialCode"
          class="sc-card__code"
          :title="item.socialCode"
        >
          {{ item.socialCode }}
        </span>
      </footer>
    </article>
  </div>
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
          label: '正常'
        };
      case 2:
        return {
          className: 'sc-card--capacity-disabled',
          label: '停用'
        };
      case 3:
        return {
          className: 'sc-card--capacity-blacklist',
          label: '黑名单'
        };
      default:
        return {
          className: 'sc-card--capacity-inactive',
          label: '未生效'
        };
    }
  });

  const approvalStatusMeta = computed(() => {
    switch (props.item.approvalStatus) {
      case 0:
        return { label: '草稿', tone: 'info' as const };
      case 1:
        return { label: '待审核', tone: 'warning' as const };
      case 3:
        return { label: '已驳回', tone: 'danger' as const };
      default:
        return { label: '—', tone: 'info' as const };
    }
  });

  const showApprovalPill = computed(() => props.item.approvalStatus !== 2);

  const statusCardClass = computed(() => capacityStatusMeta.value.className);
  const capacityStatusLabel = computed(() => capacityStatusMeta.value.label);
  const approvalStatusLabel = computed(() => approvalStatusMeta.value.label);
  const approvalTone = computed(() => approvalStatusMeta.value.tone);

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

  const hasFooter = computed(
    () => !!props.item.createdAt || !!props.item.socialCode
  );

  const createdAtLabel = computed(() => {
    if (!props.item.createdAt) return '';
    return formatDateTime(props.item.createdAt);
  });

  const handleCardClick = (e: MouseEvent) => {
    if ((e.target as HTMLElement).closest('.el-dropdown')) {
      return;
    }
    emit('action', 'view', props.item);
  };

  const onCommand = (key: string) => {
    emit('action', key, props.item);
  };
</script>

<style scoped>
  .sc-card-wrapper {
    height: 100%;
    cursor: pointer;
  }

  .sc-card {
    --sc-accent: var(--el-color-primary);
    --sc-soft-bg: var(--el-color-primary-light-9);
    --sc-soft-ring: var(--el-color-primary-light-7);

    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 12px 12px 0;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    box-sizing: border-box;
    overflow: hidden;
    position: relative;
    transform-origin: center center;
    transition:
      border-color 0.2s cubic-bezier(0.23, 1, 0.32, 1),
      box-shadow 0.2s cubic-bezier(0.23, 1, 0.32, 1),
      background 0.2s cubic-bezier(0.23, 1, 0.32, 1),
      transform 0.16s cubic-bezier(0.23, 1, 0.32, 1);
  }

  .sc-card--capacity-active {
    --sc-accent: var(--el-color-success);
    --sc-soft-bg: var(--el-color-success-light-9);
    --sc-soft-ring: var(--el-color-success-light-7);
  }

  .sc-card--capacity-disabled {
    --sc-accent: var(--el-color-warning);
    --sc-soft-bg: var(--el-color-warning-light-9);
    --sc-soft-ring: var(--el-color-warning-light-7);
  }

  .sc-card--capacity-blacklist {
    --sc-accent: var(--el-color-danger);
    --sc-soft-bg: var(--el-color-danger-light-9);
    --sc-soft-ring: var(--el-color-danger-light-7);
  }

  .sc-card--capacity-inactive {
    --sc-accent: #64748b;
    --sc-soft-bg: rgba(100, 116, 139, 0.1);
    --sc-soft-ring: rgba(100, 116, 139, 0.28);
  }

  @media (hover: hover) and (pointer: fine) {
    .sc-card-wrapper:hover .sc-card {
      border-color: var(--sc-accent);
      background: color-mix(in srgb, var(--sc-soft-bg) 55%, var(--el-bg-color));
      box-shadow:
        0 0 0 1px var(--sc-soft-ring),
        0 8px 20px rgba(15, 23, 42, 0.07);
      transform: translateY(-2px);
    }

    .sc-card-wrapper:active .sc-card {
      transform: scale(0.985);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .sc-card {
      transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease;
    }

    .sc-card-wrapper:hover .sc-card,
    .sc-card-wrapper:active .sc-card {
      transform: none;
    }
  }

  /* —— Header —— */
  .sc-card__header {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    min-width: 0;
    margin-bottom: 10px;
  }

  .sc-card__portrait {
    flex-shrink: 0;
    width: 64px;
    aspect-ratio: 3 / 4;
    border-radius: 10px;
    overflow: hidden;
    background: linear-gradient(
      160deg,
      color-mix(in srgb, var(--sc-accent) 8%, var(--el-fill-color-light)),
      var(--el-fill-color-light)
    );
    box-shadow: inset 0 0 0 1px var(--el-border-color-extra-light);
  }

  .sc-card__portrait-image {
    width: 100%;
    height: 100%;
    display: block;
  }

  .sc-card__portrait-image :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center center;
  }

  .sc-card__portrait-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: color-mix(
      in srgb,
      var(--sc-accent) 45%,
      var(--el-text-color-placeholder)
    );
  }

  .sc-card__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 3px;
  }

  .sc-card__title-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 4px;
    width: 100%;
    min-width: 0;
  }

  .sc-card__name {
    margin: 0;
    min-width: 0;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.01em;
    line-height: 1.3;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sc-card__menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    margin: -4px -4px 0 0;
    padding: 0;
    border: none;
    border-radius: 7px;
    background: transparent;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    flex-shrink: 0;
    transition:
      background 0.16s cubic-bezier(0.23, 1, 0.32, 1),
      color 0.16s cubic-bezier(0.23, 1, 0.32, 1),
      transform 0.16s cubic-bezier(0.23, 1, 0.32, 1);
  }

  .sc-card__menu-btn:hover {
    background: var(--el-fill-color);
    color: var(--el-text-color-primary);
  }

  .sc-card__menu-btn:active {
    transform: scale(0.97);
  }

  .sc-card__menu-danger {
    color: var(--el-color-danger);
  }

  .sc-card__phone {
    margin: 0;
    font-size: 12px;
    line-height: 1.35;
    color: var(--el-text-color-secondary);
    font-variant-numeric: tabular-nums;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  }

  .sc-card__badges {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
    margin-top: 2px;
  }

  .sc-card__badge {
    display: inline-flex;
    align-items: center;
    padding: 1px 7px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.45;
    color: var(--sc-accent);
    background: color-mix(in srgb, var(--sc-accent) 12%, transparent);
    white-space: nowrap;
  }

  .sc-card__badge--approval-info {
    color: var(--el-color-info);
    background: color-mix(in srgb, var(--el-color-info) 12%, transparent);
  }

  .sc-card__badge--approval-warning {
    color: var(--el-color-warning);
    background: color-mix(in srgb, var(--el-color-warning) 12%, transparent);
  }

  .sc-card__badge--approval-danger {
    color: var(--el-color-danger);
    background: color-mix(in srgb, var(--el-color-danger) 12%, transparent);
  }

  /* —— Vehicle —— */
  .sc-card__vehicle {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    min-height: 0;
    padding-bottom: 10px;
  }

  .sc-card__plates {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
  }

  .sc-card__plate-plus {
    color: var(--el-text-color-secondary);
    font-weight: 700;
    font-size: 13px;
    flex-shrink: 0;
  }

  .sc-card__vehicle-empty {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  .sc-card__vehicle-tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
  }

  .sc-card__rating {
    display: inline-flex;
    align-items: center;
    padding: 0 6px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    line-height: 1.6;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-8);
  }

  /* —— Footer —— */
  .sc-card__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: auto;
    margin-left: -12px;
    margin-right: -12px;
    padding: 8px 12px;
    border-top: 1px solid var(--el-border-color-extra-light);
    background: color-mix(
      in srgb,
      var(--el-fill-color-extra-light) 80%,
      transparent
    );
  }

  .sc-card__meta {
    display: inline-flex;
    align-items: baseline;
    gap: 4px;
    min-width: 0;
  }

  .sc-card__meta-label {
    flex-shrink: 0;
    font-size: 11px;
    color: var(--el-text-color-placeholder);
  }

  .sc-card__meta-value {
    font-size: 11px;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sc-card__code {
    flex-shrink: 1;
    max-width: 48%;
    font-size: 11px;
    color: var(--el-text-color-placeholder);
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
