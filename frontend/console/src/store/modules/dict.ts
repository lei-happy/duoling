import { defineStore } from 'pinia';
import type { DictionaryData } from '@/api/system/dictionary-data/model';

/**
 * 字典状态管理
 */
export const useDictStore = defineStore('dict', {
  state: () => ({
    /** 字典数据缓存 */
    dicts: null as Map<string, DictionaryData[] | null | undefined> | null
  }),
  actions: {
    /**
     * 清空字典数据
     */
    clearDicts() {
      if (this.dicts == null) {
        return;
      }
      this.dicts.clear();
    },
    /**
     * 更新字典数据
     * @param value 字典数据
     * @param code 字典代码
     */
    setDicts<T extends string | null | undefined>(
      value: T extends string
        ? DictionaryData[] | null | undefined
        :
            | Map<string, DictionaryData[]>
            | Record<string, DictionaryData[]>
            | null
            | undefined,
      code: T
    ) {
      if (code != null) {
        if (this.dicts == null) {
          this.dicts = new Map<string, DictionaryData[]>();
        }
        this.dicts.set(code, value as DictionaryData[] | null | undefined);
        return;
      }
      if (value == null) {
        this.dicts = null;
        return;
      }
      if (value instanceof Map) {
        this.dicts = value;
        return;
      }
      if (this.dicts == null) {
        this.dicts = new Map<string, DictionaryData[]>();
      } else {
        this.clearDicts();
      }
      Object.keys(value).forEach((key) => {
        (this.dicts as Map<string, DictionaryData[]>).set(key, value[key]);
      });
    },
    /**
     * 获取字典数据
     * @param code 字典代码
     */
    getDicts<T extends string | null | undefined>(
      code: T
    ): T extends string
      ? DictionaryData[] | null | undefined
      : Map<string, DictionaryData[]> | null | undefined {
      if (code != null) {
        if (this.dicts == null) {
          return void 0 as any;
        }
        return this.dicts.get(code) as any;
      }
      return this.dicts as any;
    }
  }
});
