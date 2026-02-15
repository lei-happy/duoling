<template>
  <ele-card>
    <template #header>
      <span>useModal 函数式操作弹窗</span>
      <el-badge
        value="New"
        style="display: inline-flex; font-weight: normal; margin: -2px 0 0 4px"
      />
    </template>
    <div>
      useModal 可直接传递页面路径纯 js
      方法打开弹窗，并且对上下文、生命周期都做了完美处理。
    </div>
    <div style="margin-top: 12px">
      <el-button class="ele-btn-icon" @click="openDialog">打开弹窗</el-button>
      <el-button class="ele-btn-icon" @click="openDialog2">打开抽屉</el-button>
      <el-button class="ele-btn-icon" @click="openDialog3">
        打开无遮罩层弹窗
      </el-button>
    </div>
    <div style="margin-top: 16px">
      <el-button class="ele-btn-icon" @click="openDialog4">
        传递数据及监听保存成功事件
      </el-button>
    </div>
    <div style="margin-top: 16px">
      <el-button class="ele-btn-icon" @click="openDialog5">
        页面关闭后仍然保持弹窗打开
      </el-button>
    </div>
    <div style="margin-top: 16px">
      <el-button class="ele-btn-icon" @click="openDialog6">
        自定义弹窗的顶栏、底栏
      </el-button>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { useModal, EleMessage } from 'ele-admin-plus';

  const { openModal } = useModal();

  /** 打开弹窗 */
  const openDialog = () => {
    openModal({
      asyncComponent: () => import('./demo-form.vue'),
      props: { title: '添加用户', width: 400, customFooter: true, form: true }
    });
  };

  /** 打开抽屉 */
  const openDialog2 = () => {
    openModal({
      type: 'drawer',
      asyncComponent: () => import('./demo-form.vue'),
      props: { title: '添加用户', size: 400, customFooter: true, form: true }
    });
  };

  /** 打开无遮罩层弹窗 */
  const openDialog3 = () => {
    openModal({
      asyncComponent: () => import('./demo-form.vue'),
      props: { title: '添加用户', width: 400, multiple: true }
    });
  };

  /** 传递数据及监听保存成功事件 */
  const openDialog4 = () => {
    const row = {
      nickname: '管理员',
      sex: '男',
      phone: '12345678901',
      email: 'admin@eleadmin.com',
      introduction: '这家伙很懒，什么都不说~'
    };
    openModal({
      asyncComponent: () => import('./demo-form.vue'),
      props: { title: '修改用户', width: 400, multiple: true },
      componentProps: {
        data: row,
        onDone: () => {
          EleMessage.success({ message: '监听到保存成功事件', plain: true });
        }
      }
    });
  };

  /** 页面关闭后仍然保持弹窗打开 */
  const openDialog5 = () => {
    openModal({
      asyncComponent: () => import('./demo-form.vue'),
      props: { title: '添加用户', width: 400, multiple: true },
      keepAlive: true
    });
  };

  /** 自定义弹窗的顶栏、底栏 */
  const openDialog6 = () => {
    const row = {
      nickname: '管理员',
      sex: '男',
      phone: '12345678901',
      email: 'admin@eleadmin.com',
      introduction: '这家伙很懒，什么都不说~'
    };
    openModal({
      custom: true,
      asyncComponent: () => import('./demo-form-modal.vue'),
      asyncComponentOptions: { delay: 0 },
      props: { maxable: true },
      componentProps: {
        data: row,
        onDone: () => {
          EleMessage.success({ message: '监听到保存成功事件', plain: true });
        }
      }
    });
  };
</script>
