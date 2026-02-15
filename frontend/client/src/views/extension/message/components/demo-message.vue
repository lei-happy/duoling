<template>
  <ele-card header="消息提示">
    <option-item label="风格">
      <el-radio-group v-model="theme">
        <el-radio :value="0" label="默认" />
        <el-radio :value="1" label="简约" />
        <el-radio :value="2" label="多彩" />
        <el-radio :value="3" label="多彩简约" />
      </el-radio-group>
    </option-item>
    <option-item label="限制在主体区域" style="margin-top: 16px">
      <el-switch v-model="inner" size="small" />
    </option-item>
    <option-item label="类型">
      <el-button @click="showMessage('success')">成功</el-button>
      <el-button @click="showMessage('warning')">警告</el-button>
      <el-button @click="showMessage('error')">错误</el-button>
      <el-button @click="showMessage('info')">信息</el-button>
    </option-item>
    <option-item label="加载">
      <el-button @click="showLoading()">打开</el-button>
      <el-button @click="showLoading(true)">带遮罩层</el-button>
      <el-button @click="showLoading(true, true)">居中显示</el-button>
    </option-item>
    <option-item label="响应式">
      <el-button @click="showReactiveLoading">打开加载框</el-button>
    </option-item>
    <option-item label="合并相同内容">
      <el-button @click="showGroup('success', '内容一')" class="ele-btn-icon">
        内容一
      </el-button>
      <el-button @click="showGroup('success', '内容二')" class="ele-btn-icon">
        内容二
      </el-button>
      <el-button @click="showGroup('warning', '内容一')">警告</el-button>
      <el-button @click="showGroup('error', '内容一')">错误</el-button>
    </option-item>
    <option-item label="限制在指定区域">
      <el-button @click="showInDemoWrap" class="ele-btn-icon">提示</el-button>
      <el-button @click="openModal" class="ele-btn-icon">
        限制在指定弹窗
      </el-button>
    </option-item>
    <div
      :style="{
        maxWidth: '600px',
        height: '280px',
        border: '1px solid var(--el-border-color)',
        position: 'relative',
        marginTop: '16px'
      }"
    >
      <div style="text-align: center; padding: 20px">
        <div>内容内容内容内容内容内容</div>
        <div>内容内容内容内容内容内容</div>
        <div>内容内容内容内容内容内容</div>
        <div>内容内容内容内容内容内容</div>
        <div>内容内容内容内容内容内容</div>
        <div>内容内容内容内容内容内容</div>
      </div>
      <div ref="demoMessageWrapRef" class="ele-message-wrapper"></div>
    </div>
    <demo-message-modal v-model="modalVisible" :theme="theme" :inner="inner" />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useMessage, useMessageBox, random } from 'ele-admin-plus';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';
  import DemoMessageModal from './demo-message-modal.vue';

  const message = useMessage();
  const messageBox = useMessageBox();

  /** 主题风格 */
  const theme = ref(1);

  /** 限制在主体区域 */
  const inner = ref(false);

  /** 打开消息 */
  const showMessage = (type: 'success' | 'warning' | 'error' | 'info') => {
    const messages = {
      success: '这是一条成功的提示',
      warning: '这是一条警告的提示',
      error: '这是一条错误的提示',
      info: '这是一条普通的提示'
    };
    message({
      type,
      message: messages[type],
      plain: theme.value === 1,
      original: theme.value === 3 ? 'plain' : theme.value === 2,
      inner: inner.value,
      showClose: true
    });
  };

  /** 打开加载提示 */
  const showLoading = (mask?: boolean, centered?: boolean) => {
    const loading = message.loading({
      message: '正在加载中..',
      plain: theme.value === 1,
      original: theme.value === 3 ? 'plain' : theme.value === 2,
      inner: inner.value,
      showClose: true,
      mask,
      centered
    });
    setTimeout(() => {
      loading.close();
    }, 3000);
  };

  /** 导入进度 */
  const progress = ref(0);

  /** 打开响应式加载框 */
  const showReactiveLoading = () => {
    progress.value = 0;
    const loading = message.loading({
      message: () =>
        `正在导入用户......${String(progress.value).padStart(2, '0')}%` as any,
      plain: true,
      inner: inner.value,
      mask: true,
      centered: true
    });
    const timer = setInterval(() => {
      const num = progress.value + random(0, 5);
      progress.value = num > 100 ? 100 : num;
      if (progress.value == 100) {
        loading.close();
        clearInterval(timer);
        messageBox
          .alert(
            '导入完成，共新增 80 条数据，更新 20 条数据，失败 0 条数据。',
            '导入成功',
            {
              type: 'success',
              confirmButtonText: '完成',
              inner: inner.value,
              draggable: true
            }
          )
          .then(() => {
            console.log('点击了完成');
          })
          .catch(() => {});
      }
    }, 100);
  };

  /** 合并相同内容 */
  const showGroup = (
    type: 'success' | 'warning' | 'error' | 'info',
    msg: string
  ) => {
    message({
      type,
      message: msg,
      plain: theme.value === 1,
      original: theme.value === 3 ? 'plain' : theme.value === 2,
      inner: inner.value,
      showClose: true,
      grouping: true
    });
  };

  /** 限制在指定区域 */
  const demoMessageWrapRef = ref<HTMLDivElement>();

  const showInDemoWrap = () => {
    message.success({
      message: '这是一条成功的提示',
      plain: theme.value === 1,
      original: theme.value === 3 ? 'plain' : theme.value === 2,
      inner: true,
      showClose: true,
      appendTo: demoMessageWrapRef.value
    });
  };

  /** 限制在指定弹窗 */
  const modalVisible = ref(false);

  const openModal = () => {
    modalVisible.value = true;
  };
</script>
