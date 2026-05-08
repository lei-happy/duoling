<!--
  轻量版升级横幅
  仅当当前租户为 lite 版本时挂载在 layout 顶部，
  引导承运商升级到标准版/专业版以解锁完整功能（运单、计费等）。

  提醒机制：
    - 用户点"7 天后再提醒"或"暂不提醒"会按 user_id 维度写入 localStorage
      记录"再次提醒时间戳"。
    - 横幅每次挂载时与当前时间比对，若已过期则恢复显示。
    - 退出登录或换号后，按用户隔离的 key 不互相影响。
-->
<template>
  <div v-if="visible" class="upgrade-banner">
    <span class="text">
      您当前使用的是
      <b>轻量版</b>
      （仅含运力管理与合作客户）。升级到
      <b>标准版</b>
      可解锁运单、计费、客户管理等完整能力。
    </span>
    <div class="actions">
      <el-button type="primary" size="small" @click="goPlans">
        查看升级方案
      </el-button>
      <el-tooltip content="7 天内不再展示此横幅，到期后自动恢复" placement="bottom">
        <el-button text size="small" @click="dismiss">7 天内不再提醒</el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import { useUserStore } from '@/store/modules/user';

  /** 隐藏时长：7 天（毫秒） */
  const HIDE_DURATION_MS = 7 * 24 * 60 * 60 * 1000;
  /** localStorage key 模板：按 userId 隔离，避免共用浏览器互相影响 */
  const STORAGE_KEY_PREFIX = 'upgrade-pro-banner-mute:';

  const userStore = useUserStore();
  const router = useRouter();
  const muteUntil = ref<number>(0);

  /** 当前用户的 mute key */
  const storageKey = computed(() => {
    const uid = userStore.info?.userId ?? 'anon';
    return `${STORAGE_KEY_PREFIX}${uid}`;
  });

  const refreshMuteState = () => {
    const raw = localStorage.getItem(storageKey.value);
    muteUntil.value = raw ? Number(raw) || 0 : 0;
  };

  onMounted(refreshMuteState);

  const visible = computed(() => {
    if (!userStore.isLite) return false;
    if (!muteUntil.value) return true;
    return Date.now() >= muteUntil.value;
  });

  const goPlans = () => {
    router.push('/upgrade-plans');
  };

  const dismiss = () => {
    const until = Date.now() + HIDE_DURATION_MS;
    muteUntil.value = until;
    localStorage.setItem(storageKey.value, String(until));
    const dt = new Date(until);
    const dateStr = `${dt.getMonth() + 1}月${dt.getDate()}日`;
    EleMessage.info({
      message: `已暂不提醒，${dateStr} 后将再次提示升级`,
      plain: true
    });
  };
</script>

<style scoped>
  .upgrade-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 8px 16px;
    background: linear-gradient(90deg, #fff7e6, #ffeccd);
    border-bottom: 1px solid #f5d28b;
    font-size: 13px;
    color: #8a4a00;
  }
  .text b {
    color: #d46b08;
  }
  .actions {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
  }
</style>
