import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

/**
 * 组件多语言文案
 */
export interface ComponentLangs<T> {
  /** 简体中文 */
  zh_CN: T;
  /** 繁体中文 */
  zh_TW: T;
  /** 英文 */
  en: T;
}

/**
 * 含自定义文案字段的组件属性
 */
export interface UseComponentLangProps<T> extends Record<string, any> {
  /** 自定义文案 */
  componentLang?: Partial<T>;
}

/**
 * 组件支持多语言
 * @param langs 组件多语言文案
 * @param props 组件属性
 */
export function useComponentLang<T>(
  langs: ComponentLangs<T>,
  props?: UseComponentLangProps<T>
) {
  const { locale } = useI18n();

  const lang = computed<T>(() => {
    return Object.assign(
      {},
      langs.zh_CN,
      (locale.value ? langs[locale.value] : void 0) || {},
      props?.componentLang
    );
  });

  return { lang };
}
