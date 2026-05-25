<template>
  <el-dialog
    title="启用 / 停用 / 黑名单"
    :model-value="visible"
    width="440px"
    append-to-body
    align-center
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <div v-if="row" class="sc-status">
      <p class="sc-status__line">
        当前启用状态：<strong>{{ statusLabel(row.status) }}</strong>
      </p>
      <p class="sc-status__line">目标状态</p>
      <el-select v-model="targetStatus" placeholder="请选择" class="sc-status__select">
        <el-option
          v-for="opt in targetOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>

      <p class="sc-status__line sc-status__line--remark">变更原因</p>
      <el-input
        v-model.trim="remark"
        type="textarea"
        :rows="3"
        placeholder="可选 / 加入黑名单建议必填"
      />
    </div>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="confirm">确认</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { updateSocialCapacityStatus } from '@/api/capacity/social-capacity/list';
  import type { SocialCapacityListItem } from '@/api/capacity/social-capacity/list/model';

  const props = defineProps<{
    visible: boolean;
    row?: SocialCapacityListItem | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const targetStatus = ref<number | undefined>(undefined);
  const remark = ref('');
  const saving = ref(false);

  const statusLabel = (s?: number) =>
    s === 0
      ? '未生效'
      : s === 1
        ? '正常'
        : s === 2
          ? '停用'
          : s === 3
            ? '黑名单'
            : '—';

  const targetOptions = computed(() => {
    const s = props.row?.status;
    if (s === 1) {
      return [
        { value: 2, label: '停用' },
        { value: 3, label: '加入黑名单' }
      ];
    }
    if (s === 2) {
      return [
        { value: 1, label: '恢复启用' },
        { value: 3, label: '加入黑名单' }
      ];
    }
    if (s === 3) {
      return [{ value: 1, label: '移出黑名单（恢复启用）' }];
    }
    if (s === 0) {
      return [
        { value: 1, label: '启用' },
        { value: 2, label: '停用' }
      ];
    }
    return [];
  });

  const onOpen = () => {
    targetStatus.value = targetOptions.value[0]?.value;
    remark.value = '';
  };

  watch(
    () => props.visible,
    (v) => {
      if (!v) {
        targetStatus.value = undefined;
        remark.value = '';
      }
    }
  );

  const confirm = async () => {
    if (!props.row?.id || targetStatus.value === undefined) {
      EleMessage.warning({ message: '请选择目标状态', plain: true });
      return;
    }
    if (targetStatus.value === 3 && !remark.value) {
      try {
        await ElMessageBox.confirm('加入黑名单未填写原因，是否继续？', '系统提示', {
          type: 'warning'
        });
      } catch {
        return;
      }
    }
    saving.value = true;
    try {
      await updateSocialCapacityStatus(props.row.id, {
        status: targetStatus.value,
        remark: remark.value || undefined
      });
      EleMessage.success({ message: '状态变更成功', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '状态变更失败', plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style scoped>
  .sc-status {
    min-height: 160px;
  }
  .sc-status__line {
    margin: 0 0 6px;
    font-size: 14px;
  }
  .sc-status__line--remark {
    margin-top: 12px;
  }
  .sc-status__select {
    width: 100%;
  }
</style>
