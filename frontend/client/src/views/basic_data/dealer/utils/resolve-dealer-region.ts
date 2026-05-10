/**
 * 将历史经销商 province/city 文本解析为 RegionsSelect(provinceCity) 所需的 [省code, 市code]。
 * 约束：O4-B 规范化 + 全局唯一才成功；否则 O2-A 由调用方置空并提示。
 */

import type { RegionsData } from '@/components/RegionsSelect/util';

export type ResolveDealerRegionResult =
  | { ok: true; codes: [string, string] }
  | { ok: false; reason: 'empty' | 'no_match' | 'ambiguous' };

/** 直辖市（国标树第一级 label） */
const MUNICIPALITY_ROOT_LABELS = new Set([
  '北京市',
  '天津市',
  '上海市',
  '重庆市'
]);

function spaceNorm(s: string): string {
  return s.replace(/[\u3000\s]+/g, ' ').trim();
}

/** 去首尾空白；合并空白（O4-B 基础） */
export function normalizeWhitespace(s: string): string {
  return spaceNorm(s);
}

/**
 * 生成用于「与国标 label 比对」的别名集合（O4-B：后缀/常见简称）
 */
function labelMatchKeys(name: string): Set<string> {
  const raw = spaceNorm(name);
  const keys = new Set<string>();
  if (!raw) return keys;
  keys.add(raw);

  // 常见后缀补全（用户写简称）
  if (!raw.endsWith('省')) keys.add(`${raw}省`);
  if (!raw.endsWith('市')) keys.add(`${raw}市`);
  if (!raw.endsWith('自治区')) {
    keys.add(`${raw}自治区`);
    keys.add(`${raw}壮族自治区`);
    keys.add(`${raw}回族自治区`);
    keys.add(`${raw}维吾尔自治区`);
  }

  // 常见简称（用户写全称时也会命中 raw）
  if (raw === '内蒙古') keys.add('内蒙古自治区');
  if (raw === '广西') keys.add('广西壮族自治区');
  if (raw === '西藏') keys.add('西藏自治区');
  if (raw === '宁夏') keys.add('宁夏回族自治区');
  if (raw === '新疆') keys.add('新疆维吾尔自治区');
  if (raw === '香港') keys.add('香港特别行政区');
  if (raw === '澳门') keys.add('澳门特别行政区');

  // 去掉行政后缀后的「核心名」再展开一轮（如 北京市 -> 北京）
  const stripped = stripAdminSuffix(raw);
  if (stripped && stripped !== raw) {
    keys.add(stripped);
    if (!stripped.endsWith('省')) keys.add(`${stripped}省`);
    if (!stripped.endsWith('市')) keys.add(`${stripped}市`);
  }

  return keys;
}

function stripAdminSuffix(s: string): string {
  let t = s;
  const suffixes = [
    '壮族自治区',
    '回族自治区',
    '维吾尔自治区',
    '特别行政区',
    '自治区',
    '省',
    '市'
  ];
  for (const suf of suffixes) {
    if (t.endsWith(suf)) {
      t = t.slice(0, -suf.length);
      break;
    }
  }
  return t;
}

function labelMatchesAny(label: string, keys: Set<string>): boolean {
  const L = spaceNorm(label);
  if (!L) return false;
  if (keys.has(L)) return true;
  const keysFromLabel = labelMatchKeys(L);
  for (const k of keys) {
    if (keysFromLabel.has(k)) return true;
  }
  for (const k of keys) {
    if (labelMatchKeys(k).has(L)) return true;
  }
  return false;
}

/** 直辖市：用户 city 写「北京」等与省名同源时，落到第二级「市辖区」等 */
function pickMunicipalitySecondLevel(
  root: RegionsData
): { value: string; label: string } | null {
  const children = root.children;
  if (!children?.length) return null;
  const shixiaqu = children.find((c) => c.label === '市辖区');
  if (shixiaqu) return { value: shixiaqu.value, label: shixiaqu.label };
  return { value: children[0].value, label: children[0].label };
}

function findProvinceNode(
  data: RegionsData[],
  provinceRaw: string
): RegionsData | null {
  const keys = labelMatchKeys(provinceRaw);
  if (keys.size === 0) return null;
  for (const p of data) {
    if (labelMatchesAny(p.label, keys)) return p;
  }
  return null;
}

function findCityChild(
  provinceNode: RegionsData,
  cityRaw: string
): { value: string; label: string } | null {
  const children = provinceNode.children;
  if (!children?.length) return null;
  const cityKeys = labelMatchKeys(cityRaw);
  if (cityKeys.size === 0) return null;

  const matches: { value: string; label: string }[] = [];
  for (const c of children) {
    if (labelMatchesAny(c.label, cityKeys)) {
      matches.push({ value: c.value, label: c.label });
    }
  }
  if (matches.length === 1) return matches[0];
  if (matches.length > 1) return null;

  // 直辖市：city 与省名同源（汽车之家常存「北京」）
  if (MUNICIPALITY_ROOT_LABELS.has(provinceNode.label)) {
    const provCore = stripAdminSuffix(provinceNode.label);
    const cityCore = stripAdminSuffix(spaceNorm(cityRaw));
    if (
      provCore &&
      cityCore &&
      (provCore === cityCore ||
        provinceNode.label.startsWith(cityCore) ||
        cityCore.startsWith(provCore))
    ) {
      return pickMunicipalitySecondLevel(provinceNode);
    }
  }

  return null;
}

/** 在省内按 label 匹配子级（不含直辖市「市名=省名」兜底，避免跨省误判） */
function findCityChildStrict(
  provinceNode: RegionsData,
  cityRaw: string
): { value: string; label: string } | null {
  const children = provinceNode.children;
  if (!children?.length) return null;
  const cityKeys = labelMatchKeys(cityRaw);
  if (cityKeys.size === 0) return null;
  const matches: { value: string; label: string }[] = [];
  for (const c of children) {
    if (labelMatchesAny(c.label, cityKeys)) {
      matches.push({ value: c.value, label: c.label });
    }
  }
  if (matches.length === 1) return matches[0];
  return null;
}

/**
 * 在「仅市名」条件下扫描全国，收集 [省, 市] 路径（用于唯一性判断）
 */
function collectPathsByCityOnly(
  data: RegionsData[],
  cityRaw: string
): [string, string][] {
  const paths: [string, string][] = [];
  for (const p of data) {
    const strict = findCityChildStrict(p, cityRaw);
    if (strict) {
      paths.push([p.value, strict.value]);
      continue;
    }
    if (MUNICIPALITY_ROOT_LABELS.has(p.label)) {
      const muni = findCityChild(p, cityRaw);
      if (muni) paths.push([p.value, muni.value]);
    }
  }
  const seen = new Set<string>();
  const unique: [string, string][] = [];
  for (const [pv, cv] of paths) {
    const k = `${pv}|${cv}`;
    if (seen.has(k)) continue;
    seen.add(k);
    unique.push([pv, cv]);
  }
  return unique;
}

/**
 * 根据租户库中的省、市自由文本，解析为与 regions-data.json 一致的二级 code 路径。
 */
export function resolveRegionCodesFromLegacyNames(
  regionsData: RegionsData[] | null | undefined,
  provinceRaw: string | undefined | null,
  cityRaw: string | undefined | null
): ResolveDealerRegionResult {
  const data = regionsData ?? [];
  if (!data.length) return { ok: false, reason: 'no_match' };

  const province = normalizeWhitespace(String(provinceRaw ?? ''));
  const city = normalizeWhitespace(String(cityRaw ?? ''));

  if (!province && !city) return { ok: false, reason: 'empty' };

  // 有省：先定省，再在省内找市
  if (province) {
    const pNode = findProvinceNode(data, province);
    if (!pNode) return { ok: false, reason: 'no_match' };
    if (!city) return { ok: false, reason: 'no_match' };
    const c = findCityChild(pNode, city);
    if (!c) return { ok: false, reason: 'no_match' };
    return { ok: true, codes: [pNode.value, c.value] };
  }

  // 仅市（平台同步常见：province 空）
  const paths = collectPathsByCityOnly(data, city);
  if (paths.length === 1) return { ok: true, codes: paths[0] };
  if (paths.length === 0) return { ok: false, reason: 'no_match' };
  return { ok: false, reason: 'ambiguous' };
}

/*
 * 样例（与 regions-data.json 一致时可解析）：
 * - resolve(..., '广东省', '深圳市') -> ['44','4403'] 形式（以实际 JSON value 为准）
 * - resolve(..., '', '北京') -> 直辖市唯一路径
 * - resolve(..., '', '未知市') -> no_match
 * - 若存在多条省下同名「县级」且与第二级 label 冲突，可能 ambiguous / no_match，需用户手选（O2-A）
 */
