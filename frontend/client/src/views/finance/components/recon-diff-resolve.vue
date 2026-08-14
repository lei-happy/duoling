<template>
  <el-dialog
    :model-value="visible"
    title="处置对账差异"
    width="520px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-descriptions :column="1" border size="small" class="diff-info">
      <el-descriptions-item label="差异类型">
        {{ diff?.diffTypeLabel || '--' }}
        <el-tag
          v-if="diff?.severity === 2"
          type="danger"
          size="small"
          effect="plain"
          style="margin-left: 6px"
        >
          阻塞确认
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="业务单据">
        {{ diff?.bizDocNo || diff?.bizDocId }}
      </el-descriptions-item>
      <el-descriptions-item label="快照值 → 当前值">
        {{ diff?.expectedValue || '--' }} → {{ diff?.actualValue || '--' }}
      </el-descriptions-item>
    </el-descriptions>

    <el-form :model="form" label-width="88px">
      <el-form-item label="处置方式" required>
        <el-select v-model="form.status" style="width: 100%">
          <el-option
            v-for="o in DIFF_RESOLVE_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="处置说明" required>
        <el-input
          v-model="form.resolution"
          type="textarea"
          :rows="3"
          maxlength="200"
          :placeholder="placeholder"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        提交处置
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { resolveReconDiff } from '@/api/finance/customer-recon';
  import { resolveCarrierReconDiff } from '@/api/finance/carrier-recon';
  import type { ReconDiff } from '@/api/finance/customer-recon/model';
  import { DIFF_RESOLVE_OPTIONS } from '../status-config';

  const props = withDefaults(
    defineProps<{
      visible: boolean;
      diff?: ReconDiff | null;
      /** 差异挂在哪类对账单上，决定调哪条处置接口 */
      side?: 'customer' | 'carrier';
    }>(),
    { side: 'customer' }
  );

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const saving = ref(false);
  const form = ref<{ status: number; resolution?: string }>({ status: 2 });

  const placeholder = computed(() =>
    props.side === 'carrier'
      ? '说明怎么处理的，例如：与承运商核对后按 8 台确认'
      : '说明怎么处理的，例如：与客户核对后按 8 台确认'
  );

  const onOpen = () => {
    form.value = { status: 2 };
  };

  const save = async () => {
    if (!props.diff) return;
    if ((form.value.resolution || '').trim().length < 2) {
      EleMessage.warning({ message: '请填写处置说明', plain: true });
      return;
    }
    saving.value = true;
    try {
      const payload = {
        status: form.value.status,
        resolution: (form.value.resolution || '').trim()
      };
      if (props.side === 'carrier') {
        await resolveCarrierReconDiff(props.diff.id, payload);
      } else {
        await resolveReconDiff(props.diff.id, payload);
      }
      EleMessage.success({ message: '差异已处置', plain: true });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '处置失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .diff-info {
    margin-bottom: 14px;
  }
</style>
