<!--
  「不通过」类处置的统一弹层：驳回 / 强制下架 / 抽检不通过

  三个动作的界面元素是同一套（选原因 + 写给企业看的说明），差别只在后果不同。
  合成一个弹层，是为了让说明文案的必填规则、模板套用、后果提示这三件事只有
  一份实现——分成三个文件时，最先失去同步的一定是「这段话会原样发给企业」
  这个前提，而那正是运营最容易写错的地方。
-->
<template>
  <ele-modal form :width="620" :title="config.title" v-bind="modalProps">
    <el-alert
      :type="config.alertType"
      :closable="false"
      show-icon
      :title="config.consequence"
      style="margin-bottom: 14px"
    />

    <div class="eco-deny__post">
      <div class="eco-deny__post-title">{{ post.title }}</div>
      <div class="eco-deny__post-meta">
        {{ post.postNo }} ·
        {{ post.ownerTenantName || post.ownerTenantCode }}
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="96px"
      @submit.prevent="submit"
    >
      <el-form-item :label="config.reasonCodeLabel" prop="reasonCode">
        <el-select
          v-model="form.reasonCode"
          :clearable="!config.reasonCodeRequired"
          placeholder="请选择原因"
          style="width: 100%"
          @change="fillTemplate"
        >
          <el-option
            v-for="r in reasons"
            :key="r.value"
            :label="r.label"
            :value="r.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="给企业的说明" prop="reason">
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="4"
          maxlength="500"
          show-word-limit
          :placeholder="config.reasonPlaceholder"
        />
        <div class="eco-deny__tip">
          这段话会原样展示给发布方，请写清楚哪里有问题、该怎么改。
        </div>
      </el-form-item>

      <el-form-item v-if="mode === 'force-delist'" label="免审白名单">
        <el-switch v-model="form.revokeWhitelist" />
        <span class="eco-deny__switch-text">
          同时移出免审白名单（建议保持开启，否则这家企业下一条照样直通上架）
        </span>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="() => modalProps.onCancel?.()">取消</el-button>
      <el-button :type="config.confirmType" :loading="loading" @click="submit">
        {{ config.confirmText }}
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    forceDelistPost,
    rejectPost,
    spotCheckFail
  } from '@/api/ecosystem/audit';
  import type {
    AuditPost,
    AuditRejectReason
  } from '@/api/ecosystem/audit/model';

  const props = defineProps<{
    mode: 'reject' | 'force-delist' | 'spot-fail';
    post: AuditPost;
    reasons: AuditRejectReason[];
    onDone?: () => void;
  }>();

  const { modalProps, closeModal } = useModal();

  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);
  const form = reactive<{
    reasonCode?: number;
    reason: string;
    revokeWhitelist: boolean;
  }>({
    reasonCode: void 0,
    reason: '',
    revokeWhitelist: true
  });

  const CONFIGS = {
    reject: {
      title: '驳回挂牌',
      alertType: 'warning' as const,
      consequence: '驳回后挂牌回到发布方的「已驳回」，他改好可以重新提交。',
      reasonCodeLabel: '驳回原因',
      reasonCodeRequired: true,
      reasonPlaceholder: '留空就用所选原因的标准说明发给企业',
      confirmText: '确定驳回',
      confirmType: 'danger' as const
    },
    'force-delist': {
      title: '强制下架',
      alertType: 'error' as const,
      consequence:
        '下架后挂牌立即从大厅移出，正在洽谈的同行会收到通知。已经进入成交的挂牌不能这样下架，需要到成交单里走终止流程。',
      reasonCodeLabel: '处置原因',
      reasonCodeRequired: false,
      reasonPlaceholder: '必填。说明哪里违规，发布方能看到这段话',
      confirmText: '确定强制下架',
      confirmType: 'danger' as const
    },
    'spot-fail': {
      title: '抽检不通过',
      alertType: 'error' as const,
      consequence:
        '抽检不通过会下架这条挂牌并移出免审白名单，这家企业之后发布的内容都要过人工审核。若挂牌已进入成交，则只记抽检失败并移出白名单，不下架。',
      reasonCodeLabel: '问题类型',
      reasonCodeRequired: false,
      reasonPlaceholder: '必填。写清抽检发现了什么问题',
      confirmText: '确定不通过',
      confirmType: 'danger' as const
    }
  };

  const config = computed(() => CONFIGS[props.mode]);

  /** 「其他」这类没有标准模板的原因，必须自己写说明 */
  const selectedReason = computed(() =>
    props.reasons.find((r) => r.value === form.reasonCode)
  );

  const reasonRequired = computed(
    () => props.mode !== 'reject' || !!selectedReason.value?.reasonRequired
  );

  const rules = computed<FormRules>(() => ({
    reasonCode: config.value.reasonCodeRequired
      ? [{ required: true, message: '请选择原因', trigger: 'change' }]
      : [],
    reason: reasonRequired.value
      ? [
          {
            required: true,
            message: '请写一下原因，发布方要靠这段话知道怎么改',
            trigger: 'blur'
          }
        ]
      : []
  }));

  /** 换原因时把标准说明填进来，运营可以直接改，也可以清空走模板 */
  const fillTemplate = () => {
    const template = selectedReason.value?.template;
    if (!template) {
      return;
    }
    const isUntouched =
      !form.reason.trim() ||
      props.reasons.some((r) => r.template && r.template === form.reason);
    if (isUntouched) {
      form.reason = template;
    }
  };

  watch(reasonRequired, () => {
    formRef.value?.clearValidate?.('reason');
  });

  const submit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      const reason = form.reason.trim();
      loading.value = true;
      const request = () => {
        if (props.mode === 'reject') {
          return rejectPost(props.post.id, {
            reasonCode: form.reasonCode as number,
            reason: reason || void 0
          });
        }
        if (props.mode === 'force-delist') {
          return forceDelistPost(props.post.id, {
            reason,
            reasonCode: form.reasonCode,
            revokeWhitelist: form.revokeWhitelist
          });
        }
        return spotCheckFail(props.post.id, {
          reason,
          reasonCode: form.reasonCode
        });
      };
      request()
        .then(({ message }) => {
          loading.value = false;
          EleMessage.success({
            message: message || '已处理',
            plain: true
          });
          props.onDone?.();
          closeModal();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };
</script>

<style lang="scss" scoped>
  .eco-deny__post {
    margin-bottom: 14px;
    padding: 10px 12px;
    border-radius: 6px;
    background: var(--el-fill-color-light);
  }

  .eco-deny__post-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .eco-deny__post-meta {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-deny__tip {
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }

  .eco-deny__switch-text {
    margin-left: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
