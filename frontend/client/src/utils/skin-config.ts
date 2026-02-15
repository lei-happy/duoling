import type {
  PredefinedLayout,
  SkinConfig
} from 'ele-admin-plus/es/utils/theme-util';
import wallpaper01 from '@/assets/wallpaper-01.jpg';
import wallpaper01Cover from '@/assets/wallpaper-01-cover.jpg';
import wallpaper01Dark from '@/assets/wallpaper-01-dark.jpg';
import wallpaper01DarkCover from '@/assets/wallpaper-01-dark-cover.jpg';
import wallpaper02 from '@/assets/wallpaper-02.jpg';
import wallpaper02Cover from '@/assets/wallpaper-02-cover.jpg';
import wallpaper02Dark from '@/assets/wallpaper-02-dark.jpg';
import wallpaper02DarkCover from '@/assets/wallpaper-02-dark-cover.jpg';
import wallpaper03 from '@/assets/wallpaper-03.jpg';
import wallpaper03Cover from '@/assets/wallpaper-03-cover.jpg';
import wallpaper04 from '@/assets/wallpaper-04.jpg';
import wallpaper04Cover from '@/assets/wallpaper-04-cover.jpg';

/**
 * 预设常用布局
 */
export const PREDEFINED_LAYOUTS: PredefinedLayout[] = [
  {
    name: 'default',
    cover: 'CoverDefault',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'default',
      headerStyle: 'light',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'mixedSidebar',
    cover: 'CoverMixedSidebar',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'mix',
      headerStyle: 'light',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'compactMixSidebar',
    cover: 'CoverCompactMixSidebar',
    config: {
      collapse: false,
      compact: true,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'mix',
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'compactSidebar',
    cover: 'CoverCompactSidebar',
    config: {
      collapse: true,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'mix',
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'colorfulSidebar',
    cover: 'CoverColorfulSidebar',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: true,
      layout: 'default',
      sidebarLayout: 'default',
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'tabInHeader',
    cover: 'CoverTabInHeader',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'default',
      headerStyle: 'primary',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: true,
      tabInHeader: true,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: {
        '--el-bg-color': 'var(--ele-layout-bg)'
      },
      contentCustomStyle: null,
      layoutCustomStyle: {
        '--ele-header-height': '46px',
        '--ele-header-primary-bg': 'var(--el-color-primary)'
      },
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      headerStyle: 'light'
    }
  },
  {
    name: 'cardLayout',
    cover: 'CoverCardLayout',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'mix',
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'light',
      tabStyle: 'simple',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: true,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: {
        margin: '16px 0 16px 16px',
        borderRadius: '8px'
      },
      sideboxCustomStyle: {
        margin: '16px 0 16px 16px',
        borderRadius: '8px'
      },
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: {
        '--ele-header-height': '46px',
        '--ele-header-primary-bg': 'var(--el-color-primary)'
      },
      layoutCustomClass: 'layout-card-style'
    },
    traditionalThemeConfig: {
      headerStyle: 'dark'
    }
  },
  {
    name: 'cardSidebar',
    cover: 'CoverCardSidebar',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'default',
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      fixedBody: true,
      fluid: true,
      logoInHeader: true,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: {
        margin: '16px 0 16px 16px',
        borderRadius: '8px'
      },
      sideboxCustomStyle: {
        margin: '16px 0 16px 16px',
        borderRadius: '8px'
      },
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: 'layout-card-style'
    }
  },
  {
    name: 'cardMixedSidebar',
    cover: 'CoverCardMixedSidebar',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'mix',
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      fixedBody: true,
      fluid: true,
      logoInHeader: false,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: {
        padding: '16px 0 16px 0',
        clipPath: 'inset(14px 0 14px 0 round 0 12px 12px 0)',
        '--ele-sidebar-bg': 'none'
      },
      sideboxCustomStyle: {
        padding: '16px 0 16px 14px',
        clipPath: 'inset(14px 0 14px 14px round 12px 0 0 12px)',
        '--ele-sidebar-bg': 'none'
      },
      sideCustomStyle: {
        clipPath: 'inset(14px 0px 14px 14px round 14px 12px 12px 14px)',
        borderRadius: '24px',
        boxShadow:
          'inset 7px 0px 0px 8px var(--el-border-color-extra-light), inset 8px 10px 0px 5px var(--el-border-color-extra-light), inset 8px -10px 0px 5px var(--el-border-color-extra-light)',
        background: 'var(--ele-sidebar-bg)'
      },
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: {
        '--ele-sidebox-width': '96px',
        '--ele-sidebar-collapse-width': '70px',
        '--ele-header-height': '46px'
      },
      layoutCustomClass: 'layout-card-style layout-mix-card-style'
    }
  },
  {
    name: 'verticalLayout',
    cover: 'CoverVerticalLayout',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'default',
      sidebarLayout: 'default',
      headerStyle: 'primary',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'tag',
      fixedBody: true,
      fluid: true,
      logoInHeader: true,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'topBarLayout',
    cover: 'CoverTopBarLayout',
    config: {
      collapse: false,
      compact: false,
      tabBar: true,
      colorfulIcon: false,
      layout: 'top',
      sidebarLayout: 'default',
      headerStyle: 'dark',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      fixedBody: true,
      fluid: true,
      logoInHeader: true,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: {
        '--ele-header-primary-bg': 'var(--el-color-primary)'
      },
      layoutCustomClass: null
    }
  },
  {
    name: 'limitedWidth',
    cover: 'CoverLimitedWidth',
    config: {
      collapse: false,
      compact: false,
      tabBar: false,
      colorfulIcon: false,
      layout: 'top',
      sidebarLayout: 'default',
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      fixedBody: true,
      fluid: false,
      logoInHeader: true,
      tabInHeader: false,
      sidebarMenuProps: null,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  }
];

/**
 * 简约主题的预设常用布局
 */
export const SIMPLE_LAYOUTS: PredefinedLayout[] = [
  {
    name: 'default',
    cover: 'CoverDefault',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'mixedSidebar',
    cover: 'CoverMixedSidebar',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: true,
      logoInHeader: false,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'compactMixSidebar',
    cover: 'CoverCompactMixSidebar',
    config: {
      collapse: false,
      compact: true,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: false,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'compactSidebar',
    cover: 'CoverCompactSidebar',
    config: {
      collapse: true,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: false,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'tabInHeader',
    cover: 'CoverTabInHeader',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'compactLayout',
    cover: 'CoverCompactLayout',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'colorfulSidebar',
    cover: 'CoverColorfulSidebar',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: true,
      logoInHeader: true,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'topBarLayout',
    cover: 'CoverTopBarLayout',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: 'button',
      layout: 'top',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sideboxMenuProps: null,
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  }
];

/**
 * 现代主题的预设常用布局
 */
export const MODERN_LAYOUTS: PredefinedLayout[] = [
  {
    name: 'default',
    cover: 'CoverModernDefault',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'simple',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  },
  {
    name: 'mixedSidebar',
    cover: 'CoverModernMixedSidebar',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'simple',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  },
  {
    name: 'compactMixSidebar',
    cover: 'CoverModernCompactMixed',
    config: {
      collapse: false,
      compact: true,
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'simple',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  },
  {
    name: 'compactSidebar',
    cover: 'CoverModernCompactSidebar',
    config: {
      collapse: true,
      compact: false,
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'simple',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  },
  {
    name: 'cardTabStyle',
    cover: 'CoverModernCardTab',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: true,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    }
  },
  {
    name: 'rowLayout',
    cover: 'CoverModernRow',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: false,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  },
  {
    name: 'rowMixedSidebar',
    cover: 'CoverModernRowMixed',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'light',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'button',
      layout: 'default',
      sidebarLayout: 'mix',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: false,
      tabInHeader: false,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  },
  {
    name: 'rowCompactHeader',
    cover: 'CoverModernRowHeader',
    config: {
      collapse: false,
      compact: false,
      headerStyle: 'primary',
      sidebarStyle: 'dark',
      mixSidebarStyle: 'dark',
      tabStyle: 'simple',
      layout: 'default',
      sidebarLayout: 'default',
      tabBar: true,
      colorfulIcon: false,
      logoInHeader: false,
      tabInHeader: true,
      fixedBody: true,
      fluid: true,
      sidebarMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sideboxMenuProps: { popupTheme: 'light', popperEffect: 'light' },
      sidebarCustomStyle: null,
      sideboxCustomStyle: null,
      sideCustomStyle: null,
      headerCustomStyle: null,
      tabsCustomStyle: null,
      contentCustomStyle: null,
      layoutCustomStyle: null,
      layoutCustomClass: null
    },
    traditionalThemeConfig: {
      tabStyle: 'button'
    }
  }
];

/**
 * 皮肤背景的预设常用布局
 */
export const SKIN_LAYOUTS: PredefinedLayout[] = PREDEFINED_LAYOUTS.map(
  (item) => ({
    ...item,
    config: {
      ...item.config,
      headerStyle: 'light',
      sidebarStyle: 'light',
      mixSidebarStyle: 'light',
      tabStyle: item.name === 'cardLayout' ? 'tag' : item.config.tabStyle
    }
  })
);

/**
 * 预设皮肤背景
 */
export const PREDEFINED_SKINS: SkinConfig[] = [
  {
    name: 'simple',
    color: '#2f54eb',
    cover: 'CoverSimple',
    themeClass: 'ele-theme-simple',
    darkConfig: {
      color: '#2f54eb',
      cover: 'CoverSimpleDark',
      themeClass: 'ele-theme-simple-dark'
    },
    layouts: SIMPLE_LAYOUTS
  },
  {
    name: 'modern',
    color: '#5f80c7',
    cover: 'CoverModernDefault',
    themeClass: 'ele-theme-modern',
    darkConfig: {
      color: '#5f80c7',
      cover: 'CoverModernDefault',
      themeClass: 'ele-theme-modern-dark'
    },
    layouts: MODERN_LAYOUTS
  },
  {
    name: 'gradient',
    color: '#1677ff',
    cover: `url(${wallpaper01Cover}) center / 100% 100%`,
    wallpaper: `url(${wallpaper01}) center / 100% 100%`,
    maskColor: 'rgba(222, 242, 249, 0.4)',
    headerBg: 'rgba(255, 255, 255, 0.4)',
    sidebarBg: 'rgba(255, 255, 255, 0.4)',
    cardBg: 'rgba(255, 255, 255, 0.88)',
    overlayBg: `url(${wallpaper01}) center / 100% 100%`,
    overlayMaskColor:
      'linear-gradient(90deg, rgba(255, 255, 255, 0.8), rgba(0, 0, 0, 0), rgba(255, 255, 255, 0.8)) center / 102% 102%',
    darkConfig: {
      color: '#00a7a7',
      cover: `url(${wallpaper01DarkCover}) center / 100% 100%`,
      wallpaper: `url(${wallpaper01Dark}) center / 100% 100%`,
      maskColor: 'rgba(0, 0, 0, 0.52)',
      headerBg: 'rgba(0, 0, 0, 0.28)',
      sidebarBg: 'rgba(0, 0, 0, 0.28)',
      cardBg: 'rgba(0, 0, 0, 0.36)',
      overlayBg: `url(${wallpaper01Dark}) center / 100% 100%`,
      overlayMaskColor: 'rgba(0, 0, 0, 0.6)'
    },
    layouts: SKIN_LAYOUTS
  },
  {
    name: 'technology',
    color: '#1677ff',
    cover: `url(${wallpaper02Cover}) center / 100% 100%`,
    wallpaper: `url(${wallpaper02}) center / 100% 100%`,
    maskColor: 'rgba(214, 227, 250, 0.4)',
    headerBg: 'rgba(255, 255, 255, 0.4)',
    sidebarBg: 'rgba(255, 255, 255, 0.4)',
    cardBg: 'rgba(255, 255, 255, 0.68)',
    overlayBg: `url(${wallpaper02}) center / 100% 100%`,
    overlayMaskColor:
      'linear-gradient(0deg, rgba(255, 255, 255, 0.8), rgba(214, 227, 250, 0.4), rgba(255, 255, 255, 0.8)) center / 102% 102%',
    darkConfig: {
      color: '#13c2c2',
      cover: `url(${wallpaper02DarkCover}) center / 100% 100%`,
      wallpaper: `url(${wallpaper02Dark}) center / 100% 100%`,
      maskColor: 'rgba(0, 0, 0, 0)',
      headerBg: 'rgba(22, 44, 78, 0.68)',
      sidebarBg: 'rgba(22, 44, 78, 0.68)',
      cardBg: 'rgba(22, 44, 78, 0.68)',
      overlayBg: `url(${wallpaper02Dark}) center / 100% 100%`,
      overlayMaskColor:
        'linear-gradient(0deg, rgba(18, 44, 82, 0.8), rgba(22, 44, 78, 0.4), rgba(18, 44, 82, 0.8)) center / 102% 102%'
    },
    layouts: SKIN_LAYOUTS
  },
  {
    name: 'aesthetic',
    cover: `url(${wallpaper03Cover}) bottom center / cover`,
    wallpaper: `url(${wallpaper03}) bottom center / cover`,
    maskColor:
      'linear-gradient(22deg, rgba(240, 242, 245, 0.08) 0%, rgba(240, 242, 245, 0.88) 100%) center / 100% 100%',
    headerBg: 'rgba(255, 255, 255, 0.48)',
    sidebarBg: 'rgba(255, 255, 255, 0.48)',
    cardBg: 'rgba(255, 255, 255, 0.68)',
    overlayBg: `url(${wallpaper03}) bottom center / cover`,
    overlayMaskColor: 'rgba(255, 255, 255, 0.8)',
    darkConfig: {
      cover: `url(${wallpaper03Cover}) bottom center / cover`,
      wallpaper: `url(${wallpaper03}) bottom center / cover`,
      maskColor: 'rgba(0, 0, 0, 0.68)',
      headerBg: 'rgba(0, 0, 0, 0.2)',
      sidebarBg: 'rgba(0, 0, 0, 0.2)',
      cardBg: 'rgba(0, 0, 0, 0.28)',
      overlayBg: `url(${wallpaper03}) bottom center / cover`,
      overlayMaskColor: 'rgba(0, 0, 0, 0.8)'
    },
    layouts: SKIN_LAYOUTS
  },
  {
    name: 'cartoon',
    color: '#32a2d4',
    cover: `url(${wallpaper04Cover}) top center / cover`,
    wallpaper: `url(${wallpaper04}) top center / cover`,
    maskColor: 'rgba(255, 255, 255, 0.2)',
    headerBg: 'rgba(255, 255, 255, 0.48)',
    sidebarBg: 'rgba(255, 255, 255, 0.48)',
    cardBg: 'rgba(255, 255, 255, 0.8)',
    overlayBg: 'linear-gradient(238deg, #fff1eb 0%, #ace0f9 120%)',
    darkConfig: {
      color: '#32a2d4',
      cover: `url(${wallpaper04Cover}) top center / cover`,
      wallpaper: `url(${wallpaper04}) top center / cover`,
      maskColor: 'rgba(0, 0, 0, 0.68)',
      headerBg: 'rgba(0, 0, 0, 0.28)',
      sidebarBg: 'rgba(0, 0, 0, 0.28)',
      cardBg: 'rgba(0, 0, 0, 0.48)',
      overlayBg: 'linear-gradient(238deg, #372406 0%, #04293a 120%)'
    },
    layouts: SKIN_LAYOUTS
  }
];

/**
 * 主题色类型
 */
export interface ThemeItem {
  /** 主题名称 */
  name: string;
  /** 主题颜色值 */
  value?: string;
  /** 主题抽屉中显示的色块颜色 */
  color?: string;
}

/**
 * 预设主题色
 */
export const PREDEFINE_THEMES: ThemeItem[] = [
  { name: 'default', color: '#2f54eb' },
  { name: 'geekblue', value: '#1677ff' },
  { name: 'green', value: '#1ab394' },
  { name: 'purple', value: '#9333ea' },
  { name: 'volcano', value: '#f5686f' },
  { name: 'sunset', value: '#f59b00' },
  { name: 'dust', value: '#5f80c7' }
];

/**
 * 主题颜色选择器预设颜色
 */
export const PREDEFINE_COLORS: string[] = [
  '#0073e6',
  '#0057c3',
  '#2a49b5',
  '#4562bd',
  '#1cad70',
  '#16a34a',
  '#eb4646',
  '#32a2d4',
  '#0ea5e9',
  '#13c2c2'
];
