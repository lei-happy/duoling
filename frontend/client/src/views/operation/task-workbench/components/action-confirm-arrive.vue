<!--
  确认到达弹窗（多批次卸车 / 单任务）

  改造要点：
  - 不再走 PUT /task/{id}/status 推 3→4，转为 POST /task/{id}/loading-records (eventType=2)；
    后端按 item 状态聚合 task 3→4（全部卸完才推进）。
  - 表单字段：
    1) 关联调令（多调令必选；单调令默认锁定）
    2) 卸车地点（默认填调令 to_location）
    3) 实际卸车时间
    4) 选择本次要卸车的 items（仅展示已装车未卸车的挂接行）
    5) 上传照片（≤9 张）
    6) 备注
-->
<template>
  <el-dialog
    :model-value="visible"
    title="确认到达（本次卸车）"
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
      :title="`任务单 ${task.taskNo} · ${task.origin || '--'} → ${task.destination || '--'} · 已卸 ${unloadedQuantity}/${task.totalQuantity || 0} 台`"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      v-loading="loading"
    >
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="关联调令" prop="dispatchOrderId" required>
            <el-select
              v-model="form.dispatchOrderId"
              placeholder="选择本次卸车所属调令"
              :disabled="heavyOrders.length <= 1"
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
          <el-form-item label="实际到达时间" prop="happenedAt" required>
            <el-date-picker
              v-model="form.happenedAt"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="选择实际到达时间"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="卸车地点">
        <el-input
          v-model="form.location"
          placeholder="卸车地点（默认填本调令目的地）"
        />
      </el-form-item>

      <el-form-item label="本次卸车" prop="itemIds" required>
        <div style="width: 100%">
          <el-table
            :data="unloadableItems"
            row-key="id"
            border
            size="small"
            max-height="280"
            @selection-change="onItemSelection"
          >
            <el-table-column type="selection" width="44" />
            <el-table-column label="运单号" prop="waybillNo" min-width="140" />
            <el-table-column label="品牌" prop="vehicleBrand" width="110" />
            <el-table-column label="车型" prop="vehicleModel" min-width="140" />
            <el-table-column
              label="台数"
              prop="quantity"
              width="80"
              align="center"
            />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="(ITEM_STATUS_MAP[row.status]?.type as any) || 'info'"
                  size="small"
                >
                  {{ ITEM_STATUS_MAP[row.status]?.label || '--' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!unloadableItems.length" class="ele-text-secondary mt-8">
            当前调令下已无可卸车的挂接行（全部已卸 / 待装车）。
          </div>
        </div>
      </el-form-item>

      <el-form-item label="卸车照片">
        <div class="photo-uploader">
          <div
            v-for="(url, idx) in form.photoUrls"
            :key="url"
            class="photo-item"
          >
            <el-image
              :src="url"
              fit="cover"
              :preview-src-list="form.photoUrls"
              :initial-index="idx"
            />
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
        <div class="ele-text-secondary mt-4">最多 9 张，每张不超过 5MB。</div>
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="可选"
        />
      </el-form-item>
    </el-form>

    <el-divider content-position="left">历史卸车记录</el-divider>
    <el-table
      :data="unloadHistory"
      size="small"
      border
      max-height="180"
      empty-text="暂无卸车记录"
    >
      <el-table-column label="时间" width="160">
        <template #default="{ row }">{{ formatDateTime(row.happenedAt) }}</template>
      </el-table-column>
      <el-table-column label="地点" prop="location" min-width="140" />
      <el-table-column label="台数" prop="quantity" width="80" align="center" />
      <el-table-column label="操作人" prop="operatorName" width="120" />
      <el-table-column label="备注" prop="remark" min-width="160" />
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button
        type="success"
        :loading="submitting"
        :disabled="!form.itemIds.length"
        @click="submit"
      >
        确认本次卸车
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { Close, Plus } from '@element-plus/icons-vue';
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
    DISPATCH_TYPE_HEAVY,
    ITEM_STATUS_MAP
  } from '../../task/status-config';

  const props = defineProps<{
    visible: boolean;
    /** 多批次模式只支持单任务 */
    tasks: Task[];
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const loading = ref(false);
  const submitting = ref(false);

  const dispatchOrders = ref<TaskDispatchOrder[]>([]);
  const items = ref<TaskWaybillItem[]>([]);
  const unloadHistory = ref<TaskLoadingRecord[]>([]);

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
    happenedAt: [{ required: true, message: '请选择实际到达时间' }],
    itemIds: [
      {
        validator: (_r, _v, cb) => {
          if (!form.itemIds.length)
            return cb(new Error('请勾选本次卸车的挂接行'));
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

  const unloadableItems = computed(() => {
    const oid = form.dispatchOrderId;
    return items.value.filter((it) => {
      if ((it.status ?? 0) !== 1) return false;
      if (oid != null && it.dispatchOrderId != null && it.dispatchOrderId !== oid) {
        return false;
      }
      return true;
    });
  });

  const unloadedQuantity = computed(() =>
    items.value
      .filter((it) => (it.status ?? 0) >= 2)
      .reduce((s, it) => s + (it.quantity || 0), 0)
  );

  const onOpen = async () => {
    form.dispatchOrderId = undefined;
    form.happenedAt = new Date().toISOString().slice(0, 19);
    form.location = '';
    form.itemIds = [];
    form.photoUrls = [];
    form.remark = '';
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
      unloadHistory.value = history.filter((r) => r.eventType === 2);
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
      form.location = o.toLocation || '';
    }
  };

  const onItemSelection = (rows: TaskWaybillItem[]) => {
    form.itemIds = rows.map((r) => r.id!).filter((x) => !!x);
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
        eventType: 2,
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
      EleMessage.success({ message: '已记录本次卸车', plain: true });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '卸车记录失败',
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
</style>
