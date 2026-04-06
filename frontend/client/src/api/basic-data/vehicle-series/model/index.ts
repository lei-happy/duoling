/** 租户车系 */

export interface VehicleSeries {
  seriesId: number;
  brandId: number;
  price?: string | null;
  seriesImage?: string | null;
  seriesName: string;
  energyType?: string | null;
  lengthMm?: number | null;
  widthMm?: number | null;
  heightMm?: number | null;
  wheelbaseMm?: number | null;
  frontTrackMm?: number | null;
  rearTrackMm?: number | null;
  approachAngle?: number | null;
  departureAngle?: number | null;
  curbWeightKg?: number | null;
  createTime?: string | null;
  lastUpdateTime?: string | null;
}
