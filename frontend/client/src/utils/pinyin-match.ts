import { match } from 'pinyin-pro';

/**
 * 文本是否匹配关键词（中文包含 + 拼音/首字母，与《拼音搜索集成指南》一致）
 */
export function pinyinMatch(text: string, keyword: string): boolean {
  if (!keyword) return true;
  const kw = keyword.toLowerCase().trim();
  if (!kw) return true;
  const t = text ?? '';
  if (t.toLowerCase().includes(kw)) return true;
  return match(t, kw) != null;
}
