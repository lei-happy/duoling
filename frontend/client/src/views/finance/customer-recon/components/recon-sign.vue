<template>
  <el-dialog
    :model-value="visible"
    title="登记客户回签"
    width="480px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="96px">
      <el-form-item label="客户确认人" required>
        <el-input
          v-model="form.signerName"
          maxlength="50"
          placeholder="签字或盖章的客户方人员"
        />
      </el-form-item>
      <el-form-item label="回签时间">
        <el-date-picker
          v-model="form.signedAt"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          placeholder="留空按当前时间"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="回签凭证">
        <el-input
          v-model="form.voucherUrl"
          maxlength="500"
          placeholder="选填，回签扫描件链接"
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
  import { signRecon } from '@/api/finance/customer-recon';

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
      EleMessage.warning({ message: '请填写客户确认人姓名', plain: true });
      return;
    }
    saving.value = true;
    try {
      await signRecon(props.reconId, {
        signerName: form.value.signerName.trim(),
        signedAt: form.value.signedAt,
        voucherUrl: form.value.voucherUrl
      });
      EleMessage.success({ message: '已登记客户回签', plain: true });
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
