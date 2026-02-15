<template>
  <ele-drawer
    :size="430"
    :inner="inner"
    v-model="visible"
    title="限制在抽屉中的消息提示"
  >
    <div>内容内容内容内容内容内容</div>
    <div>内容内容内容内容内容内容</div>
    <div>内容内容内容内容内容内容</div>
    <div>内容内容内容内容内容内容</div>
    <div>内容内容内容内容内容内容</div>
    <div>内容内容内容内容内容内容</div>
    <div style="margin: 16px 0 26px 0">
      <el-button type="primary" class="ele-btn-icon" @click="showMessage">
        显示提示
      </el-button>
    </div>
    <div ref="modalMessageWrapRef" class="ele-message-wrapper"></div>
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </ele-drawer>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useMessage } from 'ele-admin-plus';

  const props = defineProps<{
    theme?: number;
    inner?: boolean;
  }>();

  const visible = defineModel({ type: Boolean });

  const message = useMessage();

  const modalMessageWrapRef = ref<HTMLDivElement>();

  const showMessage = () => {
    message.success({
      message: '这是一条成功的提示',
      plain: props.theme === 1,
      original: props.theme === 3 ? 'plain' : props.theme === 2,
      inner: true,
      showClose: true,
      appendTo: modalMessageWrapRef.value
    });
  };

  const save = () => {
    message.info({
      message: '点击了保存',
      plain: true,
      inner: true,
      appendTo: modalMessageWrapRef.value
    });
  };

  const handleCancel = () => {
    visible.value = false;
  };
</script>
