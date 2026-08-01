<template>
  <div
    class="capacity-card-wrapper"
    :class="{ 'is-expanded': expanded }"
    @click="handleCardClick"
  >
    <Motion
      as="article"
      class="capacity-card"
      :class="[statusCardClass, { 'is-expanded': expanded }]"
      :layout-id="layoutId"
      :transition="layoutTransition"
      :crossfade="true"
    >
      <!-- 身份区：头像 + 姓名/状态并排；手机与车牌左对齐 -->
      <header class="capacity-card__header">
        <div class="capacity-card__portrait">
          <el-image
            v-if="avatarUrl"
            :src="avatarUrl"
            fit="contain"
            class="capacity-card__portrait-image"
          >
            <template #error>
              <div class="capacity-card__portrait-placeholder">
                <el-icon :size="28"><UserOutlined /></el-icon>
              </div>
            </template>
            <template #placeholder>
              <div class="capacity-card__portrait-placeholder">
                <el-icon :size="28"><UserOutlined /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-else class="capacity-card__portrait-placeholder">
            <el-icon :size="28"><UserOutlined /></el-icon>
          </div>
        </div>

        <div class="capacity-card__main">
          <div class="capacity-card__identity">
            <div class="capacity-card__title-row">
              <div class="capacity-card__title-left">
                <h3 class="capacity-card__name" :title="item.driverName">
                  {{ item.driverName || '—' }}
                </h3>
                <span class="capacity-card__badge">{{ statusLabel }}</span>
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
            </div>
            <p class="capacity-card__phone">{{ item.driverPhone || '—' }}</p>
          </div>
          <div
            v-if="item.plateNumber || item.trailerPlateNumber"
            class="capacity-card__plates"
          >
            <plate-number-tag
              v-if="item.plateNumber"
              :text="item.plateNumber"
              :category="item.plateCategory"
            />
            <span
              v-if="item.trailerPlateNumber"
              class="capacity-card__trailer-mark"
              title="已绑定挂车，完整车牌见详情"
            >
              挂
            </span>
          </div>
        </div>
      </header>

      <!-- 车型 / 无车辆时的空态 -->
      <section
        v-if="item.vehicleType || (!item.plateNumber && !item.trailerPlateNumber)"
        class="capacity-card__vehicle"
      >
        <div v-if="item.vehicleType" class="capacity-card__vehicle-type">
          <dict-data
            type="tag"
            :code="dictCodeVehicleType"
            :model-value="item.vehicleType"
            :component-props="{ size: 'small', type: 'info', effect: 'plain' }"
          />
        </div>
        <span v-else class="capacity-card__vehicle-empty">暂无车辆信息</span>
      </section>

      <!-- 底部：上车时间（强调）；部门弱化尾注 -->
      <footer v-if="hasFooter" class="capacity-card__footer">
        <span v-if="item.boundAt" class="capacity-card__meta">
          <span class="capacity-card__meta-label">上车</span>
          <span class="capacity-card__meta-value" :title="boundAtFullLabel">
            {{ boundAtLabel }}
          </span>
        </span>
        <span
          v-if="item.departmentName"
          class="capacity-card__dept"
          :title="item.departmentName"
        >
          {{ item.departmentName }}
        </span>
      </footer>
    </Motion>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import dayjs from 'dayjs';
  import { Motion } from 'motion-v';
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
    /** 当前是否展开为详情（共享 layoutId） */
    expanded?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'unbind', item: Capacity): void;
    (e: 'change-status', payload: { item: Capacity; status: number }): void;
    (e: 'detail', item: Capacity): void;
  }>();

  const layoutTransition = {
    type: 'spring' as const,
    bounce: 0,
    duration: 0.32
  };

  /** 始终挂 layoutId，供详情面板 shared layout 形变起止 */
  const layoutId = computed(() =>
    props.item.id != null ? `capacity-shell-${props.item.id}` : undefined
  );

  const handleCardClick = (e: MouseEvent) => {
    if ((e.target as HTMLElement).closest('.el-dropdown')) {
      return;
    }
    emit('detail', props.item);
  };

  const avatarUrl = computed(() => {
    const raw = props.item.driverAvatar?.trim();
    return raw ? resolveUploadUrl(raw) : '';
  });

  /** 运力运营状态 1-空闲 2-运输中 3-休假 4-停运 5-维修保养 */
  const statusMeta = computed(() => {
    switch (props.item.operationStatus) {
      case 1:
        return { className: 'capacity-card--op-available', label: '空闲' };
      case 2:
        return { className: 'capacity-card--op-intask', label: '运输中' };
      case 3:
        return { className: 'capacity-card--op-resting', label: '休假' };
      case 4:
        return { className: 'capacity-card--op-stopped', label: '停运' };
      case 5:
        return {
          className: 'capacity-card--op-maintenance',
          label: '维修保养中'
        };
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
      { value: 1, label: '置为空闲' },
      { value: 4, label: '置为停运' }
    ],
    4: [
      { value: 1, label: '置为空闲' },
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

  const hasFooter = computed(
    () => !!props.item.boundAt || !!props.item.departmentName
  );

  /** 列表展示精确到分钟，完整时分秒放 title */
  const boundAtLabel = computed(() => {
    if (!props.item.boundAt) return '';
    const d = dayjs(props.item.boundAt);
    return d.isValid() ? d.format('YYYY-MM-DD HH:mm') : String(props.item.boundAt);
  });

  const boundAtFullLabel = computed(() => {
    if (!props.item.boundAt) return '';
    return formatDateTime(props.item.boundAt);
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

  .capacity-card-wrapper.is-expanded {
    pointer-events: none;
  }

  .capacity-card {
    --capacity-accent: var(--el-color-primary);
    --capacity-soft-bg: var(--el-color-primary-light-9);
    --capacity-soft-ring: var(--el-color-primary-light-7);

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

  .capacity-card.is-expanded {
    opacity: 0;
  }

  .capacity-card--op-available {
    --capacity-accent: var(--el-color-success);
    --capacity-soft-bg: var(--el-color-success-light-9);
    --capacity-soft-ring: var(--el-color-success-light-7);
  }
  .capacity-card--op-intask {
    --capacity-accent: var(--el-color-primary);
    --capacity-soft-bg: var(--el-color-primary-light-9);
    --capacity-soft-ring: var(--el-color-primary-light-7);
  }
  .capacity-card--op-resting {
    --capacity-accent: #64748b;
    --capacity-soft-bg: rgba(100, 116, 139, 0.1);
    --capacity-soft-ring: rgba(100, 116, 139, 0.28);
  }
  .capacity-card--op-stopped {
    --capacity-accent: var(--el-color-danger);
    --capacity-soft-bg: var(--el-color-danger-light-9);
    --capacity-soft-ring: var(--el-color-danger-light-7);
  }
  .capacity-card--op-maintenance {
    --capacity-accent: var(--el-color-warning);
    --capacity-soft-bg: var(--el-color-warning-light-9);
    --capacity-soft-ring: var(--el-color-warning-light-7);
  }
  .capacity-card--op-unknown {
    --capacity-accent: var(--el-text-color-placeholder);
    --capacity-soft-bg: var(--el-fill-color-light);
    --capacity-soft-ring: var(--el-border-color);
  }

  @media (hover: hover) and (pointer: fine) {
    .capacity-card-wrapper:not(.is-expanded):hover .capacity-card {
      border-color: var(--capacity-accent);
      background: color-mix(
        in srgb,
        var(--capacity-soft-bg) 55%,
        var(--el-bg-color)
      );
      box-shadow:
        0 0 0 1px var(--capacity-soft-ring),
        0 8px 20px rgba(15, 23, 42, 0.07);
      transform: translateY(-2px);
    }

    .capacity-card-wrapper:not(.is-expanded):active .capacity-card {
      transform: scale(0.985);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .capacity-card {
      transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease;
    }

    .capacity-card-wrapper:not(.is-expanded):hover .capacity-card,
    .capacity-card-wrapper:not(.is-expanded):active .capacity-card {
      transform: none;
    }
  }

  /* —— Header —— */
  .capacity-card__header {
    display: flex;
    align-items: stretch;
    gap: 10px;
    min-width: 0;
    margin-bottom: 8px;
  }

  .capacity-card__portrait {
    flex-shrink: 0;
    align-self: flex-start;
    width: 64px;
    aspect-ratio: 3 / 4;
    border-radius: 10px;
    overflow: hidden;
    background: linear-gradient(
      160deg,
      color-mix(in srgb, var(--capacity-accent) 8%, var(--el-fill-color-light)),
      var(--el-fill-color-light)
    );
    box-shadow: inset 0 0 0 1px var(--el-border-color-extra-light);
  }

  .capacity-card__portrait-image {
    width: 100%;
    height: 100%;
    display: block;
  }

  .capacity-card__portrait-image :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center center;
  }

  .capacity-card__portrait-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: color-mix(
      in srgb,
      var(--capacity-accent) 45%,
      var(--el-text-color-placeholder)
    );
  }

  .capacity-card__main {
    flex: 1;
    min-width: 0;
    /* 与左侧照片同高：身份组顶对齐，车牌底对齐 */
    min-height: calc(64px * 4 / 3);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: space-between;
  }

  .capacity-card__identity {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 3px;
    width: 100%;
    min-width: 0;
  }

  .capacity-card__plates {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    max-width: 100%;
  }

  .capacity-card__plates :deep(.plate-number-tag) {
    max-width: 100%;
  }

  .capacity-card__trailer-mark {
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    height: 18px;
    padding: 0 4px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: 0.02em;
    color: var(--el-color-warning-dark-2, #b88230);
    background: var(--el-color-warning-light-9);
    border: 1px solid
      color-mix(in srgb, var(--el-color-warning) 35%, transparent);
  }

  .capacity-card__title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
    width: 100%;
    min-width: 0;
  }

  .capacity-card__title-left {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
    flex: 1;
  }

  .capacity-card__name {
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

  .capacity-card__menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    margin: 0 -4px 0 0;
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

  .capacity-card__menu-btn:hover {
    background: var(--el-fill-color);
    color: var(--el-text-color-primary);
  }

  .capacity-card__menu-btn:active {
    transform: scale(0.97);
  }

  .capacity-card__menu-danger {
    color: var(--el-color-danger);
  }

  .capacity-card__phone {
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

  .capacity-card__badge {
    display: inline-flex;
    align-items: center;
    flex-shrink: 0;
    padding: 1px 7px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.45;
    color: var(--capacity-accent);
    background: color-mix(in srgb, var(--capacity-accent) 12%, transparent);
    white-space: nowrap;
  }

  /* —— Vehicle —— */
  .capacity-card__vehicle {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-height: 0;
    padding-bottom: 8px;
  }

  .capacity-card__vehicle-empty {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  .capacity-card__vehicle-type {
    display: flex;
    align-items: center;
  }

  /* —— Footer —— */
  .capacity-card__footer {
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

  .capacity-card__meta {
    display: inline-flex;
    align-items: baseline;
    gap: 5px;
    min-width: 0;
  }

  .capacity-card__meta-label {
    flex-shrink: 0;
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-secondary);
  }

  .capacity-card__meta-value {
    font-size: 12px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .capacity-card__dept {
    flex-shrink: 1;
    max-width: 36%;
    font-size: 11px;
    color: var(--el-text-color-placeholder);
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
