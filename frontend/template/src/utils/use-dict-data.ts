import type { ComputedRef } from 'vue';
import { computed } from 'vue';
import { EleMessage } from 'ele-admin-plus';
import { useDictStore } from '@/store/modules/dict';
import { listDictionaryData } from '@/api/system/dictionary-data';
import type { DictionaryData } from '@/api/system/dictionary-data/model';
/** 获取字典数据是否只请求一次返回全部 */
const isSingleRequest = false;

/**
 * 请求并缓存字典数据
 */
export function useGetDictData() {
  const dictStore = useDictStore();

  const getDictData = (code: string) => {
    if (dictStore.getDicts(isSingleRequest ? void 0 : code) != null) {
      return;
    }
    if (isSingleRequest) {
      dictStore.setDicts({}, void 0);
    } else {
      dictStore.setDicts([], code);
    }
    listDictionaryData(isSingleRequest ? void 0 : { dictCode: code })
      .then((list) => {
        if (!isSingleRequest) {
          dictStore.setDicts(list, code);
        } else {
          const temp = new Map<string, DictionaryData[]>();
          list.forEach((item) => {
            const dictCode = item.dictCode;
            if (dictCode) {
              const tempList = temp.get(dictCode);
              if (!tempList) {
                temp.set(dictCode, [item]);
              } else {
                temp.set(dictCode, [...tempList, item]);
              }
            }
          });
          dictStore.setDicts(temp, void 0);
        }
      })
      .catch((e) => {
        dictStore.setDicts(null, isSingleRequest ? void 0 : code);
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  return { getDictData };
}

/**
 * 获取字典数据
 * @param codes 字典代码
 */
export function useDictData(codes: string[]): ComputedRef<DictionaryData[]>[] {
  const dictStore = useDictStore();
  const { getDictData } = useGetDictData();

  const result: ComputedRef<DictionaryData[]>[] = [];
  codes.forEach((code) => {
    result.push(
      computed<DictionaryData[]>(() => dictStore.getDicts(code) || [])
    );
    getDictData(code);
  });

  return result;
}
