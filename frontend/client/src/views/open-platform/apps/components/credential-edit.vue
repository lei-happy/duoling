<template>
  <ele-modal
    form
    :width="560"
    :title="isUpdate ? '调整密钥授权' : '创建 API 密钥'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="可访问的能力" prop="scope">
        <el-select
          v-model="form.scope"
          multiple
          filterable
          collapse-tags
          collapse-tags-tooltip
          placeholder="勾选这把密钥允许访问的能力（最小授权）"
          style="width: 100%"
        >
          <el-option
            v-for="c in capabilities"
            :key="c.code"
            :label="`${c.name}（${c.code}）`"
            :value="c.code"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="IP 白名单（选填）">
        <el-input
          v-model.trim="form.ip_whitelist"
          type="textarea"
          :rows="2"
          placeholder="限制只允许这些 IP 调用，多个用英文逗号隔开；留空表示不限制"
        />
      </el-form-item>
      <el-form-item label="有效期（选填）" v-if="!isUpdate">
        <el-date-picker
          v-model="form.expires_at"
          type="datetime"
          placeholder="到期后自动失效；留空表示长期有效"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => closeModal() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    listCapabilities,
    createCredential,
    updateCredentialScope
  } from '@/api/open-platform';
  import type { Capability, Credential } from '@/api/open-platform/model';

  const props = defineProps<{
    appId: number;
    data?: Credential | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
    (e: 'reveal', cred: Credential): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(!!props.data);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);
  const capabilities = ref<Capability[]>([]);

  const form = reactive<{
    scope: string[];
    ip_whitelist: string;
    expires_at: string | null;
  }>({
    scope: props.data?.scope ? [...props.data.scope] : [],
    ip_whitelist: props.data?.ip_whitelist || '',
    expires_at: null
  });

  const rules = reactive<FormRules>({
    scope: [
      {
        required: true,
        type: 'array',
        min: 1,
        message: '请至少勾选一个能力',
        trigger: 'change'
      }
    ]
  });

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const fail = (e: any) => {
        loading.value = false;
        EleMessage.error({
          message: e.message || '操作失败，请稍后重试',
          plain: true
        });
      };
      if (isUpdate.value && props.data) {
        updateCredentialScope(props.data.id, {
          scope: form.scope,
          ip_whitelist: form.ip_whitelist
        })
          .then(() => {
            loading.value = false;
            EleMessage.success({ message: '已保存', plain: true });
            closeModal();
            emit('done');
          })
          .catch(fail);
      } else {
        createCredential(props.appId, {
          scope: form.scope,
          ip_whitelist: form.ip_whitelist,
          expires_at: form.expires_at
        })
          .then((cred) => {
            loading.value = false;
            closeModal();
            emit('done');
            if (cred) emit('reveal', cred);
          })
          .catch(fail);
      }
    });
  };

  onMounted(async () => {
    try {
      capabilities.value = await listCapabilities('api');
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载能力目录失败，请稍后重试',
        plain: true
      });
    }
  });
</script>
