/** 租户品牌（biz_vehicle_brand） */

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
  seriesCount?: number;
}
