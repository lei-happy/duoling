/** 与后端 app.modules.client.constants.plate_category 枚举一致 */

export type PlateCategory = 'BLUE' | 'YELLOW' | 'NEW_ENERGY';

export const DEFAULT_PLATE_CATEGORY: PlateCategory = 'YELLOW';

export const PLATE_CATEGORY_OPTIONS: {
  value: PlateCategory;
  label: string;
}[] = [
  { value: 'BLUE', label: '蓝牌' },
  { value: 'YELLOW', label: '黄牌' },
  { value: 'NEW_ENERGY', label: '新能源' }
];

/** 机动车号牌录入长度（不含分隔符） */
export function plateInputMaxLen(category: PlateCategory): number {
  return category === 'NEW_ENERGY' ? 8 : 7;
}

/** 挂车号牌：黄牌/蓝牌为 京A1234挂（7 字符）；新能源按 8 位小型新能源规则 */
export function trailerPlateInputMaxLen(category: PlateCategory): number {
  return category === 'NEW_ENERGY' ? 8 : 7;
}
