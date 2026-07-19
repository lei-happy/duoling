<!-- 顶栏意见反馈入口：快捷提交弹窗 -->
<template>
  <div
    style="display: flex; align-items: center; height: 100%"
    title="意见反馈"
    @click="dialogVisible = true"
  >
    <el-icon style="transform: scale(1.12)">
      <ChatDotRound />
    </el-icon>
  </div>

  <feedback-submit-dialog
    v-model="dialogVisible"
    show-my-link
    @view-list="goMyFeedback"
  />
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { ChatDotRound } from '@element-plus/icons-vue';
  import FeedbackSubmitDialog from '@/views/user/feedback/components/feedback-submit-dialog.vue';

  defineOptions({ name: 'HeaderFeedback' });

  const { push } = useRouter();
  const dialogVisible = ref(false);

  const goMyFeedback = () => {
    dialogVisible.value = false;
    push('/user/feedback');
  };
</script>
