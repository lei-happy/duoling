import type { Locale } from './zh_CN';

export const zh_TW: Locale = {
  layout: {
    home: '主頁',
    header: {
      profile: '個人中心',
      password: '修改密碼',
      logout: '安全登出'
    },
    footer: {
      website: '官網',
      document: '檔案',
      authorization: '授權',
      copyright: 'Copyright © 2025 武漢易雲智科技有限公司'
    },
    logout: {
      title: '詢問',
      message: '確定要登出嗎?'
    },
    tabs: {
      reload: '重新載入',
      close: '關閉標籤頁',
      closeLeft: '關閉左側標籤頁',
      closeRight: '關閉右側標籤頁',
      closeOther: '關閉其它標籤頁',
      closeAll: '關閉全部標籤頁',
      fullscreen: '全屏內容區域',
      fullscreenExit: '退出內容全屏',
      maximized: '全屏主體區域',
      maximizedExit: '退出主體全屏',
      blank: '在新視窗中打開',
      pin: '固定',
      unpin: '取消固定'
    },
    setting: {
      title: '主題風格設定',
      sideStyles: {
        dark: '暗色側欄',
        light: '亮色側欄'
      },
      headStyles: {
        light: '亮色頂欄',
        dark: '暗色頂欄',
        primary: '主色頂欄'
      },
      layoutStyles: {
        side: '左側選單佈局',
        top: '頂部選單佈局',
        mix: '混合選單佈局'
      },
      colors: {
        default: '拂曉藍',
        dust: '薄暮',
        sunset: '日暮',
        volcano: '火山',
        purple: '醬紫',
        green: '極光綠',
        geekblue: '極客藍'
      },
      darkMode: '開啟暗黑模式',
      roundedTheme: '開啟圓角主題',
      layout: '導航模式',
      sidebarLayout: '側欄雙排選單',
      mixSidebarStyle: '暗色二級側欄',
      fluid: '內容區域鋪滿',
      other: '其它配寘',
      more: '更多配寘',
      tab: '頁簽配寘',
      fixedHeader: '固定頂欄區域',
      fixedSidebar: '固定側欄區域',
      fixedBody: '內容區域滾動',
      logoInHeader: 'Logo置於頂欄',
      colorfulIcon: '側欄彩色圖標',
      uniqueOpened: '側欄排它展開',
      responsive: '移動端響應式',
      weakMode: '開啟色弱模式',
      showTabs: '開啟多頁簽欄',
      fixedHome: '固定主頁頁簽',
      tabInHeader: '頁簽置於頂欄',
      tabStyle: '頁簽顯示風格',
      tabStyles: {
        default: '默認',
        dot: '圓點',
        tag: '标签',
        card: '卡片'
      },
      tabIcon: '頁籤顯示圖標',
      tabsCache: '刷新保留頁籤',
      menuItemTrigger: '混合菜單分割',
      footer: '開啟全局頁腳',
      pageKeepAlive: '頁面切換緩存',
      transitionName: '路由切換動畫',
      transitions: {
        slideRight: '滑動消退',
        slideBottom: '底部消退',
        zoomIn: '放大漸變',
        zoomOut: '縮小漸變',
        fade: '淡入淡出',
        none: '無'
      },
      reset: '重置',
      tabs: {
        theme: '主題設定',
        layout: '常用佈局',
        skin: '皮膚背景'
      },
      skins: {
        classics: '經典主題',
        custom: '自定義',
        gradient: '彩色漸變',
        technology: '藍色科技',
        aesthetic: '唯美意境',
        cartoon: '可愛卡通',
        simple: '清新主題',
        modern: '現代主題'
      },
      skinConfig: {
        wallpaper: '頁面背景圖片',
        maskColor: '頁面背景蒙層',
        headerBg: '頂欄背景顏色',
        sidebarBg: '側欄背景顏色',
        cardBg: '卡片背景顏色',
        overlayBg: '彈框背景圖片',
        overlayMaskColor: '彈框背景蒙層',
        darkConfig: '暗黑模式'
      },
      layouts: {
        default: '常規佈局',
        mixedSidebar: '雙側欄佈局',
        compactSidebar: '緊湊側欄佈局',
        tabInHeader: '頁籤位於頂欄',
        cardSidebar: '卡片側欄佈局',
        cardMixedSidebar: '卡片雙側欄',
        cardLayout: '卡片風格佈局',
        verticalLayout: '上下佈局',
        topBarLayout: '頂欄佈局',
        limitedWidth: '內容固定寬度',
        compactMixSidebar: '緊湊雙側欄',
        compactLayout: '緊湊佈局',
        colorfulSidebar: '側欄彩色圖標',
        cardTabStyle: '頁籤卡片風格',
        rowLayout: '左右佈局',
        rowMixedSidebar: '左右雙側欄',
        rowCompactHeader: '左右緊湊頂欄'
      }
    }
  },
  login: {
    title: '用戶登錄',
    username: '請輸入登入帳號',
    password: '請輸入登入密碼',
    code: '請輸入驗證碼',
    remember: '記住密碼',
    login: '登入',
    passwordType: '密碼登入',
    qrcodeType: '掃碼登入',
    refreshQrcode: '重繪二維碼'
  },
  list: {
    // 基础列表
    basic: {
      table: {
        avatar: '頭像',
        username: '用戶賬號',
        nickname: '用戶名',
        organizationName: '組織機構',
        phone: '手機號',
        email: '郵箱',
        roles: '角色',
        sexName: '性別',
        createTime: '創建時間',
        status: '狀態',
        action: '操作'
      }
    }
  }
};
