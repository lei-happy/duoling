<template>
  <ele-card header="Popover、PopConfirm、Dropdown">
    <div>
      <el-space wrap style="margin-bottom: 20px">
        <ele-popover
          :width="180"
          trigger="click"
          title="这是标题"
          :offset="8"
          :popper-options="{ strategy: 'fixed' }"
        >
          <template #reference>
            <el-button class="ele-btn-icon">Popover</el-button>
          </template>
          <div>This is content.</div>
          <div>This is content.</div>
        </ele-popover>
        <ele-popconfirm
          :width="190"
          :offset="8"
          title="确定要删除此用户吗?"
          :popper-options="{ strategy: 'fixed' }"
          @confirm="handleConfirm"
        >
          <template #reference>
            <el-button class="ele-btn-icon">PopConfirm</el-button>
          </template>
        </ele-popconfirm>
        <ele-popconfirm
          :width="258"
          :offset="8"
          title="用户满意度调研"
          content="您在使用中是否对本产品还满意?"
          cancel-button-text="关闭"
          confirm-button-text="满意"
          :cancel-button-props="{ style: { order: -1, margin: '0 auto 0 0' } }"
          :popper-options="{ strategy: 'fixed' }"
          @confirm="handleAgree"
        >
          <template #reference>
            <el-button class="ele-btn-icon">PopConfirm 自定义按钮</el-button>
          </template>
          <template #action="{ cancel }">
            <el-button
              plain
              size="small"
              type="danger"
              @click="handleComplain(cancel)"
            >
              投诉
            </el-button>
          </template>
        </ele-popconfirm>
      </el-space>
    </div>
    <div>
      <el-space wrap>
        <ele-dropdown
          :items="[
            { title: '重置密码', command: 'password', icon: LockOutlined },
            { title: '修改用户', command: 'edit', icon: EditOutlined },
            {
              title: '删除用户',
              command: 'delete',
              icon: DeleteOutlined,
              divided: true,
              danger: true
            }
          ]"
          component-type="pro"
          :icon-props="{ size: 14 }"
          :popper-options="{ strategy: 'fixed' }"
          trigger="click"
          @command="handleCommand"
        >
          <el-button class="ele-btn-icon">
            <span>Dropdown</span>
            <el-icon style="margin: 0 -4px 0 4px">
              <ArrowDown />
            </el-icon>
          </el-button>
        </ele-dropdown>
        <ele-dropdown
          :items="items"
          component-type="pro"
          :icon-props="{ size: 14 }"
          :popper-options="{ strategy: 'fixed' }"
          trigger="click"
          @command="handleCommand"
        >
          <el-button class="ele-btn-icon">
            <span>Dropdown 多级菜单</span>
            <el-icon style="margin: 0 -4px 0 4px">
              <ArrowDown />
            </el-icon>
          </el-button>
        </ele-dropdown>
        <ele-dropdown
          :items="items"
          component-type="pro"
          :icon-props="{ size: 14 }"
          :popper-options="{ strategy: 'fixed' }"
          trigger="click"
          :split-button="true"
          :split-button-props="{ class: 'ele-btn-icon' }"
          @command="handleCommand"
          @click="handleClick"
        >
          <span>按钮组</span>
        </ele-dropdown>
      </el-space>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, markRaw } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    ArrowDown,
    LockOutlined,
    EditOutlined,
    DeleteOutlined,
    DesktopOutlined,
    SettingOutlined,
    UserOutlined,
    IdcardOutlined,
    ControlOutlined,
    TableOutlined,
    ApplicationOutlined,
    AppstoreOutlined,
    LinkOutlined,
    MessageOutlined
  } from '@/components/icons';

  const items = ref([
    { title: '工作台', command: 'workplace', icon: markRaw(DesktopOutlined) },
    { title: '个人中心', command: 'profile', icon: markRaw(UserOutlined) },
    {
      title: '系统管理',
      command: 'system',
      icon: markRaw(SettingOutlined),
      children: [
        {
          title: '用户管理',
          command: 'system/user',
          icon: markRaw(UserOutlined)
        },
        {
          title: '角色管理',
          command: 'system/role',
          icon: markRaw(IdcardOutlined)
        },
        {
          title: '权限管理',
          command: 'system/menu',
          icon: markRaw(ControlOutlined)
        }
      ]
    },
    {
      title: '列表页面',
      command: 'list',
      icon: markRaw(TableOutlined),
      children: [
        {
          title: '基础列表',
          command: 'list/basic',
          icon: markRaw(TableOutlined)
        },
        {
          title: '复杂列表',
          command: 'list/basic',
          icon: markRaw(ApplicationOutlined)
        },
        {
          title: '卡片列表',
          command: 'list/card',
          icon: markRaw(AppstoreOutlined),
          children: [
            {
              title: '项目列表',
              command: 'list/card/project',
              icon: markRaw(LinkOutlined)
            },
            {
              title: '应用列表',
              command: 'list/card/application',
              icon: markRaw(LinkOutlined)
            },
            {
              title: '文章列表',
              command: 'list/card/article',
              icon: markRaw(LinkOutlined)
            }
          ]
        }
      ],
      divided: true
    },
    {
      title: '消息中心',
      command: 'message',
      icon: markRaw(MessageOutlined)
    }
  ]);

  const handleCommand = (command: string) => {
    EleMessage.info({ message: `点击了: ${command}`, plain: true });
  };

  const handleClick = () => {
    EleMessage.info({ message: '点击了按钮组', plain: true });
  };

  const handleConfirm = () => {
    EleMessage.info({ message: '点击了确定', plain: true });
  };

  const handleAgree = () => {
    EleMessage.info({ message: '点击了满意', plain: true });
  };

  const handleComplain = (cancel: any) => {
    cancel && cancel();
    EleMessage.info({ message: '点击了投诉', plain: true });
  };
</script>
