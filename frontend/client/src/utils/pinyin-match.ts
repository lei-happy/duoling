import { pinyin } from 'pinyin-pro';

type PinyinIndex = { full: string; initial: string };

/** 按原文缓存全拼/首字母，避免大列表每次按键重复转换 */
const cache = new Map<string, PinyinIndex>();

/**
 * 获取文本的全拼与首字母索引（小写、无声调）
 */
export function getPinyinIndex(text: string): PinyinIndex {
  const key = text ?? '';
  let hit = cache.get(key);
  if (!hit) {
    hit = {
      full: pinyin(key, { toneType: 'none', type: 'array' }).join('').toLowerCase(),
      initial: pinyin(key, {
        pattern: 'first',
        toneType: 'none',
        type: 'array'
      })
        .join('')
        .toLowerCase()
    };
    cache.set(key, hit);
  }
  return hit;
}

/**
 * 预热缓存（树/列表加载后调用，把转换成本挪到加载阶段）
 */
export function warmPinyinCache(texts: Iterable<string>) {
  for (const t of texts) {
    if (t) getPinyinIndex(t);
  }
}

/**
 * 文本是否匹配关键词（中文包含 + 全拼/首字母子串，与后端 match_pinyin 一致）
 */
export function pinyinMatch(text: string, keyword: string): boolean {
  if (!keyword) return true;
  const kw = keyword.toLowerCase().trim();
  if (!kw) return true;
  const t = text ?? '';
  if (t.toLowerCase().includes(kw)) return true;
  const { full, initial } = getPinyinIndex(t);
  return full.includes(kw) || initial.includes(kw);
}
