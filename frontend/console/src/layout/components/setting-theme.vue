<template>
  <!-- 侧栏风格 -->
  <div class="ele-setting-theme">
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-side-light"
        @click="updateValue('sidebarStyle', 'light')"
      >
        <EleText
          v-if="sidebarStyle === 'light'"
          type="primary"
          :icon="CheckOutlined"
        />
      </div>
      <div>{{ t('layout.setting.sideStyles.light') }}</div>
    </div>
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-side-dark"
        @click="updateValue('sidebarStyle', 'dark')"
      >
        <EleText
          v-if="sidebarStyle === 'dark'"
          type="primary"
          :icon="CheckOutlined"
        />
      </div>
      <div>{{ t('layout.setting.sideStyles.dark') }}</div>
    </div>
  </div>
  <!-- 顶栏风格 -->
  <div class="ele-setting-theme">
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-head-light"
        @click="updateValue('headerStyle', 'light')"
      >
        <EleText
          v-if="headerStyle === 'light'"
          type="primary"
          :icon="CheckOutlined"
        />
      </div>
      <div>{{ t('layout.setting.headStyles.light') }}</div>
    </div>
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-head-dark"
        @click="updateValue('headerStyle', 'dark')"
      >
        <EleText
          v-if="headerStyle === 'dark'"
          type="primary"
          :icon="CheckOutlined"
        />
      </div>
      <div>{{ t('layout.setting.headStyles.dark') }}</div>
    </div>
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-head-primary"
        @click="updateValue('headerStyle', 'primary')"
      >
        <EleText
          v-if="headerStyle === 'primary'"
          type="primary"
          :icon="CheckOutlined"
        />
      </div>
      <div>{{ t('layout.setting.headStyles.primary') }}</div>
    </div>
  </div>
  <!-- 主题色 -->
  <div class="ele-setting-colors">
    <div
      v-for="item in PREDEFINE_THEMES"
      :key="item.name"
      :style="{ 'background-color': item.color || item.value }"
      class="ele-setting-color-item"
      :title="t(`layout.setting.colors.${item.name}`)"
      @click="updateColor(item.value)"
    >
      <ElIcon v-if="item.value ? item.value === color : !color">
        <CheckOutlined />
      </ElIcon>
    </div>
    <!-- 颜色选择器 -->
    <ElColorPicker
      :teleported="false"
      v-model="colorPickerValue"
      :predefine="PREDEFINE_COLORS"
      class="ele-setting-color-picker"
      :class="{ 'is-empty-color': !colorPickerValue }"
      :popperOptions="{ strategy: 'fixed' }"
      @change="updateColor"
    />
  </div>
  <!-- 暗黑模式 -->
  <SettingItem :title="t('layout.setting.darkMode')">
    <ElSwitch
      ref="darkSwitchRef"
      size="small"
      :modelValue="darkMode"
      @update:modelValue="updateDarkMode"
    />
  </SettingItem>
  <!-- 圆角主题 -->
  <SettingItem :title="t('layout.setting.roundedTheme')">
    <ElSwitch
      size="small"
      :modelValue="roundedTheme"
      @update:modelValue="(val) => updateValue('roundedTheme', val)"
    />
  </SettingItem>
  <ElDivider />
  <!-- 导航布局 -->
  <EleText type="placeholder" class="ele-setting-title">
    {{ t('layout.setting.layout') }}
  </EleText>
  <div class="ele-setting-theme hidden-xs-only">
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-side-dark ele-setting-layout-side"
        @click="updateValue('layout', 'default')"
      >
        <EleText
          v-if="layout === 'default'"
          type="primary"
          :icon="CheckOutlined"
        />
      </div>
      <div>{{ t('layout.setting.layoutStyles.side') }}</div>
    </div>
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-head-dark ele-setting-layout-top"
        @click="updateValue('layout', 'top')"
      >
        <EleText v-if="layout === 'top'" type="primary" :icon="CheckOutlined" />
      </div>
      <div>{{ t('layout.setting.layoutStyles.top') }}</div>
    </div>
    <div class="ele-setting-theme-item">
      <div
        class="ele-setting-theme-item-cover ele-setting-layout-mix"
        @click="updateValue('layout', 'mix')"
      >
        <EleText v-if="layout === 'mix'" type="primary" :icon="CheckOutlined" />
      </div>
      <div>{{ t('layout.setting.layoutStyles.mix') }}</div>
    </div>
  </div>
  <!-- 侧栏菜单布局 -->
  <SettingItem :title="t('layout.setting.sidebarLayout')">
    <ElSwitch
      size="small"
      :disabled="layout === 'top'"
      :modelValue="sidebarLayout === 'mix'"
      @update:modelValue="
        (value) => updateValue('sidebarLayout', value ? 'mix' : 'default')
      "
    />
  </SettingItem>
  <!-- 双侧栏二级风格 -->
  <SettingItem :title="t('layout.setting.mixSidebarStyle')">
    <ElSwitch
      size="small"
      :disabled="sidebarLayout !== 'mix'"
      :modelValue="mixSidebarStyle === 'dark'"
      @update:modelValue="
        (value) => updateValue('mixSidebarStyle', value ? 'dark' : 'light')
      "
    />
  </SettingItem>
  <!-- 混合菜单分割 -->
  <SettingItem :title="t('layout.setting.menuItemTrigger')">
    <ElSelect
      size="small"
      :teleported="false"
      :disabled="
        layout === 'top' || (sidebarLayout !== 'mix' && layout !== 'mix')
      "
      :modelValue="menuItemTrigger"
      @update:modelValue="(val) => updateValue('menuItemTrigger', val)"
      :popperOptions="{ strategy: 'fixed' }"
      style="width: 72px"
    >
      <ElOption value="route" label="Route" />
      <ElOption value="click" label="Click" />
      <ElOption value="hover" label="Hover" />
    </ElSelect>
  </SettingItem>
  <ElDivider />
  <EleText type="placeholder" class="ele-setting-title">
    {{ t('layout.setting.more') }}
  </EleText>
  <!-- 固定主体 -->
  <SettingItem :title="t('layout.setting.fixedBody')">
    <ElSwitch
      size="small"
      :modelValue="fixedBody"
      @update:modelValue="(val) => updateValue('fixedBody', val)"
    />
  </SettingItem>
  <!-- 固定顶栏 -->
  <SettingItem :title="t('layout.setting.fixedHeader')">
    <ElSwitch
      size="small"
      :disabled="fixedBody"
      :modelValue="fixedHeader"
      @update:modelValue="(val) => updateValue('fixedHeader', val)"
    />
  </SettingItem>
  <!-- 固定侧栏 -->
  <SettingItem :title="t('layout.setting.fixedSidebar')">
    <ElSwitch
      size="small"
      :modelValue="fixedSidebar"
      :disabled="fixedBody || layout === 'top'"
      @update:modelValue="(val) => updateValue('fixedSidebar', val)"
    />
  </SettingItem>
  <!-- 图标是否置于顶栏 -->
  <SettingItem :title="t('layout.setting.logoInHeader')" class="hidden-xs-only">
    <ElSwitch
      size="small"
      :modelValue="logoInHeader"
      :disabled="layout === 'top'"
      @update:modelValue="(val) => updateValue('logoInHeader', val)"
    />
  </SettingItem>
  <!-- 侧栏彩色图标 -->
  <SettingItem :title="t('layout.setting.colorfulIcon')">
    <ElSwitch
      size="small"
      :modelValue="colorfulIcon"
      :disabled="layout === 'top'"
      @update:modelValue="(val) => updateValue('colorfulIcon', val)"
    />
  </SettingItem>
  <!-- 侧栏排它展开 -->
  <SettingItem :title="t('layout.setting.uniqueOpened')">
    <ElSwitch
      size="small"
      :modelValue="uniqueOpened"
      @update:modelValue="(val) => updateValue('uniqueOpened', val)"
    />
  </SettingItem>
  <!-- 内容区域铺满 -->
  <SettingItem :title="t('layout.setting.fluid')" class="hidden-xs-only">
    <ElSwitch
      size="small"
      :modelValue="fluid"
      @update:modelValue="(val) => updateValue('fluid', val)"
    />
  </SettingItem>
  <ElDivider />
  <EleText type="placeholder" class="ele-setting-title">
    {{ t('layout.setting.tab') }}
  </EleText>
  <!-- 页签 -->
  <SettingItem :title="t('layout.setting.showTabs')">
    <ElSwitch
      size="small"
      :modelValue="tabBar"
      @update:modelValue="(value) => updateValue('tabBar', value)"
    />
  </SettingItem>
  <!-- 固定主页页签 -->
  <SettingItem :title="t('layout.setting.fixedHome')">
    <ElSwitch
      size="small"
      :disabled="!tabBar"
      :modelValue="fixedHome"
      @update:modelValue="(val) => updateValue('fixedHome', val)"
    />
  </SettingItem>
  <!-- 页签置于顶栏 -->
  <SettingItem :title="t('layout.setting.tabInHeader')">
    <ElSwitch
      size="small"
      :disabled="!tabBar"
      :modelValue="tabInHeader"
      @update:modelValue="(val) => updateValue('tabInHeader', val)"
    />
  </SettingItem>
  <!-- 页签显示图标 -->
  <SettingItem :title="t('layout.setting.tabIcon')">
    <ElSwitch
      size="small"
      :disabled="!tabBar"
      :modelValue="tabIcon"
      @update:modelValue="(val) => updateValue('tabIcon', val)"
    />
  </SettingItem>
  <!-- 刷新保留页签 -->
  <SettingItem :title="t('layout.setting.tabsCache')">
    <ElSwitch
      size="small"
      :disabled="!tabBar"
      :modelValue="tabsCache"
      @update:modelValue="(val) => updateValue('tabsCache', val)"
    />
  </SettingItem>
  <!-- 页签风格 -->
  <SettingItem :title="t('layout.setting.tabStyle')">
    <ElSelect
      size="small"
      :teleported="false"
      :disabled="!tabBar"
      :modelValue="tabStyle"
      @update:modelValue="(val) => updateValue('tabStyle', val)"
      :popperOptions="{ strategy: 'fixed' }"
      style="width: 90px"
    >
      <ElOption value="simple" :label="t('layout.setting.tabStyles.default')" />
      <ElOption value="indicator" :label="t('layout.setting.tabStyles.dot')" />
      <ElOption value="tag" :label="t('layout.setting.tabStyles.tag')" />
      <ElOption value="button" :label="t('layout.setting.tabStyles.card')" />
    </ElSelect>
  </SettingItem>
  <ElDivider />
  <EleText type="placeholder" class="ele-setting-title">
    {{ t('layout.setting.other') }}
  </EleText>
  <!-- 切换路由是否缓存 -->
  <SettingItem :title="t('layout.setting.pageKeepAlive')">
    <ElSwitch
      size="small"
      :modelValue="pageKeepAlive"
      @update:modelValue="(val) => updateValue('pageKeepAlive', val)"
    />
  </SettingItem>
  <!-- 全局页脚 -->
  <SettingItem :title="t('layout.setting.footer')">
    <ElSwitch
      size="small"
      :modelValue="footer"
      @update:modelValue="(val) => updateValue('footer', val)"
    />
  </SettingItem>
  <!-- 色弱模式 -->
  <SettingItem :title="t('layout.setting.weakMode')">
    <ElSwitch
      ref="weakSwitchRef"
      size="small"
      :modelValue="weakMode"
      @update:modelValue="updateWeakMode"
    />
  </SettingItem>
  <!-- 响应式开关 -->
  <SettingItem :title="t('layout.setting.responsive')">
    <ElSwitch
      size="small"
      :modelValue="responsive"
      @update:modelValue="updateResponsive"
    />
  </SettingItem>
  <!-- 切换动画 -->
  <SettingItem :title="t('layout.setting.transitionName')">
    <ElSelect
      size="small"
      :teleported="false"
      :modelValue="transitionName"
      @update:modelValue="(val) => updateValue('transitionName', val)"
      :popperOptions="{ strategy: 'fixed' }"
      style="width: 110px"
    >
      <ElOption
        value="slide-right"
        :label="t('layout.setting.transitions.slideRight')"
      />
      <ElOption
        value="slide-bottom"
        :label="t('layout.setting.transitions.slideBottom')"
      />
      <ElOption
        value="zoom-in"
        :label="t('layout.setting.transitions.zoomIn')"
      />
      <ElOption
        value="zoom-out"
        :label="t('layout.setting.transitions.zoomOut')"
      />
      <ElOption value="fade" :label="t('layout.setting.transitions.fade')" />
      <ElOption value="none" :label="t('layout.setting.transitions.none')" />
    </ElSelect>
  </SettingItem>
  <ElDivider />
  <!-- 重置 -->
  <div class="ele-setting-footer">
    <ElButton size="small" class="ele-fluid" @click="resetSetting">
      {{ t('layout.setting.reset') }}
    </ElButton>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { CheckOutlined } from '@/components/icons';
  import { useTabStore, tabStateProps } from '@/store/modules/tab';
  import { useThemeStore } from '@/store/modules/theme';
  import type { TabStateProp } from '@/store/modules/tab';
  import type { ThemeStateProp } from '@/store/modules/theme';
  import { PREDEFINE_THEMES, PREDEFINE_COLORS } from '@/utils/skin-config';
  import { doWithTransition } from '@/utils/common';
  import SettingItem from './setting-item.vue';

  const { t } = useI18n();
  const tabStore = useTabStore();
  const themeStore = useThemeStore();

  const {
    tabBar,
    layout,
    sidebarLayout,
    headerStyle,
    sidebarStyle,
    mixSidebarStyle,
    tabStyle,
    fixedHeader,
    fixedSidebar,
    fixedBody,
    fluid,
    logoInHeader,
    transitionName,
    colorfulIcon,
    uniqueOpened,
    tabInHeader,
    menuItemTrigger,
    weakMode,
    darkMode,
    color,
    roundedTheme,
    footer,
    tabIcon,
    responsive
  } = storeToRefs(themeStore);
  const { fixedHome, tabsCache, pageKeepAlive } = storeToRefs(tabStore);

  /** 暗黑主题切换开关 */
  const darkSwitchRef = ref<any>(null);

  /** 色弱模式切换开关 */
  const weakSwitchRef = ref<any>(null);

  /** 颜色选择器选中颜色 */
  const colorPickerValue = ref<string>();

  /** 初始化主题色选择器选中 */
  const initColorValue = () => {
    if (color.value && !PREDEFINE_THEMES.some((t) => t.value === color.value)) {
      colorPickerValue.value = color.value;
    } else {
      colorPickerValue.value = void 0;
    }
  };

  /** 更新主题配置 */
  const updateValue = (
    prop: Exclude<
      ThemeStateProp | TabStateProp,
      'color' | 'darkMode' | 'weakMode' | 'skinConfig' | 'responsive'
    >,
    value?: any
  ) => {
    if (tabStateProps.includes(prop as TabStateProp)) {
      tabStore.setValue(prop as TabStateProp, value);
      return;
    }
    themeStore.setValue(prop as ThemeStateProp, value).catch((e) => {
      console.error(e);
    });
  };

  /** 切换主题色 */
  const updateColor = (val?: string | null) => {
    themeStore
      .setValue('color', val)
      .then(() => {
        initColorValue();
      })
      .catch((e) => {
        console.error(e);
      });
  };

  /** 切换暗黑模式 */
  const updateDarkMode = (val: boolean) => {
    doWithTransition(
      () => themeStore.setValue('darkMode', val),
      darkSwitchRef.value?.$el?.querySelector?.('.el-switch__action'),
      weakMode.value ? val : !val
    );
  };

  /** 切换色弱模式 */
  const updateWeakMode = (val: boolean) => {
    doWithTransition(
      () => themeStore.setValue('weakMode', val),
      weakSwitchRef.value?.$el?.querySelector?.('.el-switch__action'),
      darkMode.value ? val : !val
    );
  };

  /** 开关移动端响应式 */
  const updateResponsive = (val: boolean) => {
    themeStore
      .setValue('responsive', val)
      .then(() => {
        location.reload();
      })
      .catch((e) => {
        console.error(e);
      });
  };

  /** 重置 */
  const resetSetting = () => {
    const lastResponsive = responsive.value;
    themeStore
      .resetSetting()
      .then(() => {
        tabStore.resetSetting();
        initColorValue();
        if (responsive.value !== lastResponsive) {
          location.reload();
        }
      })
      .catch((e) => {
        console.error(e);
      });
  };

  watch(
    color,
    () => {
      initColorValue();
    },
    { immediate: true }
  );
</script>
