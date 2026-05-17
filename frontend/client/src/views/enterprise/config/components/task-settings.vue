<template>
  <div class="task-settings">
    <div class="task-settings__block task-settings__block--first">
      <div class="task-settings__block-head">
        <span class="task-settings__block-title">任务号生成规则</span>
        <ele-tooltip
          placement="top-start"
          effect="light"
          :width="360"
          :offset="4"
        >
          <template #content>
            <div class="task-help-tip">
              <p class="task-help-tip__title">三段式说明</p>
              <p class="task-help-tip__plain">
                从左到右依次拼接：可选「固定前缀」「日期（年月日或年月）」「自增序号」。序号在同一段前缀+日期下递增；前缀中请勿使用
                %、_ 等特殊字符。
              </p>
            </div>
          </template>
          <el-icon class="field-help-icon" tabindex="-1">
            <QuestionCircleOutlined />
          </el-icon>
        </ele-tooltip>
      </div>
      <div class="task-settings__main">
        <div class="task-settings__main-slots">
          <div class="task-settings__slots">
            <div
              v-for="(slot, idx) in noSlots"
              :key="'no-' + idx"
              class="task-settings__slot-row"
            >
              <span class="task-settings__slot-label">第 {{ idx + 1 }} 段</span>
              <el-select
                v-model="slot.type"
                class="task-settings__slot-type"
                @change="onNoTypeChange(slot)"
              >
                <el-option
                  v-for="opt in noTypeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <el-input
                v-if="slot.type === 'prefix'"
                v-model="slot.value"
                maxlength="32"
                show-word-limit
                placeholder="如 TASK"
                class="task-settings__slot-input"
                clearable
              />
              <el-select
                v-if="slot.type === 'date'"
                v-model="slot.format"
                class="task-settings__slot-input"
              >
                <el-option label="年月日 YYYYMMDD" value="YYYYMMDD" />
                <el-option label="年月 YYYYMM" value="YYYYMM" />
              </el-select>
              <template v-if="slot.type === 'seq'">
                <span class="task-settings__inline-label">位数</span>
                <el-input-number
                  v-model="slot.digits"
                  :min="1"
                  :max="6"
                  controls-position="right"
                />
                <span class="task-settings__inline-label">重置</span>
                <el-select v-model="slot.reset" style="width: 120px">
                  <el-option label="按日" value="daily" />
                  <el-option label="按月" value="monthly" />
                  <el-option label="不按日期" value="global" />
                </el-select>
              </template>
            </div>
          </div>
        </div>
        <div
          class="task-settings__preview task-settings__preview--prominent task-settings__main-preview"
        >
          <div class="task-settings__preview-head">
            <span class="task-settings__preview-badge">预览</span>
          </div>
          <div class="task-settings__preview-body">
            <code class="task-settings__preview-value">{{ taskNoPreview }}</code>
          </div>
        </div>
      </div>
      <div class="task-settings__actions">
        <el-button type="primary" :disabled="!noItem" @click="saveNoRule">
          保存任务号规则
        </el-button>
        <span class="config-default config-default--inline"
          >默认值：TASK + 年月日 + 4 位序号</span
        >
      </div>
    </div>

    <el-divider class="task-settings__divider" />

    <div
      class="task-settings__section-title task-settings__section-title--block"
    >
      任务名称生成设置
    </div>

    <div class="task-settings__block">
      <div class="task-settings__block-head">
        <span class="task-settings__block-title">任务名称生成规则</span>
        <ele-tooltip
          placement="top-start"
          effect="light"
          :width="360"
          :offset="4"
        >
          <template #content>
            <div class="task-help-tip">
              <p class="task-help-tip__title">三段式说明</p>
              <p class="task-help-tip__plain">
                每段从「路线」「商品车」「承运/计划」等维度中选一类；非空段之间用连接符拼接。商品车默认取<strong>首条挂接</strong>的品牌与型号；未派车时承运相关段自动省略。
              </p>
            </div>
          </template>
          <el-icon class="field-help-icon" tabindex="-1">
            <QuestionCircleOutlined />
          </el-icon>
        </ele-tooltip>
      </div>
      <div class="task-settings__main">
        <div class="task-settings__main-slots">
          <div class="task-settings__slots">
            <div
              v-for="(slot, idx) in nameSlots"
              :key="'nm-' + idx"
              class="task-settings__slot-row"
            >
              <span class="task-settings__slot-label">第 {{ idx + 1 }} 段</span>
              <el-select
                v-model="slot.kind"
                class="task-settings__slot-type-wide"
              >
                <el-option
                  v-for="opt in nameKindOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </div>
            <div class="task-settings__slot-row task-settings__slot-row--joiner">
              <span class="task-settings__slot-label">连接符</span>
              <el-input
                v-model="nameJoiner"
                maxlength="8"
                class="task-settings__joiner-input"
                placeholder="默认空格"
              />
            </div>
          </div>
        </div>
        <div
          class="task-settings__preview task-settings__preview--prominent task-settings__main-preview"
        >
          <div class="task-settings__preview-head">
            <span class="task-settings__preview-badge">预览</span>
          </div>
          <div class="task-settings__preview-body">
            <span
              class="task-settings__preview-value task-settings__preview-value--name"
              >{{ taskNamePreview }}</span
            >
          </div>
        </div>
      </div>
      <div class="task-settings__actions">
        <el-button type="primary" :disabled="!nameItem" @click="saveNameRule">
          保存任务名称规则
        </el-button>
        <span class="config-default config-default--inline">
          默认值：路线(出发-到达) + 首条商品车 + 主驾/车牌
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { SystemConfig } from '@/api/system/config/model';
  import { QuestionCircleOutlined } from '@/components/icons';
  import {
    TASK_NAME_GEN_DEFAULT_JSON,
    TASK_NO_GEN_DEFAULT_JSON
  } from '@/views/enterprise/config/constants';

  defineOptions({ name: 'TaskSettings' });

  function todayYmdYm() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return {
      ymd: `${y}${m}${day}`,
      ym: `${y}${m}`,
      mdLoad: `${m}月${day}日装车`
    };
  }

  function sampleNamePart(kind: string, mdLoad: string): string {
    const map: Record<string, string> = {
      none: '',
      route_od: '合肥-上海',
      route_origin: '合肥',
      route_dest: '上海',
      vehicle_first: '奥迪 A6L',
      carrier_driver_plate: '张伟/苏A88888',
      carrier_company: '某某物流有限公司',
      planned_load_md: mdLoad
    };
    return map[kind] ?? '';
  }

  type NoPartType = 'none' | 'prefix' | 'date' | 'seq';

  interface NoSlot {
    type: NoPartType;
    value?: string;
    format?: string;
    digits?: number;
    reset?: string;
  }

  interface NameSlot {
    kind: string;
  }

  const props = defineProps<{
    items: SystemConfig[];
  }>();

  const emit = defineEmits<{
    (e: 'config-change', item: SystemConfig, val: string): void;
  }>();

  const noItem = computed(() =>
    props.items.find((i) => i.configKey === 'task.no_gen_rule')
  );
  const nameItem = computed(() =>
    props.items.find((i) => i.configKey === 'task.name_gen_rule')
  );

  const noTypeOptions = [
    { value: 'none' as NoPartType, label: '无' },
    { value: 'prefix' as NoPartType, label: '固定前缀' },
    { value: 'date' as NoPartType, label: '日期' },
    { value: 'seq' as NoPartType, label: '自增序号' }
  ];

  const nameKindOptions = [
    { value: 'none', label: '无' },
    { value: 'route_od', label: '路线（出发地-目的地）' },
    { value: 'route_origin', label: '路线（仅出发地）' },
    { value: 'route_dest', label: '路线（仅目的地）' },
    { value: 'vehicle_first', label: '商品车（首条挂接品牌型号）' },
    { value: 'carrier_driver_plate', label: '承运（主驾/车牌）' },
    { value: 'carrier_company', label: '承运（承运商名称）' },
    { value: 'planned_load_md', label: '计划装车（月日）' }
  ];

  const defaultNoSlots = (): NoSlot[] => [
    { type: 'prefix', value: 'TASK' },
    { type: 'date', format: 'YYYYMMDD' },
    { type: 'seq', digits: 4, reset: 'daily' }
  ];

  const defaultNameSlots = (): NameSlot[] => [
    { kind: 'route_od' },
    { kind: 'vehicle_first' },
    { kind: 'carrier_driver_plate' }
  ];

  const noSlots = ref<NoSlot[]>(defaultNoSlots());
  const nameSlots = ref<NameSlot[]>(defaultNameSlots());
  const nameJoiner = ref(' ');

  const taskNoPreview = computed(() => {
    if (!noSlots.value.some((x) => x.type === 'seq')) {
      return '—（请至少设置一段「自增序号」）';
    }
    const { ymd, ym } = todayYmdYm();
    let seqSeen = false;
    let out = '';
    for (const s of noSlots.value) {
      if (s.type === 'none') continue;
      if (s.type === 'prefix') {
        out += String(s.value ?? '');
      } else if (s.type === 'date') {
        out += s.format === 'YYYYMM' ? ym : ymd;
      } else if (s.type === 'seq') {
        if (!seqSeen) {
          const dig = Math.min(
            6,
            Math.max(1, Math.floor(Number(s.digits) || 4))
          );
          out += String(1).padStart(dig, '0');
          seqSeen = true;
        }
      }
    }
    return out || '—';
  });

  const taskNamePreview = computed(() => {
    const { mdLoad } = todayYmdYm();
    const j = nameJoiner.value ?? ' ';
    const chunks = nameSlots.value
      .map((s) => sampleNamePart(s.kind || 'none', mdLoad))
      .filter(Boolean);
    if (!chunks.length) {
      return '—（三段均为「无」时，保存后将按系统默认规则命名）';
    }
    return chunks.join(j);
  });

  function parseNoFromJson(raw: string | undefined | null) {
    try {
      const o = JSON.parse(raw || TASK_NO_GEN_DEFAULT_JSON) as {
        parts?: unknown[];
      };
      const parts = Array.isArray(o.parts) ? o.parts : [];
      const slots: NoSlot[] = [];
      for (let i = 0; i < 3; i++) {
        const p = (parts[i] || {}) as Record<string, unknown>;
        const t = (p.type as string) || 'none';
        const type = (
          ['none', 'prefix', 'date', 'seq'].includes(t) ? t : 'none'
        ) as NoPartType;
        if (type === 'prefix') {
          slots.push({ type, value: String(p.value ?? '') });
        } else if (type === 'date') {
          const fmt = p.format === 'YYYYMM' ? 'YYYYMM' : 'YYYYMMDD';
          slots.push({ type, format: fmt });
        } else if (type === 'seq') {
          let d = Number(p.digits);
          if (!Number.isFinite(d)) d = 4;
          d = Math.min(6, Math.max(1, Math.floor(d)));
          const reset = ['daily', 'monthly', 'global'].includes(String(p.reset))
            ? String(p.reset)
            : 'daily';
          slots.push({ type, digits: d, reset });
        } else {
          slots.push({ type: 'none' });
        }
      }
      noSlots.value = slots;
    } catch {
      noSlots.value = defaultNoSlots();
    }
  }

  function parseNameFromJson(raw: string | undefined | null) {
    try {
      const o = JSON.parse(raw || TASK_NAME_GEN_DEFAULT_JSON) as {
        joiner?: string;
        parts?: unknown[];
      };
      nameJoiner.value = typeof o.joiner === 'string' ? o.joiner : ' ';
      const parts = Array.isArray(o.parts) ? o.parts : [];
      const allowed = new Set(nameKindOptions.map((x) => x.value));
      const slots: NameSlot[] = [];
      for (let i = 0; i < 3; i++) {
        const p = (parts[i] || {}) as Record<string, unknown>;
        const k = String(p.kind || 'none');
        slots.push({ kind: allowed.has(k) ? k : 'none' });
      }
      nameSlots.value = slots;
    } catch {
      nameSlots.value = defaultNameSlots();
      nameJoiner.value = ' ';
    }
  }

  watch(
    () => [noItem.value?.configValue, noItem.value?.id] as const,
    () => parseNoFromJson(noItem.value?.configValue),
    { immediate: true }
  );

  watch(
    () => [nameItem.value?.configValue, nameItem.value?.id] as const,
    () => parseNameFromJson(nameItem.value?.configValue),
    { immediate: true }
  );

  function onNoTypeChange(slot: NoSlot) {
    if (slot.type === 'prefix' && slot.value === undefined) slot.value = '';
    if (slot.type === 'date' && !slot.format) slot.format = 'YYYYMMDD';
    if (slot.type === 'seq') {
      slot.digits = slot.digits ?? 4;
      slot.reset = slot.reset || 'daily';
    }
  }

  function normalizeNoPartsForSave(): { parts: Record<string, unknown>[] } {
    let seqSeen = false;
    const parts = noSlots.value.map((s) => {
      if (s.type === 'none') return { type: 'none' };
      if (s.type === 'prefix')
        return { type: 'prefix', value: (s.value || '').trim() };
      if (s.type === 'date')
        return { type: 'date', format: s.format || 'YYYYMMDD' };
      if (s.type === 'seq') {
        if (seqSeen) return { type: 'none' };
        seqSeen = true;
        const digits = Math.min(
          6,
          Math.max(1, Math.floor(Number(s.digits) || 4))
        );
        const reset = ['daily', 'monthly', 'global'].includes(String(s.reset))
          ? s.reset
          : 'daily';
        return { type: 'seq', digits, reset };
      }
      return { type: 'none' };
    });
    return { parts };
  }

  function saveNoRule() {
    const item = noItem.value;
    if (!item) return;
    const body = normalizeNoPartsForSave();
    const json = JSON.stringify(body);
    if (json.length > 500) {
      EleMessage.error({ message: '配置过长，请缩短前缀', plain: true });
      return;
    }
    if (!body.parts.some((p) => p.type === 'seq')) {
      EleMessage.error({
        message: '任务号规则须包含一段「自增序号」',
        plain: true
      });
      return;
    }
    const seqCount = noSlots.value.filter((s) => s.type === 'seq').length;
    if (seqCount > 1) {
      EleMessage.warning({
        message: '仅保留第一个序号段，其余序号已忽略',
        plain: true
      });
    }
    emit('config-change', item, json);
  }

  function saveNameRule() {
    const item = nameItem.value;
    if (!item) return;
    const parts = nameSlots.value.map((s) => ({ kind: s.kind || 'none' }));
    const joiner = nameJoiner.value ?? ' ';
    const json = JSON.stringify({ joiner, parts });
    if (json.length > 500) {
      EleMessage.error({ message: '配置过长', plain: true });
      return;
    }
    emit('config-change', item, json);
  }
</script>

<style scoped>
  .task-settings {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .task-settings__block--first {
    margin-top: 0;
  }

  .task-settings__preview--prominent {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px 16px;
    border-radius: var(--el-border-radius-base);
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-5);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .task-settings__preview-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 12px;
  }

  .task-settings__preview-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--el-color-primary);
    background: var(--el-bg-color);
    border: 1px solid var(--el-color-primary-light-3);
    border-radius: var(--el-border-radius-small);
  }

  .task-settings__preview-hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
  }

  .task-settings__preview-body {
    padding: 10px 12px;
    border-radius: var(--el-border-radius-small);
    background: var(--el-bg-color);
    border: 1px dashed var(--el-color-primary-light-5);
  }

  .task-settings__preview-value {
    display: block;
    margin: 0;
    font-size: 17px;
    font-weight: 600;
    font-family: var(--el-font-family-mono);
    color: var(--el-color-primary);
    word-break: break-all;
    line-height: 1.45;
    letter-spacing: 0.02em;
  }

  .task-settings__preview-value--name {
    font-family: var(--el-font-family);
    font-weight: 600;
  }

  .task-settings__section-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 6px;
  }

  .task-settings__section-title--block {
    margin: 4px 0 10px;
  }

  .task-settings__divider {
    margin: 14px 0 18px;
  }

  .task-settings__block {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 8px;
  }

  .task-settings__block-head {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .task-settings__block-title {
    font-size: var(--el-form-label-font-size);
    font-weight: 500;
    color: var(--el-text-color-regular);
  }

  .task-settings__main {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    gap: 16px 20px;
  }

  .task-settings__main-slots {
    flex: 1 1 0;
    min-width: 0;
  }

  .task-settings__main-preview {
    flex: 0 1 300px;
    min-width: 200px;
    max-width: 360px;
    align-self: stretch;
  }

  .task-settings__main-preview .task-settings__preview-body {
    flex: 1;
    min-height: 0;
  }

  @media (max-width: 900px) {
    .task-settings__main {
      flex-direction: column;
    }

    .task-settings__main-preview {
      flex: 1 1 auto;
      max-width: none;
      width: 100%;
    }
  }

  .task-settings__slots {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .task-settings__slot-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 12px;
  }

  .task-settings__slot-row--joiner {
    margin-top: 4px;
  }

  .task-settings__slot-label {
    width: 52px;
    flex-shrink: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .task-settings__slot-type {
    width: 130px;
  }

  .task-settings__slot-type-wide {
    min-width: 220px;
    flex: 1;
    max-width: 420px;
  }

  .task-settings__slot-input {
    width: 200px;
    max-width: 100%;
  }

  .task-settings__joiner-input {
    width: 120px;
  }

  .task-settings__inline-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    margin-left: 4px;
  }

  .task-settings__actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px 16px;
    margin-top: 4px;
  }

  .field-help-icon {
    font-size: 15px;
    color: var(--el-text-color-secondary);
    cursor: help;
    outline: none;
  }

  .field-help-icon:hover {
    color: var(--el-color-primary);
  }

  .config-default {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  .config-default--inline {
    margin-top: 0;
  }

  .task-help-tip {
    line-height: 1.55;
    font-size: 13px;
  }

  .task-help-tip__title {
    margin: 0 0 8px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .task-help-tip__plain {
    margin: 0;
    color: var(--el-text-color-regular);
  }
</style>
