<template>
  <el-dialog
    :model-value="visible"
    title="登记承运商回签"
    width="480px"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <p class="finance-form-tip">
      登记承运商签字或盖章的回签结果。确认人必填，时间留空按现在记。
    </p>
    <el-form :model="form" label-width="0" class="finance-edit-form">
      <el-form-item>
        <floating-label
          label="请输入承运商确认人"
          type="input"
          v-model="form.signerName"
          :maxlength="50"
          :clearable="false"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.signedAt"
          label="回签时间，留空按现在"
          type="date"
          date-type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入回签凭证链接，选填"
          type="input"
          v-model="form.voucherUrl"
          :maxlength="500"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        登记回签
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { signCarrierRecon } from '@/api/finance/carrier-recon';

  const props = defineProps<{ visible: boolean; reconId: number }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const saving = ref(false);
  const form = ref<{
    signerName?: string;
    signedAt?: string;
    voucherUrl?: string;
  }>({});

  const onOpen = () => {
    form.value = {};
  };

  const save = async () => {
    if (!form.value.signerName?.trim()) {
      EleMessage.warning({ message: '请填写承运商确认人姓名', plain: true });
      return;
    }
    saving.value = true;
    try {
      await signCarrierRecon(props.reconId, {
        signerName: form.value.signerName.trim(),
        signedAt: form.value.signedAt,
        voucherUrl: form.value.voucherUrl
      });
      EleMessage.success({ message: '已登记承运商回签', plain: true });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '登记失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  @use '../../_shared/ui.scss';
</style>
