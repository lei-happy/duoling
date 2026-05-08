<!--
  承运商邀请激活弹窗
  - 路径 B（链接式）：未注册手机号，生成可分发邀请链接
  - fast-path（直连）：对方已是 lite 租户，一键直接建立互联，无需对方确认
  - 已开户其他企业：仅提示请联系对方管理员，禁用操作
-->
<template>
  <el-dialog
    title="发起承运商互联邀请"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <div v-if="data" class="invite-block">
      <p class="line">
        承运商：<b>{{ data.carrierName }}</b>
        <span class="phone">联系电话：<b>{{ data.contactPhone }}</b></span>
      </p>

      <!-- 注册状态检查 -->
      <div v-loading="checking" class="phone-status">
        <template v-if="checked && phoneCheck">
          <!-- A. 已注册且为 lite 租户：可走 fast-path 直连 -->
          <el-alert
            v-if="phoneCheck.registered && phoneCheck.canFastLink && !fastLinked"
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              对方已是
              <b>智途轻量版</b>
              用户
              <span v-if="phoneCheck.tenantName">
                （{{ phoneCheck.tenantName }}）
              </span>
            </template>
            <div class="alert-body">
              <p>
                可<b>直接建立互联</b>，无需对方再次确认。建立后该
                轻量版企业将出现在您的"承运商列表"中、互联状态为"已激活"。
              </p>
            </div>
          </el-alert>

          <!-- A2. fast-path 完成后 -->
          <el-alert
            v-else-if="fastLinked"
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              已直接建立互联
            </template>
            <div class="alert-body">
              <p>
                您与
                <b v-if="phoneCheck.tenantName">{{ phoneCheck.tenantName }}</b>
                的承运商互联关系已建立。可直接关闭本窗口，承运商
                列表会刷新为"已激活"。
              </p>
            </div>
          </el-alert>

          <!-- B. 已注册但不是 lite（已是其他企业管理员/员工）：拒绝 -->
          <el-alert
            v-else-if="phoneCheck.registered"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #title>
              该手机号<b>已在其他企业开户</b>，无法通过链接邀请激活
            </template>
            <div class="alert-body">
              <p v-if="phoneCheck.tenantName">
                所属企业：<b>{{ phoneCheck.tenantName }}</b>
              </p>
              <p v-if="phoneCheck.adminName || phoneCheck.adminPhoneMasked">
                请联系对方管理员
                <b>{{ phoneCheck.adminName || '（未设置姓名）' }}</b>
                <span v-if="phoneCheck.adminPhoneMasked">
                  （{{ phoneCheck.adminPhoneMasked }}）
                </span>
                由其在系统中接受您的邀请。
              </p>
              <p v-else>
                请联系对方在系统中确认接受邀请（互联进阶路径 C 即将开放）。
              </p>
            </div>
          </el-alert>

          <!-- C. 未注册：可正常生成邀请链接 -->
          <el-alert
            v-else
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              该手机号<b>尚未在平台开户</b>
            </template>
            <div class="alert-body">
              <p>
                生成邀请链接后，您可以通过微信等渠道转发给对方。
                对方点击链接、用此手机号完成注册，即可自动开通
                <b>免费轻量版（lite）</b>账号并与本企业建立承运商互联。
              </p>
            </div>
          </el-alert>
        </template>
      </div>

      <!-- 邀请链接展示区（路径 B 生成后） -->
      <div v-if="inviteUrl" class="link-box">
        <div class="link-label">邀请链接（7 天内有效）：</div>
        <div class="link-row">
          <el-input
            ref="urlInputRef"
            :model-value="inviteUrl"
            readonly
            size="default"
          />
          <el-button type="primary" @click="copyUrl">
            <el-icon><DocumentCopy /></el-icon>
            复制链接
          </el-button>
        </div>
        <p class="link-tip">
          已复制后，请通过微信、企业微信、钉钉等渠道发送给
          <b>{{ data.contactPhone }}</b> 对应的联系人。
        </p>
      </div>
    </div>

    <template #footer>
      <el-button @click="updateVisible(false)">
        {{ inviteUrl || fastLinked ? '完成' : '取消' }}
      </el-button>

      <!-- fast-path：直接建立互联按钮 -->
      <el-button
        v-if="!fastLinked && phoneCheck?.registered && phoneCheck?.canFastLink"
        type="primary"
        :loading="loading"
        @click="submit"
      >
        直接建立互联
      </el-button>

      <!-- 路径 B：生成邀请链接 -->
      <el-button
        v-else-if="!inviteUrl && !fastLinked"
        type="primary"
        :loading="loading"
        :disabled="!canGenerate"
        @click="submit"
      >
        生成邀请链接
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { DocumentCopy } from '@element-plus/icons-vue';
  import { checkInvitePhone, inviteCarrier } from '@/api/partner/carrier';
  import type {
    Carrier,
    CarrierInvitePhoneCheckResult,
    CarrierListItem
  } from '@/api/partner/carrier/model';

  const props = defineProps<{
    visible: boolean;
    data: CarrierListItem | Carrier | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const checking = ref(false);
  const checked = ref(false);
  const phoneCheck = ref<CarrierInvitePhoneCheckResult | null>(null);
  const inviteUrl = ref<string>('');
  const fastLinked = ref(false);

  /** 路径 B 是否允许生成链接（未注册手机号） */
  const canGenerate = computed(() => {
    return checked.value && !!phoneCheck.value && !phoneCheck.value.registered;
  });

  const reset = () => {
    loading.value = false;
    checking.value = false;
    checked.value = false;
    phoneCheck.value = null;
    inviteUrl.value = '';
    fastLinked.value = false;
  };

  watch(
    () => props.visible,
    (val) => {
      if (!val) reset();
    }
  );

  const onOpen = async () => {
    reset();
    const phone = props.data?.contactPhone?.trim();
    if (!phone) {
      checked.value = true;
      return;
    }
    checking.value = true;
    try {
      phoneCheck.value = await checkInvitePhone(phone);
    } catch (e: any) {
      EleMessage.error({ message: e.message || '查询注册状态失败', plain: true });
      phoneCheck.value = { phone, registered: false };
    } finally {
      checking.value = false;
      checked.value = true;
    }
  };

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const submit = async () => {
    if (!props.data?.id) return;
    loading.value = true;
    try {
      const res = await inviteCarrier(props.data.id, { channel: 'link' });
      if (res?.fastLinked) {
        // fast-path：后端直接互联完成
        fastLinked.value = true;
        EleMessage.success({ message: '已直接建立互联', plain: true });
        emit('done');
      } else {
        inviteUrl.value = res?.inviteUrl ?? '';
        EleMessage.success({ message: '邀请链接已生成', plain: true });
        emit('done');
        await copyUrl(true);
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const copyUrl = async (silent = false) => {
    if (!inviteUrl.value) return;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(inviteUrl.value);
      } else {
        const ta = document.createElement('textarea');
        ta.value = inviteUrl.value;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      if (!silent) {
        EleMessage.success({ message: '链接已复制到剪贴板', plain: true });
      }
    } catch {
      if (!silent) {
        EleMessage.warning({
          message: '自动复制失败，请手动选中链接复制',
          plain: true
        });
      }
    }
  };
</script>

<style scoped>
  .invite-block {
    padding: 4px 4px 12px;
  }
  .invite-block .line {
    margin: 0 0 12px;
    line-height: 1.6;
  }
  .invite-block .line .phone {
    margin-left: 16px;
    color: var(--el-text-color-secondary);
  }
  .phone-status {
    min-height: 60px;
    margin-bottom: 12px;
  }
  .alert-body {
    margin-top: 4px;
    line-height: 1.7;
  }
  .alert-body p {
    margin: 0;
  }
  .link-box {
    margin-top: 8px;
    padding: 12px 12px 8px;
    background: var(--el-fill-color-lighter);
    border-radius: 6px;
  }
  .link-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    margin-bottom: 6px;
  }
  .link-row {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .link-tip {
    margin: 8px 0 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
  }
</style>
