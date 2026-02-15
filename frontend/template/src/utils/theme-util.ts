import { cloneDeep } from 'lodash-es';
import { changeColor, changeSkin } from 'ele-admin-plus/es/utils/theme-util';
import type { SkinConfig } from 'ele-admin-plus/es/utils/theme-util';
import { THEME_CACHE_NAME } from '@/config/setting';
import { PREDEFINED_SKINS, SKIN_LAYOUTS } from './skin-config';

/**
 * 读取缓存配置
 */
export function getCacheSetting(): Record<string, any> {
  try {
    const value = localStorage.getItem(THEME_CACHE_NAME);
    if (value) {
      const cache = JSON.parse(value);
      if (typeof cache === 'object') {
        return cache;
      }
    }
  } catch (e) {
    console.error(e);
  }
  return {};
}

/**
 * 需要排除缓存的主题属性
 */
const CACHE_EXCLUDES = ['maximized', 'expanded', 'contentWidth'];

/**
 * 重置时排除的主题属性
 */
export const RESET_EXCLUDES = ['contentWidth', 'tabs'];

/**
 * 清除缓存配置
 * @param keys 需要清除的属性
 * @param excludeKeys 不需要清除的属性
 */
export function clearSetting(keys?: string[], excludeKeys?: string[]) {
  const cache = getCacheSetting();
  if (keys != null) {
    keys.forEach((k) => {
      if (
        (!excludeKeys || !excludeKeys.includes(k)) &&
        !RESET_EXCLUDES.includes(k)
      ) {
        cache[k] = void 0;
      }
    });
  } else if (excludeKeys != null) {
    Object.keys(cache).forEach((k) => {
      if (!excludeKeys.includes(k) && !RESET_EXCLUDES.includes(k)) {
        cache[k] = void 0;
      }
    });
  } else {
    Object.keys(cache).forEach((k) => {
      if (!RESET_EXCLUDES.includes(k)) {
        cache[k] = void 0;
      }
    });
  }
  cacheSetting(cache);
}

/**
 * 缓存配置
 * @param key 属性名或需要缓存的整个数据
 * @param value 值
 */
export function cacheSetting(
  key?: string | null | Record<string, any>,
  value?: unknown
) {
  if (key == null) {
    clearSetting();
    return;
  }
  if (typeof key === 'object') {
    const cache = getCacheSetting();
    Object.keys(key).forEach((k) => {
      if (!CACHE_EXCLUDES.includes(k)) {
        cache[k] = key[k];
      }
    });
    localStorage.setItem(THEME_CACHE_NAME, JSON.stringify(cache));
    return;
  }
  if (CACHE_EXCLUDES.includes(key)) {
    return;
  }
  const cache = getCacheSetting();
  if (cache[key] !== value) {
    cache[key] = value;
    localStorage.setItem(THEME_CACHE_NAME, JSON.stringify(cache));
  }
}

/**
 * 切换圆角主题
 * @param roundedTheme 是否开启圆角主题
 */
export function changeRoundedTheme(roundedTheme: boolean) {
  const classes = 'rounded';
  const $html = document.documentElement;
  if ($html && roundedTheme) {
    $html.classList.add(classes);
  } else if ($html) {
    $html.classList.remove(classes);
  }
}

/**
 * 切换色弱模式
 * @param weakMode 是否开启色弱模式
 */
export function changeWeakMode(weakMode: boolean) {
  const classes = 'ele-admin-weak';
  const $html = document.documentElement;
  if (weakMode) {
    $html.classList.add(classes);
  } else {
    $html.classList.remove(classes);
  }
}

/**
 * 开关响应式布局
 * @param responsive 是否开启移动端响应式
 */
export function changeResponsive(responsive: boolean) {
  const classes = 'ele-body-limited';
  if (responsive) {
    document.body.classList.remove(classes);
  } else {
    document.body.classList.add(classes);
  }
}

/**
 * 皮肤背景文件访问链接缓存
 */
const SKIN_BG_CACHE = new Map<string, string>();

/**
 * 缓存皮肤背景文件访问链接
 * @param id 文件 id
 * @param file 文件
 */
export function cacheSkinBg(id: string, file?: File | Blob) {
  const bg = SKIN_BG_CACHE.get(id);
  if (bg) {
    return bg;
  }
  const url = file ? URL.createObjectURL(file) : void 0;
  if (url) {
    const bg = `url(${url}) top / cover`;
    SKIN_BG_CACHE.set(id, bg);
    return bg;
  }
}

/**
 * 皮肤背景文件缓存表名
 */
const WALLPAPER_STORE_NAME = 'wallpaperFileCacheStore';

/**
 * 初始化皮肤背景文件缓存数据库
 */
function initWallpaperDB() {
  const WALLPAPER_DB_NAME = 'wallpaperFileCacheDB';
  return new Promise<IDBDatabase>((resolve, reject) => {
    const request = indexedDB.open(WALLPAPER_DB_NAME, 1);
    request.onupgradeneeded = (e: any) => {
      const db: IDBDatabase = e.target?.result;
      if (!db.objectStoreNames.contains(WALLPAPER_STORE_NAME)) {
        db.createObjectStore(WALLPAPER_STORE_NAME, { keyPath: 'id' });
      }
    };
    request.onsuccess = (e: any) => resolve(e.target?.result);
    request.onerror = (e: any) => reject(e.target?.error);
  });
}

/**
 * 缓存皮肤背景文件
 * @param file 文件
 */
export async function storeWallpaperFile(file: File) {
  const id = JSON.stringify({
    name: file.name,
    type: file.type,
    lastModified: file.lastModified
  });
  const content = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(new Uint8Array(e.target?.result as any));
    reader.onerror = (e) => reject(e.target?.error);
    reader.readAsArrayBuffer(file);
  });
  const db = await initWallpaperDB();
  const transaction = db.transaction(WALLPAPER_STORE_NAME, 'readwrite');
  const store = transaction.objectStore(WALLPAPER_STORE_NAME);
  const request = store.put({ id, type: file.type, content });
  await new Promise<void>((resolve, reject) => {
    request.onsuccess = () => resolve();
    request.onerror = (e: any) => reject(e.target?.error);
  });
  return id;
}

/**
 * 获取缓存的皮肤背景文件
 * @param id 文件 id
 */
async function getWallpaperFile(id: string) {
  const db = await initWallpaperDB();
  const transaction = db.transaction(WALLPAPER_STORE_NAME, 'readonly');
  const store = transaction.objectStore(WALLPAPER_STORE_NAME);
  const request = store.get(id);
  const content = await new Promise<Blob | undefined>((resolve, reject) => {
    request.onsuccess = (e: any) => {
      const data = e.target?.result;
      if (!data) {
        resolve(void 0);
      } else {
        const blob = new Blob([data.content], { type: data.type });
        resolve(blob);
      }
    };
    request.onerror = (e: any) => reject(e.target?.error);
  });
  return content;
}

/**
 * 清空缓存的皮肤背景文件
 */
async function clearAllWallpaperFile() {
  const db = await initWallpaperDB();
  const transaction = db.transaction(WALLPAPER_STORE_NAME, 'readwrite');
  const store = transaction.objectStore(WALLPAPER_STORE_NAME);
  const request = store.clear();
  await new Promise<void>((resolve, reject) => {
    request.onsuccess = () => resolve();
    request.onerror = (e: any) => reject(e.target?.error);
  });
}

/**
 * 删除未使用的缓存的皮肤背景文件
 * @param ids 还在使用的文件 id
 */
async function clearWallpaperFile(ids: string[]) {
  const db = await initWallpaperDB();
  const transaction = db.transaction(WALLPAPER_STORE_NAME, 'readwrite');
  const store = transaction.objectStore(WALLPAPER_STORE_NAME);
  const request = store.getAll();
  const data: any = await new Promise((resolve, reject) => {
    request.onsuccess = (e: any) => resolve(e.target?.result);
    request.onerror = (e: any) => reject(e.target?.error);
  });
  for (const item of data) {
    if (!ids.includes(item.id)) {
      const deleteRequest = store.delete(item.id);
      await new Promise<void>((resolve, reject) => {
        deleteRequest.onsuccess = () => resolve();
        deleteRequest.onerror = (e: any) => reject(e.target?.error);
      });
    }
  }
}

/**
 * 判断图片背景是否为文件 id 形式
 * @param wallpaper 图片背景
 */
function isWallpaperFileId(wallpaper?: string) {
  return wallpaper != null && wallpaper.startsWith('{');
}

/**
 * 获取皮肤背景配置
 * @param config 配置
 * @param isId 背景图片是否返回文件 id 的形式
 * @param isCache 是否是缓存的数据需要同步最新的配置
 */
export async function getSkinConfig(
  config?: SkinConfig | null,
  isId?: boolean,
  isCache?: boolean
) {
  if (!config) {
    return config ?? null;
  }
  const skin: SkinConfig = { ...config };
  if (isCache) {
    // 缓存的旧图片同步最新的预设皮肤
    if (skin.name) {
      const ps = PREDEFINED_SKINS.find((s) => s.name === skin.name);
      if (ps) {
        Object.assign(skin, cloneDeep(ps));
      }
    } else if (skin.skinName) {
      const ps = PREDEFINED_SKINS.find((s) => s.name === skin.skinName);
      if (ps) {
        if (skin.wallpaper && !isWallpaperFileId(skin.wallpaper)) {
          skin.wallpaper = ps.wallpaper;
        }
        if (skin.overlayBg && !isWallpaperFileId(skin.overlayBg)) {
          skin.overlayBg = ps.overlayBg;
        }
        if (
          skin.darkConfig?.wallpaper &&
          !isWallpaperFileId(skin.darkConfig.wallpaper)
        ) {
          skin.darkConfig.wallpaper = ps.darkConfig?.wallpaper;
        }
        if (
          skin.darkConfig?.overlayBg &&
          !isWallpaperFileId(skin.darkConfig.overlayBg)
        ) {
          skin.darkConfig.overlayBg = ps.darkConfig?.overlayBg;
        }
      }
    }
  }
  const keys = Object.keys(skin);
  for (const key of keys) {
    const value = skin[key];
    if (key === 'darkConfig') {
      skin[key] = (await getSkinConfig(value, isId)) as any;
    } else if (value != null && typeof value === 'string') {
      if (isId) {
        for (const [id, url] of SKIN_BG_CACHE.entries()) {
          if (url === value) {
            skin[key] = id;
            break;
          }
        }
      } else if (isWallpaperFileId(value)) {
        const url = SKIN_BG_CACHE.get(value);
        if (url) {
          skin[key] = url;
        } else {
          const blob = await getWallpaperFile(value);
          skin[key] = cacheSkinBg(value, blob);
        }
      }
    }
  }
  return skin;
}

/**
 * 获取缓存的皮肤背景
 * @param cfg 默认的皮肤背景
 */
export async function getCacheSkinConfig(cfg?: SkinConfig | null) {
  const cache = getCacheSetting();
  const skin = typeof cache.skinConfig !== 'undefined' ? cache.skinConfig : cfg;
  const skinConfig = await getSkinConfig(skin, false, true);
  if (skinConfig != null && !skinConfig.name) {
    skinConfig.layouts = SKIN_LAYOUTS;
  }
  return skinConfig;
}

/**
 * 释放无用的皮肤背景文件缓存
 * @param isAll 是否全部释放
 * @param skinConfig 当前皮肤背景配置
 */
export async function releaseSkinBgCache(
  isAll?: boolean,
  skinConfig?: SkinConfig | null
) {
  // 释放全部
  if (isAll || !skinConfig) {
    SKIN_BG_CACHE.forEach((url) => {
      URL.revokeObjectURL(url);
    });
    SKIN_BG_CACHE.clear();
    await clearAllWallpaperFile();
    return;
  }
  // 释放未使用的文件
  const urls = [
    skinConfig.wallpaper,
    skinConfig.overlayBg,
    skinConfig.darkConfig?.wallpaper,
    skinConfig.darkConfig?.overlayBg
  ];
  const delIds: string[] = [];
  SKIN_BG_CACHE.forEach((url, id) => {
    if (!urls.some((u) => u && u.includes(url))) {
      URL.revokeObjectURL(url);
      delIds.push(id);
    }
  });
  delIds.forEach((id) => {
    SKIN_BG_CACHE.delete(id);
  });
  await clearWallpaperFile(SKIN_BG_CACHE ? [...SKIN_BG_CACHE.keys()] : []);
}

/**
 * 皮肤背景中的主题状态配置排除的字段
 */
export const SKIN_THEME_CONFIG_EXCLUDES = [
  'color',
  'roundedTheme',
  'weakMode',
  'darkMode',
  'contentWidth',
  'responsive',
  'skinConfig',
  'layoutName'
];

/**
 * 切换主题
 * @param color 主题色
 * @param dark 是否是暗黑模式
 * @param skinCfg 皮肤背景配置
 */
export function changeTheme(
  color?: string | null,
  dark?: boolean,
  skinCfg?: SkinConfig | null
) {
  // 切换主题色
  const isTransparent = !(
    !skinCfg ||
    (!skinCfg.wallpaper &&
      !skinCfg.maskColor &&
      !skinCfg.headerBg &&
      !skinCfg.sidebarBg &&
      !skinCfg.cardBg &&
      !skinCfg.overlayBg &&
      !skinCfg.overlayMaskColor)
  );
  changeColor(
    isTransparent ? (color ?? '#2f54eb') : color,
    dark,
    isTransparent
  );
  // 切换皮肤背景
  changeSkin(skinCfg, dark);
  // 切换自定义主题类名
  const $html = document.documentElement;
  $html.className.split(' ').forEach((className) => {
    if (className.startsWith('ele-theme-')) {
      $html.classList.remove(className);
    }
  });
  const themeClass = (dark ? skinCfg?.darkConfig : skinCfg)?.themeClass;
  if (themeClass) {
    $html.classList.add(themeClass);
  }
}
