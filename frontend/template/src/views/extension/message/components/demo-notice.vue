<template>
  <ele-card header="消息通知">
    <option-item label="使用">
      <el-button @click="showNotification()" class="ele-btn-icon">
        打开通知
      </el-button>
      <el-button @click="showNotification('success')" class="ele-btn-icon">
        带图标
      </el-button>
      <el-button @click="showNotification('info', 0)" class="ele-btn-icon">
        不自动关闭
      </el-button>
    </option-item>
    <option-item label="类型">
      <el-button @click="showNotification('success')">成功</el-button>
      <el-button @click="showNotification('warning')">警告</el-button>
      <el-button @click="showNotification('error')">错误</el-button>
      <el-button @click="showNotification('info')">信息</el-button>
    </option-item>
    <option-item label="位置">
      <el-button
        @click="showNotification('info', null, 'top-left')"
        class="ele-btn-icon"
      >
        TopLeft
      </el-button>
      <el-button
        @click="showNotification('info', null, 'bottom-left')"
        class="ele-btn-icon"
      >
        BottomLeft
      </el-button>
      <el-button
        @click="showNotification('info', null, 'bottom-right')"
        class="ele-btn-icon"
      >
        BottomRight
      </el-button>
    </option-item>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ElNotification } from 'element-plus';
  import type { NotificationProps } from 'element-plus';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  /** 打开消息通知 */
  const showNotification = (
    type?: NotificationProps['type'] | null,
    duration?: number | null,
    position?: NotificationProps['position'] | null
  ) => {
    ElNotification({
      title: 'Notification Title',
      message:
        'This is the content of the notification. This is the content of the notification. ',
      type: type || '',
      duration: duration ?? 4500,
      position: position || 'top-right'
    });
  };
</script>
