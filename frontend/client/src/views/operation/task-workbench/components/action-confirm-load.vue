<!--
  确认装车弹窗（多批次模式 / 单任务）

  改造要点：
  - 不再走 PUT /task/{id}/status 推 1→2，转为 POST /task/{id}/loading-records；
    后端按 item 状态聚合 task 1→2（全部装完才推进）。
  - 表单字段：
    1) 关联调令（多调令必选；单调令默认锁定）
    2) 装车地点（自由文本，默认填调令 from_location）
    3) 实际装车时间
    4) 选择本次要装车的 items（仅展示 status<1 的运单货物）
    5) 上传照片（≤9 张）
    6) 备注
  - 只支持单任务（多批次模式不适合批量）
-->
<template>
  <el-dialog
    :model-value="visible"
    title="确认装车（本次记录）"
    width="900px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="task"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="`任务单 ${task.taskNo} · ${task.origin || '--'} → ${task.destination || '--'} · 已装 ${loadedQuantity}/${task.totalQuantity || 0} 台`"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      v-loading="loading"
    >
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="关联调令" prop="dispatchOrderId" required>
            <el-select
              v-model="form.dispatchOrderId"
              placeholder="选择本次装车所属调令"
              :disabled="dispatchOrders.length <= 1"
              style="width: 100%"
              @change="onOrderChange"
            >
              <el-option
                v-for="o in heavyOrders"
                :key="o.id"
                :value="o.id!"
                :label="`第 ${o.orderNo} 段 · ${o.fromLocation || '--'} → ${o.toLocation || '--'}`"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="实际装车时间" prop="happenedAt" required>
            <el-date-picker
              v-model="form.happenedAt"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="选择实际装车时间"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="装车地点">
        <el-input
          v-model="form.location"
          placeholder="装车地点（默认填本调令出发地）"
        />
      </el-form-item>

      <el-form-item
        prop="itemIds"
        required
        :show-message="false"
        class="load-item-form-item"
      >
        <template #label>
          <div class="load-item-label-row">
            <div class="load-item-label-row__left">
              <span class="load-item-label-row__title">本次装车</span>
              <span class="load-item-label-row__hint">
                点击卡片选择本次要装的商品车
              </span>
            </div>
            <div v-if="loadableItems.length" class="load-item-label-row__right">
              <span class="load-item-label-row__count">
                已选 {{ selectedQuantity }} / {{ loadableTotalQuantity }} 台
              </span>
              <el-button
                link
                type="primary"
                size="small"
                @click.stop="toggleSelectAllLoadable"
              >
                {{ allLoadableSelected ? '取消全选' : '全选' }}
              </el-button>
            </div>
          </div>
        </template>
        <div class="load-item-panel">
          <el-scrollbar v-if="loadableItems.length" max-height="680px">
            <div class="load-item-grid">
              <div
                v-for="row in loadableItems"
                :key="row.id"
                class="load-item-card"
                :class="{ 'load-item-card--selected': isItemSelected(row.id!) }"
                role="button"
                tabindex="0"
                @click="toggleItem(row)"
                @keydown.enter.prevent="toggleItem(row)"
                @keydown.space.prevent="toggleItem(row)"
              >
                <div class="load-item-card__check">
                  <el-icon v-if="isItemSelected(row.id!)"><Check /></el-icon>
                </div>
                <div class="load-item-card__thumb">
                  <el-image
                    v-if="seriesImageUrl(row.seriesImage)"
                    :src="seriesImageUrl(row.seriesImage)"
                    fit="contain"
                    class="load-item-card__img"
                    lazy
                  >
                    <template #error>
                      <div class="load-item-card__ph">
                        <el-icon :size="18"><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <div v-else class="load-item-card__ph">
                    <el-icon :size="18"><Picture /></el-icon>
                  </div>
                  <span class="load-item-card__qty">×{{ row.quantity || 0 }}</span>
                </div>
                <div class="load-item-card__body">
                  <div
                    class="load-item-card__model"
                    :title="`${row.vehicleBrand || '--'} / ${row.vehicleModel || '--'}`"
                  >
                    {{ row.vehicleBrand || '--' }} / {{ row.vehicleModel || '--' }}
                  </div>
                  <div class="load-item-card__waybill" :title="row.waybillNo || ''">
                    {{ row.waybillNo || '--' }}
                  </div>
                </div>
              </div>
            </div>
          </el-scrollbar>

          <div v-else class="ele-text-secondary mt-8">
            当前调令下已无可装车的挂接行（全部已装或已签收）。
          </div>
        </div>
      </el-form-item>

      <el-form-item class="photo-form-item">
        <template #label>
          <el-tooltip
            content="最多 9 张，每张不超过 5MB。"
            placement="top"
          >
            <span class="photo-form-item__label">装车照片</span>
          </el-tooltip>
        </template>
        <div class="photo-uploader">
          <div
            v-for="(url, idx) in form.photoUrls"
            :key="url"
            class="photo-item"
          >
            <el-image :src="url" fit="cover" :preview-src-list="form.photoUrls" :initial-index="idx" />
            <el-icon class="photo-remove" @click="removePhoto(idx)">
              <Close />
            </el-icon>
          </div>
          <el-upload
            v-if="form.photoUrls.length < 9"
            class="photo-add"
            accept="image/*"
            :show-file-list="false"
            :before-upload="beforeUpload"
          >
            <el-icon><Plus /></el-icon>
            <span class="photo-add__hint">添加照片</span>
          </el-upload>
        </div>
      </el-form-item>

    </el-form>

    <div class="load-history-entry">
      <el-button
        v-if="loadHistory.length"
        link
        type="info"
        class="load-history-entry__btn"
        @click="historyDialogVisible = true"
      >
        历史装车记录
        <el-tag size="small" type="info">{{ loadHistory.length }} 条</el-tag>
        <span v-if="latestHistorySummary" class="load-history-entry__summary">
          {{ latestHistorySummary }}
        </span>
      </el-button>
      <span v-else class="load-history-entry__empty ele-text-secondary">
        暂无历史装车记录
      </span>
    </div>

    <template #footer>
      <div class="confirm-load-footer">
        <div class="confirm-load-footer__left">
          <el-popover
            v-model:visible="remarkPopoverVisible"
            placement="top-start"
            :width="420"
            trigger="click"
            popper-class="confirm-load-remark-popper"
          >
            <template #reference>
              <el-button link type="primary">
                <el-icon><EditPen /></el-icon>
                {{ remarkFilled ? '编辑备注' : '填写备注' }}
              </el-button>
            </template>
            <div class="confirm-load-remark-popover">
              <div class="confirm-load-remark-popover__title">装车备注</div>
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="4"
                maxlength="500"
                show-word-limit
                placeholder="装车过程中的其他说明（可选）"
              />
            </div>
          </el-popover>
          <span
            v-if="remarkFilled"
            class="confirm-load-footer__remark-preview"
            :title="form.remark.trim()"
          >
            {{ remarkPreview }}
          </span>
        </div>
        <div class="confirm-load-footer__actions">
          <el-button @click="emit('update:visible', false)">取消</el-button>
          <el-tooltip
            content="请先点击卡片选择本次要装的商品车"
            placement="top"
            :disabled="!!form.itemIds.length"
          >
            <span class="confirm-load-submit-wrap">
              <el-button
                type="warning"
                :loading="submitting"
                :disabled="!form.itemIds.length"
                @click="submit"
              >
                确认本次装车
              </el-button>
            </span>
          </el-tooltip>
        </div>
      </div>
    </template>
  </el-dialog>

  <el-dialog
    v-model="historyDialogVisible"
    title="历史装车记录"
    width="760px"
    append-to-body
    align-center
    destroy-on-close
    class="load-history-dialog"
  >
    <el-table
      :data="loadHistory"
      size="small"
      border
      max-height="480"
      empty-text="暂无装车记录"
    >
      <el-table-column label="时间" width="160">
        <template #default="{ row }">{{
          formatDateTime(row.happenedAt)
        }}</template>
      </el-table-column>
      <el-table-column label="地点" prop="location" min-width="140" />
      <el-table-column label="台数" prop="quantity" width="80" align="center" />
      <el-table-column label="操作人" prop="operatorName" width="120" />
      <el-table-column label="备注" prop="remark" min-width="160" />
    </el-table>
    <template #footer>
      <el-button type="primary" @click="historyDialogVisible = false">
        关闭
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { Check, Close, EditPen, Picture, Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { listTaskSegments, listTaskWaybillItems } from '@/api/operation/task';
  import {
    createLoadingRecord,
    listLoadingRecords
  } from '@/api/operation/task/loading-record';
  import { uploadFile } from '@/api/system/file';
  import type {
    Task,
    TaskDispatchOrder,
    TaskLoadingRecord,
    TaskWaybillItem
  } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    DISPATCH_TYPE_DEFAULT,
    DISPATCH_TYPE_HEAVY
  } from '../../task/status-config';

  const props = defineProps<{
    visible: boolean;
    /** 多批次模式只支持单任务；caller 传 tasks[0] 即可 */
    tasks: Task[];
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const loading = ref(false);
  const submitting = ref(false);
  const remarkPopoverVisible = ref(false);
  const historyDialogVisible = ref(false);

  const dispatchOrders = ref<TaskDispatchOrder[]>([]);
  const items = ref<TaskWaybillItem[]>([]);
  const loadHistory = ref<TaskLoadingRecord[]>([]);

  const form = reactive({
    dispatchOrderId: undefined as number | undefined,
    happenedAt: '',
    location: '',
    itemIds: [] as number[],
    photoUrls: [] as string[],
    remark: ''
  });

  const rules: FormRules = {
    dispatchOrderId: [{ required: true, message: '请选择关联调令' }],
    happenedAt: [{ required: true, message: '请选择实际装车时间' }],
    itemIds: [
      {
        validator: (_r, _v, cb) => {
          if (!form.itemIds.length) {
            return cb(new Error('请先选择本次要装的商品车'));
          }
          cb();
        },
        trigger: 'change'
      }
    ]
  };

  const task = computed<Task | null>(() => props.tasks?.[0] ?? null);

  const heavyOrders = computed(() =>
    dispatchOrders.value.filter(
      (o) => (o.dispatchType ?? DISPATCH_TYPE_DEFAULT) === DISPATCH_TYPE_HEAVY
    )
  );

  const loadableItems = computed(() => {
    const oid = form.dispatchOrderId;
    return items.value.filter((it) => {
      if ((it.status ?? 0) >= 1) return false;
      if (oid != null && it.dispatchOrderId != null && it.dispatchOrderId !== oid) {
        return false;
      }
      return true;
    });
  });

  const loadableTotalQuantity = computed(() =>
    loadableItems.value.reduce((s, it) => s + (it.quantity || 0), 0)
  );

  const selectedQuantity = computed(() => {
    const idSet = new Set(form.itemIds);
    return loadableItems.value
      .filter((it) => it.id != null && idSet.has(it.id))
      .reduce((s, it) => s + (it.quantity || 0), 0);
  });

  const allLoadableSelected = computed(() => {
    if (!loadableItems.value.length) return false;
    return loadableItems.value.every(
      (it) => it.id != null && form.itemIds.includes(it.id)
    );
  });

  const latestHistorySummary = computed(() => {
    const latest = loadHistory.value[0];
    if (!latest) return '';
    const time = formatDateTime(latest.happenedAt) || '--';
    const qty = latest.quantity ?? 0;
    const loc = latest.location?.trim();
    return loc ? `最近 ${time} · ${loc} · ${qty} 台` : `最近 ${time} · ${qty} 台`;
  });

  const remarkFilled = computed(() => !!form.remark.trim());
  const remarkPreview = computed(() => {
    const text = form.remark.trim();
    if (!text) return '';
    return text.length > 32 ? `${text.slice(0, 32)}…` : text;
  });

  function seriesImageUrl(p?: string | null): string {
    const s = p?.trim();
    if (!s) return '';
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    return s.startsWith('/') ? s : `/${s}`;
  }

  const loadedQuantity = computed(() =>
    items.value
      .filter((it) => (it.status ?? 0) >= 1)
      .reduce((s, it) => s + (it.quantity || 0), 0)
  );

  const syncItemSelectionValidation = () => {
    formRef.value?.validateField('itemIds').catch(() => undefined);
  };

  const isItemSelected = (id: number) => form.itemIds.includes(id);

  const toggleItem = (row: TaskWaybillItem) => {
    const id = row.id;
    if (id == null) return;
    const idx = form.itemIds.indexOf(id);
    if (idx >= 0) {
      form.itemIds.splice(idx, 1);
    } else {
      form.itemIds.push(id);
    }
    syncItemSelectionValidation();
  };

  const selectAllLoadable = () => {
    form.itemIds = loadableItems.value
      .map((it) => it.id!)
      .filter((id) => id != null);
    syncItemSelectionValidation();
  };

  const toggleSelectAllLoadable = () => {
    if (allLoadableSelected.value) {
      form.itemIds = [];
    } else {
      selectAllLoadable();
    }
    syncItemSelectionValidation();
  };

  const onOpen = async () => {
    form.dispatchOrderId = undefined;
    form.happenedAt = new Date().toISOString().slice(0, 19);
    form.location = '';
    form.itemIds = [];
    form.photoUrls = [];
    form.remark = '';
    remarkPopoverVisible.value = false;
    historyDialogVisible.value = false;
    if (!task.value?.id) return;
    loading.value = true;
    try {
      const [orders, its, history] = await Promise.all([
        listTaskSegments(task.value.id),
        listTaskWaybillItems(task.value.id),
        listLoadingRecords(task.value.id)
      ]);
      dispatchOrders.value = orders as unknown as TaskDispatchOrder[];
      items.value = its;
      loadHistory.value = history
        .filter((r) => r.eventType === 1)
        .sort(
          (a, b) =>
            new Date(b.happenedAt || 0).getTime() -
            new Date(a.happenedAt || 0).getTime()
        );
      const heavy = dispatchOrders.value.filter(
        (o) => (o.dispatchType ?? DISPATCH_TYPE_DEFAULT) === DISPATCH_TYPE_HEAVY
      );
      if (heavy.length === 1) {
        form.dispatchOrderId = heavy[0]!.id;
        onOrderChange(form.dispatchOrderId);
      }
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载任务详情失败',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const onOrderChange = (id?: number) => {
    const o = dispatchOrders.value.find((x) => x.id === id);
    if (o && !form.location) {
      form.location = o.fromLocation || '';
    }
    form.itemIds = [];
    syncItemSelectionValidation();
  };

  const beforeUpload = async (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      EleMessage.error({ message: '图片不能超过 5MB', plain: true });
      return false;
    }
    try {
      const res = await uploadFile(file, undefined, file.name, 'task_loading');
      if (res?.url) {
        form.photoUrls.push(res.url);
        EleMessage.success({ message: '上传成功', plain: true });
      }
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '上传失败',
        plain: true
      });
    }
    return false;
  };

  const removePhoto = (idx: number) => {
    form.photoUrls.splice(idx, 1);
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (!task.value?.id) return;
    const selected = items.value.filter((it) =>
      form.itemIds.includes(it.id!)
    );
    if (!selected.length) {
      EleMessage.warning({ message: '请至少勾选一行', plain: true });
      return;
    }
    submitting.value = true;
    try {
      await createLoadingRecord(task.value.id, {
        eventType: 1,
        dispatchOrderId: form.dispatchOrderId,
        happenedAt: form.happenedAt,
        location: form.location || undefined,
        items: selected.map((it) => ({
          itemId: it.id!,
          quantity: it.quantity || 0
        })),
        photoUrls: form.photoUrls,
        remark: form.remark || undefined
      });
      EleMessage.success({ message: '已记录本次装车', plain: true });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '装车记录失败',
        plain: true
      });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .photo-uploader {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
  }

  .photo-item {
    position: relative;
    width: 88px;
    height: 88px;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid var(--el-border-color);

    :deep(.el-image) {
      width: 100%;
      height: 100%;
    }
  }

  .photo-remove {
    position: absolute;
    top: 2px;
    right: 2px;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    padding: 2px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 12px;
  }

  .photo-add {
    width: 88px;
    height: 88px;
    border: 1px dashed var(--el-border-color);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    gap: 4px;

    &:hover {
      border-color: var(--el-color-primary);
      color: var(--el-color-primary);
    }

    &__hint {
      font-size: 12px;
    }
  }

  .mt-4 {
    margin-top: 4px;
  }
  .mt-8 {
    margin-top: 8px;
  }

  .load-item-form-item {
    :deep(.el-form-item__label) {
      display: flex !important;
      align-items: center;
      width: 100% !important;
      padding-right: 0;

      &::before {
        flex-shrink: 0;
        margin-right: 4px;
      }
    }

    :deep(.el-form-item__error) {
      display: none;
    }
  }

  .load-item-label-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    width: 100%;
    flex: 1;
    min-width: 0;
  }

  .load-item-label-row__left {
    display: flex;
    align-items: baseline;
    gap: 8px;
    min-width: 0;
  }

  .load-item-label-row__title {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-regular);
  }

  .load-item-label-row__hint {
    font-size: 12px;
    font-weight: 400;
    color: var(--el-text-color-secondary);
  }

  .load-item-label-row__right {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
  }

  .load-item-label-row__count {
    font-size: 12px;
    color: var(--el-text-color-regular);
    margin-right: 2px;
  }

  .load-item-panel {
    width: 100%;
  }

  .load-item-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 8px;
    padding: 2px 4px 4px 2px;
  }

  .load-item-card {
    position: relative;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    padding: 6px;
    cursor: pointer;
    background: var(--el-bg-color);
    transition:
      border-color 0.15s ease,
      box-shadow 0.15s ease,
      background-color 0.15s ease;
    outline: none;

    &:hover {
      border-color: var(--el-color-primary-light-5);
    }

    &:focus-visible {
      box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
    }

    &--selected {
      border-color: var(--el-color-primary);
      background: var(--el-color-primary-light-9);
      box-shadow: 0 0 0 1px var(--el-color-primary-light-7);
    }
  }

  .load-item-card__check {
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 2;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 1px solid var(--el-border-color);
    background: rgba(255, 255, 255, 0.92);
    display: flex;
    align-items: center;
    justify-content: center;
    color: transparent;
    font-size: 10px;
    transition:
      border-color 0.15s ease,
      background-color 0.15s ease,
      color 0.15s ease;

    .load-item-card--selected & {
      border-color: var(--el-color-primary);
      background: var(--el-color-primary);
      color: #fff;
    }
  }

  .load-item-card__thumb {
    position: relative;
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color-light);
    line-height: 0;

    :deep(.el-image) {
      width: 100%;
      height: 100%;
      display: block;
    }

    :deep(.el-image__inner),
    :deep(.el-image__wrapper),
    :deep(.el-image__error) {
      width: 100% !important;
      height: 100% !important;
    }

    :deep(.el-image__inner) {
      object-fit: contain;
    }
  }

  .load-item-card__ph {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    background: var(--el-fill-color);
  }

  .load-item-card__qty {
    position: absolute;
    right: 4px;
    bottom: 4px;
    z-index: 1;
    min-width: 24px;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 700;
    line-height: 18px;
    text-align: center;
    color: #fff;
    background: var(--el-color-warning);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.28);
  }

  .load-item-card__body {
    margin-top: 4px;
    min-width: 0;
    line-height: 1.2;
  }

  .load-item-card__model {
    font-size: 12px;
    font-weight: 600;
    line-height: 1.2;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .load-item-card__waybill {
    margin-top: 0;
    font-size: 11px;
    line-height: 1.2;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .photo-form-item__label {
    cursor: help;
    border-bottom: 1px dashed var(--el-border-color);
  }

  .load-history-entry {
    margin-top: 4px;
  }

  .load-history-entry__btn {
    padding-left: 0;
    height: auto;
    line-height: 1.5;

    :deep(.el-tag) {
      margin-left: 6px;
    }
  }

  .load-history-entry__summary {
    margin-left: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .load-history-entry__empty {
    font-size: 12px;
  }

  .confirm-load-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
  }

  .confirm-load-footer__left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex: 1;
  }

  .confirm-load-footer__remark-preview {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 280px;
  }

  .confirm-load-footer__actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .confirm-load-submit-wrap {
    display: inline-flex;
  }

  .confirm-load-remark-popover__title {
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }
</style>
