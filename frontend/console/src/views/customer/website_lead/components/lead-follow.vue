<!-- 官网线索详情与跟进 -->
<template>
  <ele-modal
    form
    :width="760"
    title="线索详情与跟进"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-descriptions v-if="detail" :column="2" border class="mb-16">
      <el-descriptions-item label="企业名称">
        {{ detail.company_name || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="联系人">
        {{ detail.contact_person || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="手机号">
        {{ detail.contact_phone || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="车队规模">
        {{ fleetLabel(detail.fleet_size) }}
      </el-descriptions-item>
      <el-descriptions-item label="测评档位">
        <template v-if="detail.stage_band">
          {{ detail.stage_band }} · {{ detail.stage_name }}
        </template>
        <span v-else class="lead-muted">未做自测</span>
      </el-descriptions-item>
      <el-descriptions-item label="四维得分">
        <template v-if="detail.total_score != null">
          总分 {{ detail.total_score }}/80 · 业务在线 {{ detail.dim_a }} ·
          数据贯通 {{ detail.dim_b }} · 智能应用 {{ detail.dim_c }} ·
          经营闭环 {{ detail.dim_d }}
        </template>
        <span v-else class="lead-muted">—</span>
      </el-descriptions-item>
      <el-descriptions-item
        v-for="item in profileRows"
        :key="item.label"
        :label="item.label"
      >
        {{ item.value }}
      </el-descriptions-item>
      <el-descriptions-item label="最头疼的事" :span="2">
        <div class="lead-text">{{ detail.pain_point || '未填写' }}</div>
      </el-descriptions-item>
      <el-descriptions-item label="留资时间">
        {{ detail.created_at || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="来源页">
        {{ detail.source_page || '-' }}
      </el-descriptions-item>
      <el-descriptions-item v-if="detail.handler_name" label="上次跟进人">
        {{ detail.handler_name }}
      </el-descriptions-item>
      <el-descriptions-item v-if="detail.contacted_at" label="首次联系时间">
        {{ detail.contacted_at }}
      </el-descriptions-item>
    </el-descriptions>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
      <el-form-item label="跟进状态" prop="status">
        <el-select
          v-model="form.status"
          placeholder="请选择跟进状态"
          style="width: 100%"
        >
          <el-option
            v-for="o in STATUS_OPTIONS"
            :key="o.value"
            :label="o.label"
            :value="o.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="form.status === 2" label="转化租户" prop="converted_tenant_code">
        <el-input
          v-model="form.converted_tenant_code"
          maxlength="32"
          placeholder="开户后的企业编码，便于回溯这条线索的成单"
        />
      </el-form-item>
      <el-form-item label="跟进备注" prop="follow_remark">
        <el-input
          v-model="form.follow_remark"
          type="textarea"
          :rows="4"
          maxlength="2000"
          show-word-limit
          placeholder="记下沟通结果与下一步动作，例如：已加微信，下周二演示"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => modalProps.onCancel?.() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { followWebsiteLead, getWebsiteLead } from '@/api/website-lead';
  import type { WebsiteLead } from '@/api/website-lead/model';
  import { STATUS_OPTIONS, fleetLabel, readableProfile } from '../constants';

  const props = defineProps<{
    data?: WebsiteLead | null;
    onDone?: () => void;
  }>();

  const { modalProps, closeModal } = useModal();
  const loading = ref(false);
  const detail = ref<WebsiteLead | null>(null);
  const formRef = ref<FormInstance | null>(null);
  const form = reactive({
    status: 0,
    follow_remark: '',
    converted_tenant_code: ''
  });

  const rules: FormRules = {
    status: [{ required: true, message: '请选择跟进状态', trigger: 'change' }]
  };

  const profileRows = computed(() =>
    readableProfile(detail.value?.profile_answers)
  );

  onMounted(async () => {
    if (!props.data?.id) return;
    loading.value = true;
    try {
      detail.value = (await getWebsiteLead(props.data.id)) || null;
      form.status = detail.value?.status ?? 0;
      form.follow_remark = detail.value?.follow_remark || '';
      form.converted_tenant_code = detail.value?.converted_tenant_code || '';
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载失败，请重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  });

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid || !props.data?.id) return;
      const loadingMsg = EleMessage.loading({
        message: '正在保存跟进记录，请稍候…',
        plain: true
      });
      followWebsiteLead(props.data.id, {
        status: form.status,
        follow_remark: form.follow_remark,
        converted_tenant_code: form.converted_tenant_code
      })
        .then((msg) => {
          loadingMsg.close();
          EleMessage.success({
            message: msg || '已更新跟进记录',
            plain: true
          });
          props.onDone?.();
          closeModal();
        })
        .catch((e) => {
          loadingMsg.close();
          EleMessage.error({
            message: e.message || '保存失败，请稍后重试',
            plain: true
          });
        });
    });
  };
</script>

<style scoped>
  .mb-16 {
    margin-bottom: 16px;
  }
  .lead-text {
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
  }
  .lead-muted {
    color: var(--el-text-color-placeholder);
  }
</style>
