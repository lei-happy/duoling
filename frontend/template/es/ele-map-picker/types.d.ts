/**
 * 位置选择模式
 */
export type SelectMode = 'lnglat' | 'poi' | 'keyword';

/**
 * 行政区数据
 */
export interface City {
  /** 省 */
  province: string;
  /** 市 */
  city: string;
  /** 区 */
  district: string;
  /** 区号 */
  citycode: number;
}

/**
 * 检索结果
 */
export interface PoiItem extends Record<string, any> {
  /** 唯一标识 */
  key?: string;
  /** 地点名称 */
  name?: string;
  /** 详细地址 */
  address?: string;
  /** 纬度 */
  lat?: number;
  /** 经度 */
  lng?: number;
  /** 输入建议的街道 */
  district?: string;
  /** 行政区 */
  city?: City;
}

/**
 * 实例
 */
export interface MapState {
  context?: any;
  /** 上次搜索建议 */
  lastSuggestion?: string;
  /** 选中的搜索建议 */
  selectedSuggestion?: PoiItem | null;
  /** 是否是选中条目移动地图 */
  isItemClickMove?: boolean;
  /** 地图实例 */
  mapIns?: any;
  /** 检索实例 */
  placeSearchIns?: any;
  /** 搜索建议实例 */
  autoCompleteIns?: any;
  /** 地图标记点 */
  centerMarker?: any;
}

/**
 * 国际化
 */
export interface MapLocale {
  title: string;
  placeholder: string;
  message: string;
  ok: string;
  clickMessage: string;
}

export type CenterPoint = PoiItem;
