<!-- 顶栏 AI 数字员工入口（炫彩圆形按钮 + hover 弹出员工列表 + 点击打开会话弹窗） -->
<template>
  <ele-popover
    :width="320"
    trigger="hover"
    transition="el-zoom-in-top"
    :show-after="120"
    :hide-after="160"
    :content-style="{ padding: 0 }"
    :body-style="{ overflow: 'hidden' }"
    :popper-options="{
      strategy: 'fixed',
      modifiers: [{ name: 'offset', options: { offset: [0, 5] } }]
    }"
    v-model:visible="popoverVisible"
  >
    <template #reference>
      <div class="ai-orb-wrapper">
        <div class="ai-orb" aria-label="AI 数字员工">
          <div
            class="ai-orb__icon"
            :style="{ '--ai-orb-icon-url': aiOrbIconUrl }"
          ></div>
          <div class="ai-orb__halo"></div>
        </div>
      </div>
    </template>

    <div class="ai-entry-popover">
      <div class="ai-entry-popover__header">
        <div class="ai-entry-popover__title">AI 数字员工</div>
        <div class="ai-entry-popover__sub">
          {{
            employees.length ? '选择一位数字员工开始对话' : '暂无可用数字员工'
          }}
        </div>
      </div>
      <div v-if="loading" class="ai-entry-popover__loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中…</span>
      </div>
      <div v-else-if="!employees.length" class="ai-entry-popover__empty">
        未配置数字员工，请联系运营在「AI 数字员工」中创建
      </div>
      <div v-else class="ai-entry-popover__list">
        <div
          v-for="emp in employees"
          :key="emp.code"
          class="ai-entry-card"
          @click="openChat(emp)"
        >
          <el-avatar :size="36" :src="normalizeAvatar(emp.avatar)">
            {{ (emp.name || '').slice(0, 1) }}
          </el-avatar>
          <div class="ai-entry-card__body">
            <div class="ai-entry-card__name">
              <span>{{ emp.name }}</span>
              <el-tag size="small" effect="plain" style="margin-left: 6px">
                {{ empTypeText(emp.employeeType) }}
              </el-tag>
            </div>
            <div class="ai-entry-card__desc">
              {{ emp.description || '企业数字员工' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </ele-popover>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { useModal } from 'ele-admin-plus';
  import { Loading } from '@element-plus/icons-vue';
  import { listAiEmployees } from '@/api/ai';
  import type { AiEmployee } from '@/api/ai/model';
  import { getSvgIconUrl } from '@/components/IconSelect/util';

  const { openModal } = useModal();

  const employees = ref<AiEmployee[]>([]);
  const loading = ref(false);
  const popoverVisible = ref(false);

  /** 顶栏圆形图标使用 menu-icons/aizhushou.svg 做 mask，便于跟随主题色 */
  const aiOrbIconUrl = `url('${getSvgIconUrl('aizhushou') || ''}')`;

  onMounted(async () => {
    loading.value = true;
    try {
      employees.value = await listAiEmployees();
    } catch (e) {
      // 静默失败：当前租户可能没有启用功能或后端异常，不影响其它顶栏入口
      console.warn('[header-ai-entry] 加载数字员工失败', e);
      employees.value = [];
    } finally {
      loading.value = false;
    }
  });

  function normalizeAvatar(p?: string): string | undefined {
    const s = (p || '').trim();
    if (!s) return undefined;
    if (
      s.startsWith('http://') ||
      s.startsWith('https://') ||
      s.startsWith('data:')
    ) {
      return s;
    }
    return s.startsWith('/') ? s : `/${s}`;
  }

  function empTypeText(t?: string): string {
    switch (t) {
      case 'form_recorder':
        return '录单员';
      case 'data_analyst':
        return '数据分析员';
      case 'archivist':
        return '档案管理员';
      default:
        return '数字员工';
    }
  }

  function openChat(emp: AiEmployee) {
    popoverVisible.value = false;
    openModal({
      modalId: 'ai-chat-modal',
      type: 'modal',
      asyncComponent: () =>
        import('@/views/dashboard/ai-assistant/components/ai-chat-panel.vue'),
      props: {
        // 隐藏默认标题栏：title 留空 + modalClass 由全局样式接管 header 隐藏
        title: '',
        showClose: false,
        // 容器宽 80vw、高 90vh，由 ele-modal 内置的 margin:auto 完成水平 + 垂直居中
        width: '80vw',
        height: '90vh',
        customFooter: true,
        modalClass: 'ai-chat-modal',
        bodyStyle: { padding: 0, overflow: 'hidden' }
      },
      componentProps: {
        defaultEmployeeCode: emp.code,
        embedded: true
      }
    });
  }
</script>

<style lang="scss" scoped>
  /* 圆形炫彩按钮 */
  .ai-orb-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    cursor: pointer;
  }

  .ai-orb {
    position: relative;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: conic-gradient(
      from 120deg,
      #6a8bff 0deg,
      #a36bff 90deg,
      #ff7adb 180deg,
      #ffce6b 260deg,
      #6a8bff 360deg
    );
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.18) inset,
      0 2px 8px rgba(120, 90, 255, 0.35);
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;
    overflow: hidden;
  }

  .ai-orb::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: radial-gradient(
      circle at 30% 30%,
      rgba(255, 255, 255, 0.55) 0%,
      rgba(255, 255, 255, 0) 55%
    );
    pointer-events: none;
  }

  .ai-orb__icon {
    position: absolute;
    inset: 5px;
    background-color: #ffffff;
    -webkit-mask: var(--ai-orb-icon-url) center / contain no-repeat;
    mask: var(--ai-orb-icon-url) center / contain no-repeat;
    z-index: 1;
  }

  .ai-orb__halo {
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    background: conic-gradient(
      from 0deg,
      rgba(106, 139, 255, 0.5),
      rgba(163, 107, 255, 0.5),
      rgba(255, 122, 219, 0.5),
      rgba(255, 206, 107, 0.5),
      rgba(106, 139, 255, 0.5)
    );
    filter: blur(6px);
    opacity: 0;
    z-index: -1;
    transition: opacity 0.3s ease;
  }

  .ai-orb-wrapper:hover .ai-orb {
    transform: scale(1.06);
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.3) inset,
      0 2px 12px rgba(120, 90, 255, 0.55);
  }
  .ai-orb-wrapper:hover .ai-orb__halo {
    opacity: 1;
  }

  /* 弹层内容 */
  .ai-entry-popover {
    &__header {
      padding: 14px 16px 8px;
    }
    &__title {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
    &__sub {
      margin-top: 4px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__loading,
    &__empty {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 18px 16px 22px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__list {
      max-height: calc(100vh - 220px);
      overflow-y: auto;
      padding: 4px 8px 10px;
    }
  }

  .ai-entry-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.15s;

    &:hover {
      background-color: var(--el-fill-color-light);
    }
    &__body {
      flex: 1;
      min-width: 0;
    }
    &__name {
      display: flex;
      align-items: center;
      font-size: 13px;
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    &__desc {
      margin-top: 4px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
  }
</style>

<!--
  ai-chat-modal 渲染在 body 层（el-dialog teleport），scoped 样式无法命中，
  这里用一个非 scoped 的 style 块单独处理：
  1) 弹窗高度由 ele-modal 的 height 属性直接控制（90vh），margin: auto 完成上下居中；
  2) 隐藏弹窗自带的 header 与 footer，由面板自身渲染浮动关闭按钮；
  3) 让 body 撑满弹窗剩余空间，去掉默认内边距。

  注意：modalClass 会被加到根元素 .el-overlay 上，因此设置弹框尺寸需要写在
  .el-dialog 上（这里通过 ele-modal 的 height prop 处理，无需在 css 里 hack）。
-->
<style lang="scss">
  .ai-chat-modal {
    > .el-overlay-dialog > .el-dialog {
      margin: auto !important;
      border-radius: 12px;
      overflow: hidden;
    }

    .el-dialog__header {
      display: none;
    }
    .el-dialog__footer {
      display: none;
    }
    .el-dialog__body {
      flex: 1;
      min-height: 0;
      padding: 0 !important;
      overflow: hidden;
    }
  }
</style>
