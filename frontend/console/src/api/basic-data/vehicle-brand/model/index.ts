/** 平台品牌（basicdata_brand） */

export interface VehicleBrand {
  brandId: number;
  brandLogo?: string | null;
  brandNameCn: string;
  brandCountry?: string | null;
  brandIntroduce?: string | null;
  createTime?: string | null;
  lastUpdateTime?: string | null;
}

export interface VehicleBrandOption {
  brandId: number;
  brandNameCn: string;
  brandLogo?: string | null;
  /** 该平台品牌下车系数量 */
  seriesCount?: number;
}
