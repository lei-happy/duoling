import { defineStore, storeToRefs } from 'pinia';
import { EleMessage } from 'ele-admin-plus';
import request from '@/utils/request';
const BASE_URL = import.meta.env.BASE_URL;

/**
 * 省市区数据
 */
export interface RegionsData {
  label: string;
  value: string;
  children?: {
    value: string;
    label: string;
    children?: {
      value: string;
      label: string;
    }[];
  }[];
}

/**
 * 省市区数据状态管理
 */
export const useRegionsStore = defineStore('regions', {
  state: () => ({
    regionsData: null as RegionsData[] | null
  }),
  actions: {
    setRegionsData(data: RegionsData[]) {
      this.regionsData = data;
    }
  }
});

/**
 * 获取省市区数据hook
 */
export function useRegionsData() {
  const regionsStore = useRegionsStore();
  const { regionsData } = storeToRefs(regionsStore);
  // 若还未缓存过则获取省市区数据
  if (regionsData.value == null) {
    regionsStore.setRegionsData([]);
    getRegionsData()
      .then((data) => {
        regionsStore.setRegionsData(data);
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  }
  return regionsData;
}

/**
 * 获取省市区数据
 */
export async function getRegionsData() {
  const res = await request.get<RegionsData[]>(
    BASE_URL + 'json/regions-data.json',
    { baseURL: '' }
  );
  return res.data ?? [];
}

/**
 * 省市区数据value处理
 * @param data 省市区数据
 * @param field value字段名
 */
export function formatData(data: RegionsData[], field?: string) {
  if (field === 'label') {
    return data.map((d) => {
      const item: RegionsData = { label: d.label, value: d.label };
      if (d.children) {
        item.children = d.children.map((c) => {
          const cItem: RegionsData = { label: c.label, value: c.label };
          if (c.children) {
            cItem.children = c.children.map((cc) => {
              return { label: cc.label, value: cc.label };
            });
          }
          return cItem;
        });
      }
      return item;
    });
  }
  return data;
}

/**
 * 省市区数据筛选
 * @param data 省市区数据
 * @param type 只需要省市数据或只需要省数据
 * @param field value字段名
 */
export function filterData(data: RegionsData[], type?: string, field?: string) {
  if (type === 'provinceCity') {
    return formatData(
      data.map((d) => {
        const item: RegionsData = { label: d.label, value: d.value };
        if (d.children) {
          item.children = d.children.map((c) => {
            return { label: c.label, value: c.value };
          });
        }
        return item;
      }),
      field
    );
  } else if (type === 'province') {
    return formatData(
      data.map((d) => ({ label: d.label, value: d.value })),
      field
    );
  }
  return formatData(data, field);
}

/**
 * 获取选中值对应的文本
 * @param values 选中值
 * @param data 省市区数据
 */
export function getValueLabel(values?: string[], data?: RegionsData[]) {
  const labels: string[] = [];
  if (values && values.length && data) {
    data.forEach((d) => {
      if (d.value === values[0]) {
        labels.push(d.label);
        if (d.children && d.children.length) {
          d.children.forEach((c) => {
            if (c.value === values[1]) {
              labels.push(c.label);
            }
            if (c.children && c.children.length) {
              c.children.forEach((cc) => {
                if (cc.value === values[2]) {
                  labels.push(cc.label);
                }
              });
            }
          });
        }
      }
    });
  }
  return labels;
}
