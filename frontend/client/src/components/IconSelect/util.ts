import type { App } from 'vue';
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeStore } from '@/store/modules/theme';
import * as elIcons from '@element-plus/icons-vue';
import * as eleIcons from '@/components/icons';
/** element-plus 的图标全局安装的前缀 */
const elIconPrefix = 'IconEl';
/** ele-admin-plus 的图标全局安装的前缀 */
const eleIconPrefix = 'IconPro';

/**
 * 组件文案
 */
export interface IconSelectLocale {
  outlined: string;
  filled: string;
}

/**
 * 获取全部图标数据
 */
export function getIconData() {
  const iconData: Record<string, any> = {};
  Object.keys(elIcons).forEach((key) => {
    iconData[`${elIconPrefix}${key}`] = elIcons[key];
  });
  Object.keys(eleIcons).forEach((key) => {
    iconData[`${eleIconPrefix}${key}`] = eleIcons[key];
  });
  return iconData;
}

/**
 * 图标组件全局安装
 */
export const iconsInstaller = {
  install(app: App) {
    const iconData = getIconData();
    Object.keys(iconData).forEach((key) => {
      app.component(key, iconData[key]);
    });
  }
};

/**
 * 图标下拉选择器的 element-plus 的图标数据
 */
export const elementIconData = [
  {
    title: 'System',
    icons: [
      'Plus',
      'Minus',
      'CirclePlus',
      'Search',
      'Female',
      'Male',
      'Aim',
      'House',
      'FullScreen',
      'Loading',
      'Link',
      'Service',
      'Pointer',
      'Star',
      'Notification',
      'Connection',
      'ChatDotRound',
      'Setting',
      'Clock',
      'Position',
      'Discount',
      'Odometer',
      'ChatSquare',
      'ChatRound',
      'ChatLineRound',
      'ChatLineSquare',
      'ChatDotSquare',
      'View',
      'Hide',
      'Unlock',
      'Lock',
      'RefreshRight',
      'RefreshLeft',
      'Refresh',
      'Bell',
      'MuteNotification',
      'User',
      'Check',
      'CircleCheck',
      'Warning',
      'CircleClose',
      'Close',
      'PieChart',
      'More',
      'Compass',
      'Filter',
      'Switch',
      'Select',
      'SemiSelect',
      'CloseBold',
      'EditPen',
      'Edit',
      'Message',
      'MessageBox',
      'TurnOff',
      'Finished',
      'Delete',
      'Crop',
      'SwitchButton',
      'Operation',
      'Open',
      'Remove',
      'ZoomOut',
      'ZoomIn',
      'InfoFilled',
      'CircleCheckFilled',
      'SuccessFilled',
      'WarningFilled',
      'CircleCloseFilled',
      'QuestionFilled',
      'WarnTriangleFilled',
      'UserFilled',
      'MoreFilled',
      'Tools',
      'HomeFilled',
      'Menu',
      'UploadFilled',
      'Avatar',
      'HelpFilled',
      'Share',
      'StarFilled',
      'Comment',
      'Histogram',
      'Grid',
      'Promotion',
      'DeleteFilled',
      'RemoveFilled',
      'CirclePlusFilled'
    ]
  },
  {
    title: 'Arrow',
    icons: [
      'ArrowLeft',
      'ArrowUp',
      'ArrowRight',
      'ArrowDown',
      'ArrowLeftBold',
      'ArrowUpBold',
      'ArrowRightBold',
      'ArrowDownBold',
      'DArrowRight',
      'DArrowLeft',
      'Download',
      'Upload',
      'Top',
      'Bottom',
      'Back',
      'Right',
      'TopRight',
      'TopLeft',
      'BottomRight',
      'BottomLeft',
      'Sort',
      'SortUp',
      'SortDown',
      'Rank',
      'CaretLeft',
      'CaretTop',
      'CaretRight',
      'CaretBottom',
      'DCaret',
      'Expand',
      'Fold'
    ]
  },
  {
    title: 'Document',
    icons: [
      'DocumentAdd',
      'Document',
      'Notebook',
      'Tickets',
      'Memo',
      'Collection',
      'Postcard',
      'ScaleToOriginal',
      'SetUp',
      'DocumentDelete',
      'DocumentChecked',
      'DataBoard',
      'DataAnalysis',
      'CopyDocument',
      'FolderChecked',
      'Files',
      'Folder',
      'FolderDelete',
      'FolderRemove',
      'FolderOpened',
      'DocumentCopy',
      'DocumentRemove',
      'FolderAdd',
      'FirstAidKit',
      'Reading',
      'DataLine',
      'Management',
      'Checked',
      'Ticket',
      'Failed',
      'TrendCharts',
      'List'
    ]
  },
  {
    title: 'Media',
    icons: [
      'Microphone',
      'Mute',
      'Mic',
      'VideoPause',
      'VideoCamera',
      'VideoPlay',
      'Headset',
      'Monitor',
      'Film',
      'Camera',
      'Picture',
      'PictureRounded',
      'Iphone',
      'Cellphone',
      'VideoCameraFilled',
      'PictureFilled',
      'Platform',
      'CameraFilled',
      'BellFilled'
    ]
  },
  {
    title: 'Traffic',
    icons: [
      'Location',
      'LocationInformation',
      'DeleteLocation',
      'Coordinate',
      'Bicycle',
      'OfficeBuilding',
      'School',
      'Guide',
      'AddLocation',
      'MapLocation',
      'Place',
      'LocationFilled',
      'Van'
    ]
  },
  {
    title: 'Food',
    icons: [
      'Watermelon',
      'Pear',
      'NoSmoking',
      'Smoking',
      'Mug',
      'GobletSquareFull',
      'GobletFull',
      'KnifeFork',
      'Sugar',
      'Bowl',
      'MilkTea',
      'Lollipop',
      'Coffee',
      'Chicken',
      'Dish',
      'IceTea',
      'ColdDrink',
      'CoffeeCup',
      'DishDot',
      'IceDrink',
      'IceCream',
      'Dessert',
      'IceCreamSquare',
      'ForkSpoon',
      'IceCreamRound',
      'Food',
      'HotWater',
      'Grape',
      'Fries',
      'Apple',
      'Burger',
      'Goblet',
      'GobletSquare',
      'Orange',
      'Cherry'
    ]
  },
  {
    title: 'Items',
    icons: [
      'Printer',
      'Calendar',
      'CreditCard',
      'Box',
      'Money',
      'Refrigerator',
      'Cpu',
      'Football',
      'Brush',
      'Suitcase',
      'SuitcaseLine',
      'Umbrella',
      'AlarmClock',
      'Medal',
      'GoldMedal',
      'Present',
      'Mouse',
      'Watch',
      'QuartzWatch',
      'Magnet',
      'Help',
      'Soccer',
      'ToiletPaper',
      'ReadingLamp',
      'Paperclip',
      'MagicStick',
      'Basketball',
      'Baseball',
      'Coin',
      'Goods',
      'Sell',
      'SoldOut',
      'Key',
      'ShoppingCart',
      'ShoppingCartFull',
      'ShoppingTrolley',
      'Phone',
      'Scissor',
      'Handbag',
      'ShoppingBag',
      'Trophy',
      'TrophyBase',
      'Stopwatch',
      'Timer',
      'CollectionTag',
      'TakeawayBox',
      'PriceTag',
      'Wallet',
      'Opportunity',
      'PhoneFilled',
      'WalletFilled',
      'GoodsFilled',
      'Flag',
      'BrushFilled',
      'Briefcase',
      'Stamp'
    ]
  },
  {
    title: 'Weather',
    icons: [
      'Sunrise',
      'Sunny',
      'Ship',
      'MostlyCloudy',
      'PartlyCloudy',
      'Sunset',
      'Drizzling',
      'Pouring',
      'Cloudy',
      'Moon',
      'MoonNight',
      'Lightning'
    ]
  },
  {
    title: 'Other',
    icons: [
      'ChromeFilled',
      'Eleme',
      'ElemeFilled',
      'ElementPlus',
      'Shop',
      'SwitchFilled',
      'WindPower'
    ]
  }
];

/**
 * 获取图标下拉选择器数据
 */
export function getIconSelectData(lang: IconSelectLocale) {
  const iconNames = Object.keys(getIconData());
  const proIconNames = iconNames.filter((name) =>
    name.startsWith(eleIconPrefix)
  );
  return [
    {
      title: 'EleAdminPlus',
      children: [
        {
          title: lang.outlined,
          icons: proIconNames.filter((name) => !name.endsWith('Filled'))
        },
        {
          title: lang.filled,
          icons: proIconNames.filter((name) => name.endsWith('Filled'))
        }
      ]
    },
    {
      title: 'ElementPlus',
      children: elementIconData.map((group) => ({
        ...group,
        icons: group.icons.map((icon) => `IconEl${icon}`)
      }))
    }
  ];
}

/**
 * 清新主题图标图片地址数据
 */
export const imgIconUrls: Record<string, string> = import.meta.glob(
  '/src/assets/menu-icons/*.png',
  {
    import: 'default',
    eager: true
  }
);

/**
 * 清新主题图标图片名称数据
 */
export const imgIconNames = Object.keys(imgIconUrls).map((name) =>
  name.slice(0, name.lastIndexOf('.')).replace('/src/assets/menu-icons/', '')
);

/**
 * 自定义 SVG 图标地址数据
 */
export const svgIconUrls: Record<string, string> = import.meta.glob(
  '/src/assets/menu-icons/*.svg',
  {
    import: 'default',
    eager: true
  }
);

export const svgIconNames = Object.keys(svgIconUrls).map((name) =>
  name.slice(0, name.lastIndexOf('.')).replace('/src/assets/menu-icons/', '')
);

export function getSvgIconUrl(iconName: string): string | undefined {
  return svgIconUrls[`/src/assets/menu-icons/${iconName}.svg`];
}

/**
 * 判断是否是清新主题
 */
export function useIsSimpleTheme() {
  const themeStore = useThemeStore();
  const { skinConfig } = storeToRefs(themeStore);

  /** 是否是清新主题 */
  const isSimpleTheme = computed(() => skinConfig.value?.name === 'simple');

  return { isSimpleTheme };
}
