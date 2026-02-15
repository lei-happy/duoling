<template>
  <ele-page :multi-card="false">
    <ele-card :body-style="{ padding: 0 }">
      <div :class="['message-wrapper', { 'is-mobile': mobile }]">
        <div class="message-side">
          <ele-menus
            :items="menus"
            :default-active="active"
            :mode="mobile ? 'horizontal' : 'vertical'"
          />
        </div>
        <div class="message-body">
          <transition name="slide-right" mode="out-in">
            <keep-alive>
              <message-notice v-if="active == 'notice'" @reload="queryBadge" />
              <message-todo v-else-if="active == 'todo'" @reload="queryBadge" />
              <message-letter v-else @reload="queryBadge" />
            </keep-alive>
          </transition>
        </div>
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, watch } from 'vue';
  import { useRoute } from 'vue-router';
  import { useMessage } from 'ele-admin-plus';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import { useMobile } from '@/utils/use-mobile';
  import MessageNotice from './components/message-notice.vue';
  import MessageLetter from './components/message-letter.vue';
  import MessageTodo from './components/message-todo.vue';
  import { getUnReadNum } from '@/api/example';

  defineOptions({ name: 'UserMessage' });

  const messageIns = useMessage({ inner: true, plain: true });
  const route = useRoute();
  const { mobile } = useMobile();

  /** 导航选中 */
  const active = ref<string>('notice');

  /** 未读数量 */
  const unReadNum = reactive({
    notice: 0,
    letter: 0,
    todo: 0
  });

  /** 菜单数据 */
  const menus = computed<MenuItem[]>(() => {
    return [
      {
        index: 'notice',
        path: '/user/message?type=notice',
        title: '系统通知',
        badge: { value: unReadNum.notice }
      },
      {
        index: 'letter',
        path: '/user/message?type=letter',
        title: '用户私信',
        badge: { value: unReadNum.letter }
      },
      {
        index: 'todo',
        path: '/user/message?type=todo',
        title: '待办事项',
        badge: { value: unReadNum.todo }
      }
    ];
  });

  watch(
    () => route.query.type,
    (type) => {
      if (route.path === '/user/message') {
        active.value = [type].flat()[0] || 'notice';
      }
    },
    { immediate: true }
  );

  /** 查询未读数量 */
  const queryBadge = () => {
    getUnReadNum()
      .then((result) => {
        Object.assign(unReadNum, result);
      })
      .catch((e) => {
        messageIns.error(e.message);
      });
  };

  queryBadge();
</script>

<style lang="scss" scoped>
  .message-wrapper {
    display: flex;
    min-height: 582px;

    .message-side {
      width: 150px;
      flex-shrink: 0;
      display: flex;

      :deep(.el-menu) {
        width: 100%;
        padding-top: 12px;
        background: none;
      }
    }

    .message-body {
      flex: 1;
      padding: 8px 20px 16px 16px;
      box-sizing: border-box;
      overflow: hidden;
    }

    &.is-mobile {
      display: block;
      min-height: 637px;

      .message-side {
        width: auto;
        display: block;

        :deep(.el-menu) {
          justify-content: center;
          padding-top: 8px;
          padding-left: 0;
          padding-right: 0;
          --ele-menu-horizontal-height: 38px;
          --ele-menu-horizontal-item-padding: 8px;
        }
      }

      .message-body {
        padding: 16px;
      }
    }
  }
</style>
