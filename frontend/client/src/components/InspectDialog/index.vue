<!--
  只读检查弹框壳（InspectDialog）
  居中聚焦、毛玻璃顶栏、分组画布，进出沿同一条缩放路径。
  规范见 doc/04.开发手册/18.只读检查弹框规范.md
-->
<template>
  <el-dialog
    :model-value="visible"
    :width="width"
    align-center
    append-to-body
    :destroy-on-close="destroyOnClose"
    :close-on-click-modal="true"
    :show-close="false"
    :class="['wbi-dialog', dialogClass]"
    modal-class="wbi-overlay"
    @update:model-value="onVisible"
  >
    <template #header>
      <div class="wbi-chrome">
        <div class="wbi-chrome__titles">
          <h2 class="wbi-chrome__title">{{ title }}</h2>
          <div
            v-if="subtitle || $slots['header-extra']"
            class="wbi-chrome__sub"
          >
            <span v-if="subtitle" class="wbi-chrome__id">
              <span class="wbi-chrome__subtitle">{{ subtitle }}</span>
              <inspect-copy-button
                v-if="copyableSubtitle"
                :text="subtitle"
                :success-tip="copySubtitleSuccess"
                :empty-tip="copySubtitleEmpty"
                :aria-label="copySubtitleLabel"
              />
            </span>
            <slot name="header-extra" />
          </div>
        </div>
        <button
          type="button"
          class="wbi-close"
          aria-label="关闭"
          @click="onVisible(false)"
        >
          <el-icon :size="14"><Close /></el-icon>
        </button>
      </div>
    </template>

    <div v-loading="loading" class="wbi-body">
      <slot />
    </div>

    <template v-if="$slots.footer" #footer>
      <div class="wbi-footer">
        <slot name="footer" />
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { Close } from '@element-plus/icons-vue';
  import InspectCopyButton from './copy-button.vue';

  defineOptions({ name: 'InspectDialog' });

  withDefaults(
    defineProps<{
      visible: boolean;
      title: string;
      subtitle?: string;
      copyableSubtitle?: boolean;
      copySubtitleSuccess?: string;
      copySubtitleEmpty?: string;
      copySubtitleLabel?: string;
      width?: string;
      loading?: boolean;
      destroyOnClose?: boolean;
      dialogClass?: string;
    }>(),
    {
      subtitle: '',
      copyableSubtitle: false,
      copySubtitleSuccess: '已复制',
      copySubtitleEmpty: '没有可复制的内容',
      copySubtitleLabel: '复制',
      width: '760px',
      loading: false,
      destroyOnClose: true,
      dialogClass: ''
    }
  );

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  const onVisible = (v: boolean) => emit('update:visible', v);
</script>

<style lang="scss">
  .wbi-overlay {
    background: rgba(0, 0, 0, 0.36) !important;
    backdrop-filter: blur(10px) saturate(140%);
  }

  .wbi-overlay.dialog-fade-enter-active {
    animation: wbi-overlay-in 0.35s ease-out !important;
  }

  .wbi-overlay.dialog-fade-leave-active {
    animation: wbi-overlay-out 0.28s ease-in !important;
  }

  .wbi-overlay.dialog-fade-enter-active .wbi-dialog {
    animation: wbi-dialog-in 0.4s cubic-bezier(0.32, 0.72, 0, 1);
  }

  .wbi-overlay.dialog-fade-leave-active .wbi-dialog {
    animation: wbi-dialog-out 0.28s cubic-bezier(0.32, 0.72, 0, 1);
  }

  .wbi-dialog.el-dialog {
    --wbi-ink: #1c1c1e;
    --wbi-secondary: #6e6e73;
    --wbi-canvas: #f5f5f7;
    --wbi-surface: #ffffff;
    --wbi-line: rgba(60, 60, 67, 0.12);
    --wbi-radius: 16px;
    --wbi-radius-inner: 12px;
    padding: 0;
    border-radius: var(--wbi-radius);
    overflow: hidden;
    background: var(--wbi-canvas);
    box-shadow:
      0 20px 50px rgba(0, 0, 0, 0.16),
      0 2px 8px rgba(0, 0, 0, 0.06);
    max-width: calc(100vw - 32px);
    max-height: calc(100vh - 48px);
    display: flex;
    flex-direction: column;
  }

  .wbi-dialog .el-dialog__header {
    margin: 0;
    padding: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  }

  .wbi-dialog .el-dialog__body {
    padding: 16px 20px 20px;
    background: var(--wbi-canvas);
    overflow: auto;
    flex: 1;
    min-height: 0;
    max-height: min(68vh, 720px);
  }

  .wbi-dialog .el-dialog__footer {
    padding: 0;
  }

  .wbi-chrome {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    padding: 16px 18px 14px 20px;
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(20px) saturate(180%);
  }

  .wbi-chrome__titles {
    min-width: 0;
    padding-right: 8px;
  }

  .wbi-chrome__title {
    margin: 0;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.2;
    color: var(--wbi-ink);
  }

  .wbi-chrome__sub {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
  }

  .wbi-chrome__id {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    min-width: 0;
  }

  .wbi-chrome__subtitle {
    font-size: 13px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    color: var(--wbi-secondary);
    letter-spacing: 0.01em;
  }

  .wbi-copy {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    padding: 0;
    border: none;
    border-radius: 6px;
    color: var(--wbi-secondary);
    background: transparent;
    cursor: pointer;
    transition:
      background 150ms ease,
      transform 100ms ease-out,
      color 150ms ease;
  }

  .wbi-copy:hover {
    color: var(--wbi-ink);
    background: rgba(120, 120, 128, 0.12);
  }

  .wbi-copy:active {
    transform: scale(0.94);
  }

  .wbi-copy:focus-visible {
    outline: 2px solid var(--el-color-primary);
    outline-offset: 2px;
  }

  .wbi-close {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border: none;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--wbi-ink);
    background: rgba(120, 120, 128, 0.16);
    cursor: pointer;
    transition:
      transform 100ms ease-out,
      background 150ms ease;
  }

  .wbi-close:hover {
    background: rgba(120, 120, 128, 0.24);
  }

  .wbi-close:active {
    transform: scale(0.94);
  }

  .wbi-close:focus-visible {
    outline: 2px solid var(--el-color-primary);
    outline-offset: 2px;
  }

  .wbi-body {
    min-height: 160px;
  }

  .wbi-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 12px 20px 16px;
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(20px) saturate(180%);
    border-top: 1px solid rgba(255, 255, 255, 0.4);
  }

  .wbi-footer .el-button:active {
    transform: scale(0.97);
    transition: transform 100ms ease-out;
  }

  .wbi-hero {
    padding: 18px 18px 16px;
    border-radius: var(--wbi-radius-inner);
    background: var(--wbi-surface);
    border: 1px solid var(--wbi-line);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .wbi-hero__who {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.015em;
    color: var(--wbi-ink);
    line-height: 1.35;
  }

  .wbi-hero__route {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 14px;
  }

  .wbi-hero__end {
    min-width: 0;
    flex: 1;
  }

  .wbi-hero__end--to {
    text-align: right;
  }

  .wbi-hero__kicker {
    display: block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: none;
    color: var(--wbi-secondary);
    margin-bottom: 4px;
  }

  .wbi-hero__city {
    display: block;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.3;
    color: var(--wbi-ink);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .wbi-hero__spine {
    flex: 0 0 56px;
    height: 10px;
    position: relative;
  }

  .wbi-hero__rail {
    position: absolute;
    left: 0;
    right: 0;
    top: 4px;
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(
      90deg,
      rgba(60, 60, 67, 0.18),
      rgba(60, 60, 67, 0.45)
    );
  }

  .wbi-hero__rail::after {
    content: '';
    position: absolute;
    right: -1px;
    top: -3px;
    border: 4px solid transparent;
    border-left-color: rgba(60, 60, 67, 0.5);
  }

  .wbi-hero__stamp {
    flex-shrink: 0;
    min-width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: var(--el-color-primary);
    color: #fff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.16);
  }

  .wbi-hero__stamp-num {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }

  .wbi-hero__stamp-unit {
    margin-top: 3px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.04em;
    opacity: 0.88;
  }

  .wbi-hero--freight .wbi-hero__amount-row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    margin-top: 12px;
  }

  .wbi-hero__amount {
    margin-top: 2px;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--wbi-ink);
    font-variant-numeric: tabular-nums;
  }

  .wbi-section {
    margin-top: 18px;
  }

  .wbi-section__title {
    margin: 0 4px 8px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--wbi-secondary);
  }

  .wbi-group {
    background: var(--wbi-surface);
    border-radius: var(--wbi-radius-inner);
    border: 1px solid var(--wbi-line);
    overflow: hidden;
  }

  .wbi-group .el-empty {
    padding: 20px 0;
  }

  .wbi-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--wbi-line);
  }

  .wbi-row:last-child {
    border-bottom: none;
  }

  .wbi-row__label {
    flex-shrink: 0;
    font-size: 13px;
    color: var(--wbi-secondary);
    line-height: 1.45;
  }

  .wbi-row__value {
    min-width: 0;
    text-align: right;
    font-size: 13px;
    font-weight: 500;
    color: var(--wbi-ink);
    line-height: 1.45;
    word-break: break-word;
  }

  .wbi-row__value--muted {
    font-weight: 400;
    color: var(--wbi-secondary);
  }

  .wbi-note {
    margin-top: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 12px;
    line-height: 1.5;
    color: var(--wbi-secondary);
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid var(--wbi-line);
  }

  .wbi-vehicle {
    display: flex;
    gap: 12px;
    padding: 12px 14px;
    border-bottom: 1px solid var(--wbi-line);
  }

  .wbi-vehicle:last-child {
    border-bottom: none;
  }

  .wbi-vehicle__thumb {
    position: relative;
    flex-shrink: 0;
    width: 88px;
    height: 60px;
    border-radius: 8px;
    overflow: hidden;
    background: var(--wbi-canvas);
  }

  .wbi-vehicle__img {
    width: 88px;
    height: 60px;
    display: block;
  }

  .wbi-vehicle__ph {
    width: 88px;
    height: 60px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    color: var(--el-text-color-placeholder);
    font-size: 10px;
    background: var(--wbi-canvas);
  }

  .wbi-vehicle__qty {
    position: absolute;
    right: 4px;
    bottom: 4px;
    padding: 1px 6px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    color: #fff;
    background: rgba(28, 28, 30, 0.62);
    backdrop-filter: blur(6px);
  }

  .wbi-vehicle__info {
    min-width: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
  }

  .wbi-vehicle__name {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--wbi-ink);
    line-height: 1.35;
  }

  .wbi-vehicle__vin {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    max-width: 100%;
    font-size: 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    color: var(--wbi-secondary);
  }

  .wbi-vehicle__vin-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .wbi-card {
    padding: 14px 16px;
    border-bottom: 1px solid var(--wbi-line);
  }

  .wbi-card:last-child {
    border-bottom: none;
  }

  .wbi-card__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 8px;
  }

  .wbi-card__id {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    min-width: 0;
  }

  .wbi-card__no {
    font-size: 15px;
    font-weight: 600;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    color: var(--wbi-ink);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .wbi-card__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    margin-bottom: 10px;
    font-size: 13px;
    color: var(--wbi-secondary);
  }

  .wbi-card__meta-strong {
    color: var(--el-color-primary);
    font-weight: 600;
  }

  .wbi-chip-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .wbi-chip-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 8px;
    background: var(--wbi-canvas);
    font-size: 13px;
  }

  .wbi-chip-row__main {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--wbi-ink);
  }

  .wbi-chip-row__side {
    flex-shrink: 0;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  .wbi-card__action {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px dashed var(--wbi-line);
  }

  @media (max-width: 640px) {
    .wbi-hero__route {
      flex-wrap: wrap;
    }

    .wbi-hero__spine {
      flex-basis: 100%;
      height: 18px;
    }

    .wbi-hero__end,
    .wbi-hero__end--to {
      flex: 1 1 calc(50% - 28px);
      text-align: left;
    }

    .wbi-hero__stamp {
      margin-left: auto;
    }

    .wbi-hero__amount {
      font-size: 24px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .wbi-overlay.dialog-fade-enter-active,
    .wbi-overlay.dialog-fade-leave-active,
    .wbi-overlay.dialog-fade-enter-active .wbi-dialog,
    .wbi-overlay.dialog-fade-leave-active .wbi-dialog {
      animation: wbi-fade 0.2s ease !important;
    }

    .wbi-close,
    .wbi-copy,
    .wbi-footer .el-button {
      transition: none;
    }
  }

  @media (prefers-reduced-transparency: reduce) {
    .wbi-overlay {
      backdrop-filter: none;
    }

    .wbi-chrome,
    .wbi-footer {
      background: #fff;
      backdrop-filter: none;
    }
  }

  @keyframes wbi-overlay-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes wbi-overlay-out {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }

  @keyframes wbi-dialog-in {
    from {
      opacity: 0;
      transform: scale(0.96) translateY(8px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  @keyframes wbi-dialog-out {
    from {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
    to {
      opacity: 0;
      transform: scale(0.96) translateY(8px);
    }
  }

  @keyframes wbi-fade {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
</style>
