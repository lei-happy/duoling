import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';

export type WaybillEditTabName = 'basic' | 'cargo' | 'receive' | 'freight';

export type CargoEditRow = {
  vehicleBrand?: string;
  vehicleModel?: string;
  quantityStr: string;
  /** 与后端 normalize 一致：仅大写字母数字 */
  vinStr: string;
  /** 编辑时回填的 cargo.id；无 id 表示本次新增行（须填 VIN） */
  cargoId?: number | null;
  /** 新建与「添加新车」为 true；编辑时无 VIN 的旧行仅台数 */
  requireVin: boolean;
  brandId?: number | null;
  seriesOptions: VehicleSeries[];
};
