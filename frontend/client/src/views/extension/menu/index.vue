<template>
  <ele-page>
    <ele-card header="垂直菜单">
      <div style="display: flex; flex-wrap: wrap">
        <option-item
          label="暗色主题"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="dark" size="small" />
        </option-item>
        <option-item
          label="彩色图标"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="colorful" size="small" />
        </option-item>
        <option-item
          label="折叠菜单"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="collapse" size="small" />
        </option-item>
      </div>
      <div style="display: flex; flex-wrap: wrap">
        <div style="margin: 0 12px 12px 0">
          <el-button type="primary" class="ele-btn-icon" @click="changeData()">
            一级菜单分组形式
          </el-button>
        </div>
        <div style="margin: 0 12px 12px 0">
          <el-button type="primary" class="ele-btn-icon" @click="changeColor()">
            更改菜单图标颜色
          </el-button>
        </div>
      </div>
      <div style="max-width: 240px">
        <ele-menus
          mode="vertical"
          :items="menuItems"
          :collapse="collapse"
          :collapse-transition="true"
          :default-active="menuActive"
          :theme="dark ? 'dark' : 'light'"
          :colorful="colorful"
          :text-ellipsis-tooltip="true"
        />
      </div>
    </ele-card>
    <ele-card header="水平菜单">
      <div style="display: flex; flex-wrap: wrap">
        <option-item
          label="暗色主题"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="navDark" size="small" />
        </option-item>
        <option-item
          label="彩色图标"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="navColorful" size="small" />
        </option-item>
      </div>
      <div style="display: flex; flex-wrap: wrap">
        <div style="margin: 0 12px 12px 0">
          <el-button
            type="primary"
            class="ele-btn-icon"
            @click="changeColor('nav')"
          >
            更改菜单图标颜色
          </el-button>
        </div>
      </div>
      <div style="max-width: 800px">
        <ele-menus
          mode="horizontal"
          :items="navItems"
          :default-active="navActive"
          :theme="navDark ? 'dark' : 'light'"
          :colorful="navColorful"
          :text-ellipsis-tooltip="true"
        />
      </div>
    </ele-card>
    <ele-card header="紧凑菜单">
      <div style="display: flex; flex-wrap: wrap">
        <option-item
          label="暗色主题"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="boxDark" size="small" />
        </option-item>
        <option-item
          label="彩色图标"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="boxColorful" size="small" />
        </option-item>
        <option-item
          label="隐藏标题"
          :responsive="false"
          style="margin: 0 12px 12px 0"
        >
          <el-switch v-model="boxCollapse" size="small" />
        </option-item>
      </div>
      <div style="display: flex; flex-wrap: wrap">
        <div style="margin: 0 12px 12px 0">
          <el-button
            type="primary"
            class="ele-btn-icon"
            @click="changeData('box')"
          >
            一级菜单分组形式
          </el-button>
        </div>
        <div style="margin: 0 12px 12px 0">
          <el-button
            type="primary"
            class="ele-btn-icon"
            @click="changeColor('box')"
          >
            更改菜单图标颜色
          </el-button>
        </div>
      </div>
      <div
        :style="{
          width: boxCollapse ? '66px' : '88px',
          transition: 'width 0.2s'
        }"
      >
        <ele-menus
          mode="compact"
          :items="boxItems"
          :collapse="boxCollapse"
          :default-active="boxActive"
          :theme="boxDark ? 'dark' : 'light'"
          :colorful="boxColorful"
          :text-ellipsis-tooltip="true"
        />
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, markRaw } from 'vue';
  import type { MenuItem } from 'ele-admin-plus/es/ele-menus/types';
  import {
    SettingOutlined,
    CalendarOutlined,
    LogOutlined,
    LinkOutlined,
    UserOutlined
  } from '@/components/icons';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  defineOptions({ name: 'ExtensionMenu' });

  /** 垂直菜单是否暗色主题 */
  const dark = ref(false);

  /** 垂直菜单是否彩色图标 */
  const colorful = ref(false);

  /** 垂直菜单是否折叠 */
  const collapse = ref(false);

  /** 水平菜单是否暗色主题 */
  const navDark = ref(false);

  /** 水平菜单是否彩色图标 */
  const navColorful = ref(false);

  /** 紧凑菜单是否暗色主题 */
  const boxDark = ref(false);

  /** 紧凑菜单是否彩色图标 */
  const boxColorful = ref(false);

  /** 紧凑菜单是否折叠 */
  const boxCollapse = ref(false);

  /** 垂直菜单选中 */
  const menuActive = ref('1-1');

  /** 水平菜单选中 */
  const navActive = ref('1-1');

  /** 紧凑菜单选中 */
  const boxActive = ref('1-1');

  /** 获取菜单数据 */
  const getMenuData = (): MenuItem[] => {
    return [
      {
        index: '1',
        title: '系统管理',
        icon: markRaw(SettingOutlined),
        children: [
          {
            index: '1-1',
            title: '用户管理'
          },
          {
            index: '1-2',
            title: '角色管理',
            badge: { value: 1 }
          },
          {
            index: '1-3',
            title: '权限管理'
          }
        ]
      },
      {
        index: '2',
        title: '日志管理',
        icon: markRaw(CalendarOutlined),
        badge: { value: 'New', type: 'warning' },
        children: [
          {
            index: '2-1',
            title: '登录日志',
            icon: markRaw(LinkOutlined)
          },
          {
            index: '2-2',
            title: '操作日志如果标题很长很长很长',
            icon: markRaw(LinkOutlined),
            badge: { isDot: true, type: 'success' }
          }
        ]
      },
      {
        index: '3',
        title: '订单管理',
        icon: markRaw(LogOutlined),
        popperClass: 'demo-menu-popper',
        children: [
          {
            index: '3-1',
            title: '订单查询',
            icon: markRaw(LinkOutlined)
          },
          {
            index: '3-2',
            title: '退款记录',
            icon: markRaw(LinkOutlined)
          },
          {
            index: '3-3',
            title: '订单报表',
            icon: markRaw(LinkOutlined),
            children: [
              {
                index: '3-3-1',
                title: '日报表',
                icon: markRaw(LinkOutlined)
              },
              {
                index: '3-3-2',
                title: '周报表',
                icon: markRaw(LinkOutlined),
                disabled: true
              },
              {
                index: '3-3-3',
                title: '月报表',
                icon: markRaw(LinkOutlined)
              },
              {
                index: '3-3-4',
                title: '季度报表',
                group: true,
                children: [
                  {
                    index: '3-3-4-1',
                    title: '一季度',
                    icon: markRaw(LinkOutlined)
                  },
                  {
                    index: '3-3-4-2',
                    title: '二季度',
                    icon: markRaw(LinkOutlined)
                  }
                ]
              }
            ]
          },
          {
            index: '3-4',
            title: '账单统计',
            group: true,
            children: [
              {
                index: '3-4-1',
                title: '销售统计',
                icon: markRaw(LinkOutlined)
              },
              {
                index: '3-4-2',
                title: '退款统计',
                icon: markRaw(LinkOutlined)
              }
            ]
          }
        ]
      },
      {
        index: '4',
        title: '个人中心',
        icon: markRaw(UserOutlined),
        badge: { value: 100 }
      }
    ];
  };

  /** 垂直菜单数据 */
  const menuItems = ref<MenuItem[]>(getMenuData());

  /** 水平菜单数据 */
  const navItems = ref<MenuItem[]>(getMenuData());

  /** 紧凑菜单数据 */
  const boxItems = ref<MenuItem[]>(getMenuData());

  /** 一级菜单改为分组形式 */
  const changeData = (type?: 'box') => {
    const result: MenuItem[] = getMenuData().map((d: MenuItem) => {
      const t: MenuItem = { ...d };
      if (t.children) {
        t.group = true;
        t.icon = void 0;
        if (t.title) {
          t.title = t.title.replace('管理', '');
        }
        t.children = t.children.map((c) => {
          return { ...c, icon: c.icon ?? markRaw(LinkOutlined) };
        });
      }
      return t;
    });
    if (type === 'box') {
      // @ts-ignore
      boxItems.value = result;
      return;
    }
    menuItems.value = result;
  };

  /** 自定义图标背景颜色 */
  const changeColor = (type?: 'box' | 'nav') => {
    const colors: Record<string, string> = {
      '1': 'linear-gradient(-225deg, #231557 0%, #44107A 29%, #FF1361 67%, #FFF800 100%)',
      '2': 'linear-gradient( 135deg, #FFF3B0 10%, #CA26FF 100%)',
      '3': 'linear-gradient(-225deg, #69EACB 0%, #EACCF8 48%, #6654F1 100%)',
      '4': '#faad14',
      '1-1': '#f5222d',
      '1-2': '#fa541c',
      '1-3': '#fa8c16',
      '2-1': '#2f54eb',
      '2-2': '#722ed1',
      '3-1': '#eb2f96',
      '3-2':
        'linear-gradient(135deg, rgb(67, 203, 255) 10%, rgb(151, 8, 204) 100%)',
      '3-3':
        'linear-gradient(135deg, rgb(160, 254, 101) 10%, rgb(250, 1, 109) 100%)',
      '3-4': 'linear-gradient(to right, #f83600 0%, #f9d423 100%)'
    };
    const data =
      type === 'box'
        ? boxItems.value
        : type === 'nav'
          ? navItems.value
          : menuItems.value;
    const result: MenuItem[] = data.map((d: MenuItem) => {
      const t: MenuItem = { ...d };
      if (!t.group) {
        if (t.index && colors[t.index]) {
          if (colors[t.index].startsWith('linear-gradient(')) {
            t.iconProps = { style: { backgroundImage: colors[t.index] } };
          } else {
            t.iconProps = { style: { backgroundColor: colors[t.index] } };
          }
        }
      } else if (t.children) {
        t.children = t.children.map((c) => {
          const m = { ...c };
          if (m.index && colors[m.index]) {
            if (colors[m.index].startsWith('linear-gradient(')) {
              m.iconProps = { style: { backgroundImage: colors[m.index] } };
            } else {
              m.iconProps = { style: { backgroundColor: colors[m.index] } };
            }
          }
          return m;
        });
      }
      return t;
    });
    if (type === 'box') {
      boxItems.value = result;
      return;
    }
    if (type === 'nav') {
      navItems.value = result;
      return;
    }
    menuItems.value = result;
  };
</script>

<style lang="scss">
  .demo-menu-popper.ele-menu > .el-menu--popup-container > .el-menu--popup {
    overflow: visible;

    .el-sub-menu > .el-popper {
      position: absolute !important;
    }
  }
</style>
