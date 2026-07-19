<!-- 顶栏版本升级说明入口：图标点击查看历史更新；关键版本首次登录强制弹框，看过后不再弹 -->
<template>
  <!-- 外层 hover 由 header-right 的 layout-tool 提供，此处勿再套一层，否则会出现双重高亮 -->
  <div
    style="display: flex; align-items: center; height: 100%"
    @click="openDrawer"
  >
    <el-badge
      :value="unreadCount"
      :hidden="!unreadCount"
      style="line-height: 1; padding: 4px 0"
    >
      <el-icon style="transform: scale(1.12)">
        <Promotion />
      </el-icon>
    </el-badge>
  </div>

  <!-- 历史更新列表抽屉 -->
  <el-drawer
    v-model="drawerVisible"
    title="版本升级说明"
    size="480px"
    :append-to-body="true"
    @open="loadHistory"
  >
    <div v-loading="historyLoading" class="changelog-history">
      <el-empty
        v-if="!historyLoading && !historyList.length"
        description="暂无版本更新记录"
        :image-size="90"
      />
      <el-timeline v-else>
        <el-timeline-item
          v-for="item in historyList"
          :key="item.id"
          :timestamp="item.release_date"
          placement="top"
          type="primary"
        >
          <div class="changelog-item">
            <div class="changelog-item__head">
              <el-tag size="small" type="primary" :disable-transitions="true">
                {{ item.version }}
              </el-tag>
              <span class="changelog-item__title">{{ item.title }}</span>
            </div>
            <byte-md-viewer
              v-if="item.content"
              :value="item.content"
              :config="viewerConfig"
              class="changelog-item__content"
            />
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-drawer>

  <!-- 关键版本强制弹框 -->
  <el-dialog
    v-model="popupVisible"
    :title="popupTitle"
    width="600px"
    :append-to-body="true"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="changelog-popup"
    @closed="handlePopupClosed"
  >
    <div v-if="currentPopup" class="changelog-popup__body">
      <div class="changelog-popup__meta">
        <el-tag type="primary" :disable-transitions="true">
          {{ currentPopup.version }}
        </el-tag>
        <span class="changelog-popup__date">{{ currentPopup.release_date }}</span>
      </div>
      <h3 class="changelog-popup__title">{{ currentPopup.title }}</h3>
      <byte-md-viewer
        v-if="currentPopup.content"
        :value="currentPopup.content"
        :config="viewerConfig"
        class="changelog-popup__content"
      />
    </div>
    <template #footer>
      <div class="changelog-popup__footer">
        <span v-if="popupList.length > 1" class="changelog-popup__step">
          {{ popupIndex + 1 }} / {{ popupList.length }}
        </span>
        <el-button v-if="!isLastPopup" type="primary" @click="nextPopup">
          下一条
        </el-button>
        <el-button v-else type="primary" @click="confirmPopup">
          我知道了
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { Promotion } from '@element-plus/icons-vue';
  import gfm from '@bytemd/plugin-gfm';
  import 'github-markdown-css/github-markdown-light.css';
  import ByteMdViewer from '@/components/ByteMdViewer/index.vue';
  import {
    getWorkbenchChangelogs,
    getWorkbenchChangelogPopups,
    markWorkbenchChangelogsRead,
    type WorkbenchChangelog
  } from '@/api/home/workbench/changelog';

  defineOptions({ name: 'HeaderChangelog' });

  /** markdown 渲染配置 */
  const viewerConfig = { plugins: [gfm()] };

  /** 未读的强制弹框数量（用于图标角标） */
  const unreadCount = ref(0);

  /** ---- 历史列表抽屉 ---- */
  const drawerVisible = ref(false);
  const historyLoading = ref(false);
  const historyList = ref<WorkbenchChangelog[]>([]);
  let historyLoaded = false;

  const openDrawer = () => {
    drawerVisible.value = true;
  };

  const loadHistory = async () => {
    if (historyLoaded) return;
    historyLoading.value = true;
    try {
      const data = await getWorkbenchChangelogs({ page: 1, limit: 50 });
      historyList.value = data.list || [];
      historyLoaded = true;
    } catch {
      historyList.value = [];
    } finally {
      historyLoading.value = false;
    }
  };

  /** ---- 强制弹框 ---- */
  const popupVisible = ref(false);
  const popupList = ref<WorkbenchChangelog[]>([]);
  const popupIndex = ref(0);

  const currentPopup = computed(() => popupList.value[popupIndex.value] || null);
  const isLastPopup = computed(
    () => popupIndex.value >= popupList.value.length - 1
  );
  const popupTitle = computed(() =>
    popupList.value.length > 1 ? '版本更新提醒' : '版本升级说明'
  );

  const nextPopup = () => {
    if (popupIndex.value < popupList.value.length - 1) {
      popupIndex.value += 1;
    }
  };

  const confirmPopup = () => {
    popupVisible.value = false;
  };

  /** 弹框关闭（无论点确认还是关闭按钮）即视为已读，下次不再弹 */
  const handlePopupClosed = async () => {
    const ids = popupList.value.map((v) => v.id);
    if (!ids.length) return;
    try {
      await markWorkbenchChangelogsRead(ids);
    } catch {
      // best-effort，失败不影响使用
    }
    unreadCount.value = 0;
    // 已读的记录并入历史（若历史已加载）
    historyLoaded = false;
  };

  onMounted(async () => {
    try {
      const items = await getWorkbenchChangelogPopups();
      if (items.length) {
        popupList.value = items;
        popupIndex.value = 0;
        unreadCount.value = items.length;
        popupVisible.value = true;
      }
    } catch {
      // 忽略拉取失败
    }
  });
</script>

<style lang="scss" scoped>
  .changelog-history {
    min-height: 120px;
  }

  .changelog-item__head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }

  .changelog-item__title {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .changelog-popup__meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  .changelog-popup__date {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .changelog-popup__title {
    margin: 0 0 12px;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .changelog-popup__content,
  .changelog-item__content {
    max-height: 46vh;
    overflow: auto;
  }

  .changelog-popup__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
  }

  .changelog-popup__step {
    margin-right: auto;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  /* markdown 内容缩放到弹框合适字号 */
  :deep(.markdown-body) {
    font-size: 14px;
    background: transparent;
  }
</style>
