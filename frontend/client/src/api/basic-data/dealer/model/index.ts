import type { PageParam } from '@/api';

/** 租户经销商（biz_dealer） */

export interface Dealer {
  dealerId: number;
  dealerName: string;
  dealerType: string;
  mainBrand: string;
  province: string;
  city: string;
  addressDetail: string;
  longitude?: number | null;
  latitude?: number | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface DealerParam extends PageParam {
  keyword?: string;
}
