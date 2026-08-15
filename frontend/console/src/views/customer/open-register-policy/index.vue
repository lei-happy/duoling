<template>
  <ele-page>
    <ele-card title="自助注册策略">
      <template #extra>
        <span class="card-tip">控制自助开户时默认开通的产品版本与试用天数</span>
      </template>
      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="policy-notice"
        title="官网自助注册已下线，这里的配置当前只对承运商邀请激活生效"
        description="官网访客改为留下联系方式，由顾问在「客户列表」手工开户；线索见「官网线索」。"
      />
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
        class="policy-form"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="默认版本" prop="versionCode">
          <el-select
            v-model="form.versionCode"
            placeholder="请选择版本"
            filterable
            style="width: 320px"
          >
            <el-option
              v-for="v in versions"
              :key="v.id"
              :label="`${v.versionName}（${v.versionCode}）`"
              :value="v.versionCode"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="试用天数" prop="trialDays">
          <el-input-number
            v-model="form.trialDays"
            :min="0"
            :max="3650"
            :step="1"
            controls-position="right"
            style="width: 200px"
          />
          <span class="field-hint">0 表示不限期（与长期免费体验一致）</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            保存
          </el-button>
        </el-form-item>
      </el-form>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { listVersions } from '@/api/product';
  import type { ProductVersion } from '@/api/product/model';
  import {
    getOpenRegisterPolicy,
    updateOpenRegisterPolicy
  } from '@/api/customer/open-register-policy';

  defineOptions({ name: 'OpenRegisterPolicy' });

  const formRef = ref<FormInstance | null>(null);
  const loading = ref(false);
  const versions = ref<ProductVersion[]>([]);

  const form = reactive({
    versionCode: 'basic',
    trialDays: 0
  });

  const rules = reactive<FormRules>({
    versionCode: [
      { required: true, message: '请选择版本', trigger: 'change' }
    ],
    trialDays: [
      { required: true, message: '请输入试用天数', trigger: 'blur' }
    ]
  });

  const loadVersions = async () => {
    const res = await listVersions({ page: 1, page_size: 200 });
    versions.value = (res?.list ?? []).filter((v) => v.status === 1);
  };

  const loadPolicy = async () => {
    const p = await getOpenRegisterPolicy();
    form.versionCode = p.versionCode;
    form.trialDays = p.trialDays;
  };

  onMounted(async () => {
    try {
      await loadVersions();
      await loadPolicy();
    } catch (e: any) {
      EleMessage.error({ message: e.message ?? '加载失败', plain: true });
    }
  });

  const handleSubmit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      updateOpenRegisterPolicy({
        versionCode: form.versionCode,
        trialDays: form.trialDays
      })
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg ?? '保存成功', plain: true });
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message ?? '保存失败', plain: true });
        });
    });
  };
</script>

<style scoped>
  .card-tip {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
  .policy-notice {
    max-width: 720px;
    margin-bottom: 20px;
  }
  .policy-form {
    max-width: 560px;
    padding-top: 8px;
  }
  .field-hint {
    margin-left: 12px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
</style>
