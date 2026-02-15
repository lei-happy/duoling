<!-- 顶栏消息通知 -->
<template>
  <ele-popover
    :width="336"
    trigger="click"
    transition="el-zoom-in-top"
    :content-style="{ padding: 0 }"
    :body-style="{ overflow: 'hidden' }"
    :popper-style="{ maxWidth: 'calc(100% - 32px)' }"
    :popper-options="{
      strategy: 'fixed',
      modifiers: [{ name: 'offset', options: { offset: [0, 5] } }]
    }"
  >
    <template #reference>
      <div style="display: flex; align-items: center; height: 100%">
        <el-badge
          :value="unreadNum"
          :hidden="!unreadNum"
          style="line-height: 1; padding: 4px 0"
        >
          <el-icon style="transform: scale(1.17)">
            <BellOutlined />
          </el-icon>
        </el-badge>
      </div>
    </template>
    <ele-tabs
      ref="tabRef"
      :center="true"
      v-model="active"
      :items="[
        { name: 'notice', label: '通知' },
        { name: 'letter', label: '私信' },
        { name: 'todo', label: '待办' }
      ]"
      class="notice-tabs"
    >
      <template #label="{ item, label }">
        <span>{{ label }}</span>
        <span v-if="item.name === 'notice' && notices.length">
          ({{ notices.length }})
        </span>
        <span v-if="item.name === 'letter' && letters.length">
          ({{ letters.length }})
        </span>
        <span v-if="item.name === 'todo' && todos.length">
          ({{ todos.length }})
        </span>
      </template>
      <template #notice>
        <div class="list-wrapper">
          <div v-for="item in notices" :key="item.id" class="list-item">
            <div class="list-item-icon" :style="{ background: item.color }">
              <el-icon>
                <Comment
                  v-if="item.icon === 'report'"
                  style="transform: translateY(1px)"
                />
                <Stamp v-else-if="item.icon === 'leave'" />
                <Promotion v-else-if="item.icon === 'meeting'" />
                <Checked v-else-if="item.icon === 'interview'" />
                <BellFilled v-else-if="item.icon === 'salary'" />
              </el-icon>
            </div>
            <div class="list-item-body">
              <ele-ellipsis>{{ item.title }}</ele-ellipsis>
              <ele-ellipsis type="placeholder" class="list-item-text">
                {{ item.time }}
              </ele-ellipsis>
            </div>
          </div>
        </div>
        <div v-if="notices.length" class="bottom-tools">
          <div class="bottom-tool" @click="clearNotice">清空通知</div>
          <el-divider direction="vertical" style="margin: 0; width: 0" />
          <router-link to="/user/message?type=notice" class="bottom-tool">
            查看更多
          </router-link>
        </div>
        <el-empty v-else description="已查看所有通知" :image-size="68" />
      </template>
      <template #letter>
        <div class="list-wrapper">
          <div v-for="item in letters" :key="item.id" class="list-item">
            <el-avatar :size="32" :src="item.avatar" />
            <div class="list-item-body">
              <ele-ellipsis>{{ item.title }}</ele-ellipsis>
              <ele-ellipsis type="placeholder" class="list-item-text">
                {{ item.content }}
              </ele-ellipsis>
              <ele-ellipsis type="placeholder" class="list-item-text">
                {{ item.time }}
              </ele-ellipsis>
            </div>
          </div>
        </div>
        <div v-if="letters.length" class="bottom-tools">
          <div class="bottom-tool" @click="clearLetter">清空私信</div>
          <el-divider direction="vertical" style="margin: 0; width: 0" />
          <router-link to="/user/message?type=letter" class="bottom-tool">
            查看更多
          </router-link>
        </div>
        <el-empty v-else description="已读完所有私信" :image-size="68" />
      </template>
      <template #todo>
        <div class="list-wrapper">
          <div v-for="item in todos" :key="item.id" class="list-item">
            <div class="list-item-body">
              <ele-ellipsis>{{ item.title }}</ele-ellipsis>
              <ele-ellipsis type="placeholder" class="list-item-text">
                {{ item.description }}
              </ele-ellipsis>
            </div>
            <el-tag
              v-if="item.status === 0"
              type="info"
              size="small"
              :disable-transitions="true"
            >
              未开始
            </el-tag>
            <el-tag
              v-else-if="item.status === 1"
              type="danger"
              size="small"
              :disable-transitions="true"
            >
              即将到期
            </el-tag>
            <el-tag
              v-else-if="item.status === 2"
              size="small"
              :disable-transitions="true"
            >
              进行中
            </el-tag>
          </div>
        </div>
        <div v-if="todos.length" class="bottom-tools">
          <div class="bottom-tool" @click="clearTodo">清空待办</div>
          <el-divider direction="vertical" style="margin: 0; width: 0" />
          <router-link to="/user/message?type=todo" class="bottom-tool">
            查看更多
          </router-link>
        </div>
        <el-empty v-else description="已完成所有任务" :image-size="68" />
      </template>
    </ele-tabs>
  </ele-popover>
</template>

<script lang="ts" setup>
  import { ref, nextTick } from 'vue';
  import { storeToRefs } from 'pinia';
  import type { EleTabs } from 'ele-admin-plus';
  import {
    Comment,
    Stamp,
    Promotion,
    Checked,
    BellFilled
  } from '@element-plus/icons-vue';
  import { BellOutlined } from '@/components/icons';
  import { useNoticeStore } from '@/store/modules/notice';

  const noticeStore = useNoticeStore();
  const { notices, letters, todos, unreadNum } = storeToRefs(noticeStore);

  /** 选项卡 */
  const tabRef = ref<InstanceType<typeof EleTabs> | null>(null);

  /** 选项卡选中 */
  const active = ref<string>('notice');

  /** 更新选项卡指示线 */
  const updateActiveBar = () => {
    nextTick(() => {
      tabRef.value?.updateActiveBar?.();
    });
  };

  /** 清空通知 */
  const clearNotice = () => {
    noticeStore.clearNotice();
    updateActiveBar();
  };

  /** 清空私信 */
  const clearLetter = () => {
    noticeStore.clearLetter();
    updateActiveBar();
  };

  /** 清空待办 */
  const clearTodo = () => {
    noticeStore.clearTodo();
    updateActiveBar();
  };

  /** 添加模拟数据 */
  noticeStore.setNotices([
    {
      id: 1,
      color: '#60B2FC',
      icon: 'report',
      title: '你收到了一封14份新周报',
      time: '2020-07-27 18:30:18'
    },
    {
      id: 2,
      color: '#F5686F',
      icon: 'leave',
      title: '许经理同意了你的请假申请',
      time: '2020-07-27 09:08:36'
    },
    {
      id: 3,
      color: '#7CD734',
      icon: 'meeting',
      title: '陈总邀请你参加视频会议',
      time: '2020-07-26 18:30:01'
    },
    {
      id: 4,
      color: '#FAAD14',
      icon: 'interview',
      title: '你推荐的刘诗雨已通过第三轮面试',
      time: '2020-07-25 16:38:46'
    },
    {
      id: 5,
      color: '#2BCACD',
      icon: 'salary',
      title: '你的6月加班奖金已发放',
      time: '2020-07-25 11:03:31'
    }
  ]);
  noticeStore.setLetters([
    {
      id: 1,
      avatar:
        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg',
      title: 'SunSmile 评论了你的日志',
      content: '写的不错, 以后多多向你学习~',
      time: '2020-07-27 18:30:18'
    },
    {
      id: 2,
      avatar:
        'https://cdn.eleadmin.com/20200609/948344a2a77c47a7a7b332fe12ff749a.jpg',
      title: '刘诗雨 点赞了你的日志',
      content: '写的不错, 以后多多向你学习~',
      time: '2020-07-27 09:08:36'
    },
    {
      id: 3,
      avatar:
        'https://cdn.eleadmin.com/20200609/2d98970a51b34b6b859339c96b240dcd.jpg',
      title: '酷酷的大叔 评论了你的周报',
      content: '写的不错, 以后多多向你学习~',
      time: '2020-07-26 18:30:01'
    },
    {
      id: 4,
      avatar:
        'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg',
      title: 'Jasmine 点赞了你的周报',
      content: '写的不错, 以后多多向你学习~',
      time: '2020-07-25 11:03:31'
    }
  ]);
  noticeStore.setTodos([
    {
      id: 1,
      status: 0,
      title: '刘诗雨的请假审批',
      description: '刘诗雨在 07-27 18:30 提交的请假申请'
    },
    {
      id: 2,
      status: 1,
      title: '第三方代码紧急变更',
      description: '需要在 2020-07-27 之前完成'
    },
    {
      id: 3,
      status: 2,
      title: '信息安全考试',
      description: '需要在 2020-07-26 18:30 前完成'
    },
    {
      id: 4,
      status: 2,
      title: 'EleAdmin发布新版本',
      description: '需要在 2020-07-25 11:03 前完成'
    }
  ]);
</script>

<style lang="scss" scoped>
  .list-wrapper {
    padding-top: 8px;
    box-sizing: border-box;
    max-height: calc(100vh - 180px);
    min-height: 60px;
    overflow: auto;
  }

  .list-item {
    display: flex;
    padding: 14px 24px;
    box-sizing: border-box;
    transition: background-color 0.2s;
    cursor: pointer;

    .list-item-body {
      flex: 1;
      overflow: hidden;

      .list-item-text {
        margin-top: 6px;
      }
    }

    .list-item-icon {
      width: 32px;
      height: 32px;
      color: #fff;
      font-size: 16px;
      border-radius: 50%;
      text-align: center;
      background-color: #60b2fc;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    :deep(.el-avatar) {
      flex-shrink: 0;
    }

    .list-item-icon + .list-item-body,
    :deep(.el-avatar + .list-item-body) {
      padding-left: 12px;
    }

    &:hover {
      background-color: hsla(0, 0%, 60%, 0.08);
    }

    & + .list-item {
      border-top: 1px solid hsla(0, 0%, 60%, 0.2);
    }
  }

  /* 操作按钮 */
  .bottom-tools {
    display: flex;
    align-items: center;
    border-top: 1px solid hsla(0, 0%, 60%, 0.2);

    .bottom-tool {
      flex: 1;
      line-height: 46px;
      text-align: center;
      text-decoration: none;
      transition: background-color 0.3s;
      cursor: pointer;
      color: inherit;

      &:hover {
        background: hsla(0, 0%, 60%, 0.08);
      }
    }
  }

  /* 修改标签页样式 */
  .notice-tabs :deep(.el-tabs__header) {
    --ele-tab-height: 44px;
    --ele-tab-padding: 22px;
  }
</style>
