export const zh_CN = {
  layout: {
    home: '主页',
    header: {
      enterprise: '企业管理',
      profile: '个人中心',
      password: '修改密码',
      logout: '退出登录'
    },
    footer: {
      website: '官网',
      document: '帮助手册',
      authorization: '',
      copyright: 'Copyright © 2026 北京智途科技有限公司'
    },
    logout: {
      title: '系统提示',
      message: '确定要退出登录吗?'
    },
    tabs: {
      reload: '重新加载',
      close: '关闭标签页',
      closeLeft: '关闭左侧标签页',
      closeRight: '关闭右侧标签页',
      closeOther: '关闭其它标签页',
      closeAll: '关闭全部标签页',
      fullscreen: '全屏内容区域',
      fullscreenExit: '退出内容全屏',
      maximized: '全屏主体区域',
      maximizedExit: '退出主体全屏',
      blank: '在新窗口中打开',
      pin: '固定',
      unpin: '取消固定'
    },
    setting: {
      title: '主题风格设置',
      sideStyles: {
        dark: '暗色侧栏',
        light: '亮色侧栏'
      },
      headStyles: {
        light: '亮色顶栏',
        dark: '暗色顶栏',
        primary: '主色顶栏'
      },
      layoutStyles: {
        side: '左侧菜单',
        top: '顶部菜单',
        mix: '混合菜单'
      },
      colors: {
        default: '拂晓蓝',
        dust: '薄暮',
        sunset: '日暮',
        volcano: '火山',
        purple: '酱紫',
        green: '极光绿',
        geekblue: '极客蓝'
      },
      darkMode: '开启暗黑模式',
      roundedTheme: '开启圆角主题',
      layout: '导航模式',
      sidebarLayout: '侧栏双排菜单',
      mixSidebarStyle: '暗色二级侧栏',
      fluid: '内容区域铺满',
      other: '其它配置',
      more: '更多配置',
      tab: '页签配置',
      fixedHeader: '固定顶栏区域',
      fixedSidebar: '固定侧栏区域',
      fixedBody: '内容区域滚动',
      logoInHeader: 'Logo置于顶栏',
      colorfulIcon: '侧栏彩色图标',
      uniqueOpened: '侧栏排它展开',
      responsive: '移动端响应式',
      weakMode: '开启色弱模式',
      showTabs: '开启多页签栏',
      fixedHome: '固定主页页签',
      tabInHeader: '页签置于顶栏',
      tabStyle: '页签显示风格',
      tabStyles: {
        default: '默认',
        dot: '圆点',
        tag: '标签',
        card: '卡片'
      },
      tabIcon: '页签显示图标',
      tabsCache: '刷新保留页签',
      menuItemTrigger: '混合菜单分割',
      footer: '开启全局页脚',
      pageKeepAlive: '页面切换缓存',
      transitionName: '路由切换动画',
      transitions: {
        slideRight: '滑动消退',
        slideBottom: '底部消退',
        zoomIn: '放大渐变',
        zoomOut: '缩小渐变',
        fade: '淡入淡出',
        none: '无'
      },
      reset: '重置',
      tabs: {
        theme: '主题设置',
        layout: '常用布局',
        skin: '皮肤背景'
      },
      skins: {
        classics: '经典主题',
        custom: '自定义',
        gradient: '彩色渐变',
        technology: '蓝色科技',
        aesthetic: '唯美意境',
        cartoon: '可爱卡通',
        simple: '清新主题',
        modern: '现代主题'
      },
      skinConfig: {
        wallpaper: '页面背景图片',
        maskColor: '页面背景蒙层',
        headerBg: '顶栏背景颜色',
        sidebarBg: '侧栏背景颜色',
        cardBg: '卡片背景颜色',
        overlayBg: '弹框背景图片',
        overlayMaskColor: '弹框背景蒙层',
        darkConfig: '暗黑模式'
      },
      layouts: {
        default: '常规布局',
        mixedSidebar: '双侧栏布局',
        compactSidebar: '紧凑侧栏布局',
        tabInHeader: '页签位于顶栏',
        cardSidebar: '卡片侧栏布局',
        cardMixedSidebar: '卡片双侧栏',
        cardLayout: '卡片风格布局',
        verticalLayout: '上下布局',
        topBarLayout: '顶栏布局',
        limitedWidth: '内容固定宽度',
        compactMixSidebar: '紧凑双侧栏',
        compactLayout: '紧凑布局',
        colorfulSidebar: '侧栏彩色图标',
        cardTabStyle: '页签卡片风格',
        rowLayout: '左右布局',
        rowMixedSidebar: '左右双侧栏',
        rowCompactHeader: '左右紧凑顶栏'
      }
    }
  },
  login: {
    title: '用户登录',
    username: '请输入登录账号',
    password: '请输入登录密码',
    code: '请输入验证码',
    remember: '记住密码',
    login: '登录',
    passwordType: '密码登录',
    qrcodeType: '扫码登录',
    refreshQrcode: '刷新二维码'
  },
  list: {
    // 基础列表
    basic: {
      table: {
        avatar: '头像',
        username: '用户账号',
        nickname: '用户名',
        organizationName: '组织机构',
        phone: '手机号',
        email: '邮箱',
        roles: '角色',
        sexName: '性别',
        createTime: '创建时间',
        status: '状态',
        action: '操作'
      }
    }
  }
};

export type Locale = typeof zh_CN;
