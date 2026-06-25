<template>
  <div class="capacity-card-wrapper" @click="handleCardClick">
    <article class="capacity-card" :class="statusCardClass" ref="cardRef">
      <!-- Header: Driver & Status -->
      <header class="capacity-card__header">
        <div class="capacity-card__driver">
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
            <div class="capacity-card__name-wrapper">
              <h3 class="capacity-card__name" :title="item.driverName">{{ item.driverName || '—' }}</h3>
              <div class="capacity-card__status">
                <span class="capacity-card__status-dot"></span>
                {{ statusLabel }}
              </div>
            </div>
            <div class="capacity-card__desc">
              <span class="capacity-card__phone">{{ item.driverPhone || '—' }}</span>
              <template v-if="item.departmentName">
                <span class="capacity-card__divider"></span>
                <span class="capacity-card__dept" :title="item.departmentName">{{ item.departmentName }}</span>
              </template>
            </div>
          </div>
        </div>
        <el-dropdown trigger="click" @command="onCommand">
          <button
            type="button"
            class="capacity-card__menu-btn"
            aria-label="更多操作"
            @click.stop
          >
            <el-icon :size="16"><MoreOutlined /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="target in manualTargets"
                :key="target.value"
                :command="`status:${target.value}`"
              >
                {{ target.label }}
              </el-dropdown-item>
              <el-dropdown-item v-if="lockedHint" disabled>
                {{ lockedHint }}
              </el-dropdown-item>
              <el-dropdown-item command="unbind" divided>
                <span class="capacity-card__menu-danger">下车</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </header>

      <!-- Body: Vehicle Info -->
      <section class="capacity-card__body">
        <div class="capacity-card__vehicle">
          <div v-if="item.plateNumber || item.trailerPlateNumber" class="capacity-card__plates">
            <div class="capacity-card__plate-group">
              <plate-number-tag
                v-if="item.plateNumber"
                :text="item.plateNumber"
                :category="item.plateCategory"
                size="large"
              />
              <template v-if="item.trailerPlateNumber">
                <span class="capacity-card__plate-plus">+</span>
                <plate-number-tag
                  :text="item.trailerPlateNumber"
                  :category="item.trailerPlateCategory"
                  size="large"
                />
              </template>
            </div>
          </div>
          <span v-else class="capacity-card__vehicle-empty">暂无车辆信息</span>
          
          <div class="capacity-card__vehicle-tags" v-if="item.vehicleType">
            <dict-data
              type="tag"
              :code="dictCodeVehicleType"
              :model-value="item.vehicleType"
              :component-props="{ size: 'small', type: 'info', effect: 'plain' }"
            />
          </div>
        </div>
      </section>

      <!-- Footer: Meta Info -->
      <footer class="capacity-card__footer" v-if="hasMeta">
        <span class="capacity-card__time" v-if="item.boundAt">
          {{ boundAtLabel }}
        </span>
      </footer>
    </article>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
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
    (e: 'change-status', payload: { item: Capacity; status: number }): void;
    (e: 'detail', item: Capacity, el: HTMLElement): void;
  }>();

  const cardRef = ref<HTMLElement | null>(null);

  const handleCardClick = (e: MouseEvent) => {
    // 忽略下拉菜单的点击
    if ((e.target as HTMLElement).closest('.el-dropdown')) {
      return;
    }
    if (!cardRef.value) return;
    emit('detail', props.item, cardRef.value);
  };

  const avatarUrl = computed(() => {
    const raw = props.item.driverAvatar?.trim();
    return raw ? resolveUploadUrl(raw) : '';
  });

  /** 运力运营状态 1-可接单 2-运输中 3-休假 4-停运 5-维修保养 */
  const statusMeta = computed(() => {
    switch (props.item.operationStatus) {
      case 1:
        return { className: 'capacity-card--op-available', label: '可接单' };
      case 2:
        return { className: 'capacity-card--op-intask', label: '运输中' };
      case 3:
        return { className: 'capacity-card--op-resting', label: '休假' };
      case 4:
        return { className: 'capacity-card--op-stopped', label: '停运' };
      case 5:
        return { className: 'capacity-card--op-maintenance', label: '维修保养中' };
      default:
        return { className: 'capacity-card--op-unknown', label: '状态未知' };
    }
  });

  const statusCardClass = computed(() => statusMeta.value.className);
  const statusLabel = computed(() => statusMeta.value.label);

  /** 可手动切换的目标状态（运输中/维修保养由上游模块管理，不提供手动入口） */
  const MANUAL_TARGETS: Record<number, { value: number; label: string }[]> = {
    1: [
      { value: 3, label: '置为休假' },
      { value: 4, label: '置为停运' }
    ],
    3: [
      { value: 1, label: '恢复可接单' },
      { value: 4, label: '置为停运' }
    ],
    4: [
      { value: 1, label: '恢复可接单' },
      { value: 3, label: '置为休假' }
    ]
  };

  const manualTargets = computed(
    () => MANUAL_TARGETS[props.item.operationStatus ?? 0] ?? []
  );

  const lockedHint = computed(() => {
    if (props.item.operationStatus === 2) return '运输中（由任务单管理）';
    if (props.item.operationStatus === 5) return '维修保养中（由维修模块管理）';
    return '';
  });

  const hasMeta = computed(
    () => !!props.item.boundAt
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
      return;
    }
    if (command.startsWith('status:')) {
      const status = Number(command.slice('status:'.length));
      if (Number.isFinite(status)) {
        emit('change-status', { item: props.item, status });
      }
    }
  };
</script>

<style scoped>
  .capacity-card-wrapper {
    height: 100%;
    cursor: pointer;
  }

  .capacity-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    box-sizing: border-box;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    transform-origin: center center;
  }

  .capacity-card-wrapper:hover .capacity-card {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
  }

  /* 顶部状态条，用细线表示 */
  .capacity-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--capacity-accent);
    z-index: 1;
  }

  /* 状态色 */
  .capacity-card--op-available { --capacity-accent: var(--el-color-success); }
  .capacity-card--op-intask { --capacity-accent: var(--el-color-primary); }
  .capacity-card--op-resting { --capacity-accent: var(--el-text-color-secondary); }
  .capacity-card--op-stopped { --capacity-accent: var(--el-color-danger); }
  .capacity-card--op-maintenance { --capacity-accent: var(--el-color-warning); }
  .capacity-card--op-unknown { --capacity-accent: var(--el-text-color-placeholder); }

  /* Header */
  .capacity-card__header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 16px 16px 12px;
  }

  .capacity-card__driver {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }

  .capacity-card__portrait {
    flex-shrink: 0;
    width: 60px;
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
    background: var(--el-fill-color-light);
  }

  .capacity-card__driver-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .capacity-card__name-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .capacity-card__name {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .capacity-card__status {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    background: color-mix(in srgb, var(--capacity-accent) 10%, transparent);
    color: var(--capacity-accent);
  }

  .capacity-card__status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .capacity-card__desc {
    display: flex;
    align-items: center;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .capacity-card__phone {
    font-family: var(--el-font-family);
  }

  .capacity-card__divider {
    width: 1px;
    height: 10px;
    background: var(--el-border-color);
    margin: 0 8px;
  }

  .capacity-card__dept {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .capacity-card__menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    padding: 0;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.2s;
    margin-left: 8px;
  }

  .capacity-card__menu-btn:hover {
    background: var(--el-fill-color-light);
    color: var(--el-text-color-primary);
  }

  /* Body */
  .capacity-card__body {
    padding: 0 16px 12px;
    flex: 1;
  }

  .capacity-card__vehicle {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .capacity-card__plates {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .capacity-card__plate-group {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: 8px;
  }

  .capacity-card__plate-plus {
    color: var(--el-text-color-secondary);
    font-weight: bold;
    font-size: 16px;
    flex-shrink: 0;
  }

  .capacity-card__vehicle-empty {
    font-size: 13px;
    color: var(--el-text-color-placeholder);
  }

  .capacity-card__vehicle-tags {
    display: flex;
    align-items: center;
  }

  /* Footer */
  .capacity-card__footer {
    padding: 10px 16px;
    border-top: 1px dashed var(--el-border-color-lighter);
    background: var(--el-fill-color-extra-light);
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
  }

  .capacity-card__time {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
