<!-- 皮肤背景 -->
<template>
  <div class="ele-setting-layout-list ele-setting-skin-list">
    <SettingLayoutItem
      :title="t('layout.setting.skins.classics')"
      cover="CoverDefault"
      :active="!showUserSkin && !skinConfig"
      @click="updateSkinConfig(null)"
    />
    <SettingLayoutItem
      v-for="item in PREDEFINED_SKINS"
      :key="item.name"
      :title="t(`layout.setting.skins.${item.name}`)"
      :cover="darkMode ? item.darkConfig?.cover : item.cover"
      :active="!!(!showUserSkin && skinConfig && skinConfig.name === item.name)"
      @click="updateSkinConfig(item)"
    />
    <SettingLayoutItem
      :title="t('layout.setting.skins.custom')"
      :cover="
        showUserSkin
          ? darkMode
            ? userSkin.darkConfig?.wallpaper
            : userSkin.wallpaper
          : void 0
      "
      :active="showUserSkin"
      :coverStyle="{ background: 'none' }"
      @click="initUserSkin(true)"
    />
  </div>
  <!-- 自定义皮肤背景 -->
  <template v-if="showUserSkin">
    <SettingItem :title="t('layout.setting.skinConfig.wallpaper')">
      <ElUpload
        action=""
        accept="image/*"
        :showFileList="false"
        :beforeUpload="(file) => saveUserSkin(file)"
      >
        <ElIcon
          class="ele-setting-skin-item-cover ele-setting-bg-upload"
          :style="{ background: userSkin.wallpaper }"
        >
          <PlusOutlined style="stroke-width: 3" />
        </ElIcon>
      </ElUpload>
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.maskColor')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.maskColor"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.headerBg')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.headerBg"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.sidebarBg')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.sidebarBg"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.cardBg')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.cardBg"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.overlayBg')">
      <ElUpload
        action=""
        accept="image/*"
        :showFileList="false"
        :beforeUpload="(file) => saveUserSkin(file, true)"
      >
        <ElIcon
          class="ele-setting-skin-item-cover ele-setting-bg-upload"
          :style="{ background: userSkin.overlayBg }"
        >
          <PlusOutlined style="stroke-width: 3" />
        </ElIcon>
      </ElUpload>
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.overlayMaskColor')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.overlayMaskColor"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <!-- 自定义暗黑模式皮肤背景 -->
    <ElDivider />
    <EleText type="placeholder" class="ele-setting-title">
      {{ t('layout.setting.skinConfig.darkConfig') }}
    </EleText>
    <SettingItem :title="t('layout.setting.skinConfig.wallpaper')">
      <ElUpload
        action=""
        accept="image/*"
        :showFileList="false"
        :beforeUpload="(file) => saveUserSkin(file, false, true)"
      >
        <ElIcon
          class="ele-setting-skin-item-cover ele-setting-bg-upload"
          :style="{ background: userSkin.darkConfig.wallpaper }"
        >
          <PlusOutlined style="stroke-width: 3" />
        </ElIcon>
      </ElUpload>
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.maskColor')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.darkConfig.maskColor"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.headerBg')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.darkConfig.headerBg"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.sidebarBg')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.darkConfig.sidebarBg"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.cardBg')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.darkConfig.cardBg"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.overlayBg')">
      <ElUpload
        action=""
        accept="image/*"
        :showFileList="false"
        :beforeUpload="(file) => saveUserSkin(file, true, true)"
      >
        <ElIcon
          class="ele-setting-skin-item-cover ele-setting-bg-upload"
          :style="{ background: userSkin.darkConfig.overlayBg }"
        >
          <PlusOutlined style="stroke-width: 3" />
        </ElIcon>
      </ElUpload>
    </SettingItem>
    <SettingItem :title="t('layout.setting.skinConfig.overlayMaskColor')">
      <ElColorPicker
        :showAlpha="true"
        :teleported="false"
        v-model="userSkin.darkConfig.overlayMaskColor"
        class="ele-setting-bg-picker"
        :popperOptions="{ strategy: 'fixed' }"
        @change="saveUserSkin()"
      />
    </SettingItem>
  </template>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { storeToRefs } from 'pinia';
  import { isColorValue } from 'ele-admin-plus/es/utils/theme-util';
  import type { SkinConfig } from 'ele-admin-plus/es/utils/theme-util';
  import { PlusOutlined } from '@/components/icons';
  import { useThemeStore } from '@/store/modules/theme';
  import { PREDEFINED_SKINS } from '@/utils/skin-config';
  import { doWithTransition } from '@/utils/common';
  import { useMobile } from '@/utils/use-mobile';
  import SettingItem from './setting-item.vue';
  import SettingLayoutItem from './setting-layout-item.vue';

  const { t } = useI18n();
  const themeStore = useThemeStore();

  const { darkMode, skinConfig } = storeToRefs(themeStore);

  const { mobile } = useMobile();

  /** 自定义皮肤背景 */
  const userSkin = ref<SkinConfig>({ darkConfig: {} });

  /** 是否显示自定义皮肤背景 */
  const showUserSkin = ref(false);

  /** 初始化自定义主题 */
  const initUserSkin = (isCustom?: boolean) => {
    const cfg: SkinConfig = skinConfig.value || { darkConfig: {} };
    const wallpaper = cfg.wallpaper || cfg.darkConfig?.wallpaper;
    const skin: SkinConfig = {
      skinName: cfg.name,
      wallpaper: cfg.wallpaper || wallpaper,
      maskColor:
        (isColorValue(cfg.maskColor) ? cfg.maskColor : void 0) ||
        'rgba(255, 255, 255, 0.4)',
      headerBg: cfg.headerBg || 'rgba(255, 255, 255, 0.2)',
      sidebarBg: cfg.sidebarBg || 'rgba(255, 255, 255, 0.2)',
      cardBg: cfg.cardBg || 'rgba(255, 255, 255, 0.6)',
      overlayBg: cfg.overlayBg || 'rgba(255, 255, 255, 0.84)',
      overlayMaskColor:
        (isColorValue(cfg.overlayMaskColor) ? cfg.overlayMaskColor : void 0) ||
        'rgba(255, 255, 255, 0.4)',
      darkConfig: {
        wallpaper: cfg.darkConfig?.wallpaper || wallpaper,
        maskColor:
          (isColorValue(cfg.darkConfig?.maskColor)
            ? cfg.darkConfig?.maskColor
            : void 0) || 'rgba(0, 0, 0, 0.4)',
        headerBg: cfg.darkConfig?.headerBg || 'rgba(0, 0, 0, 0.2)',
        sidebarBg: cfg.darkConfig?.sidebarBg || 'rgba(0, 0, 0, 0.2)',
        cardBg: cfg.darkConfig?.cardBg || 'rgba(0, 0, 0, 0.4)',
        overlayBg: cfg.darkConfig?.overlayBg || 'hsla(0, 0%, 20%, 0.88)',
        overlayMaskColor:
          (isColorValue(cfg.darkConfig?.overlayMaskColor)
            ? cfg.darkConfig?.overlayMaskColor
            : void 0) || 'rgba(0, 0, 0, 0.4)',
        themeCss: cfg.darkConfig?.themeCss
      },
      themeCss: cfg.themeCss
    };
    userSkin.value = skin;
    if (isCustom) {
      showUserSkin.value = true;
    } else if (!skinConfig.value) {
      showUserSkin.value = false;
    } else {
      showUserSkin.value = !cfg.name;
    }
  };

  /** 切换主题皮肤 */
  const updateSkinConfig = (val: SkinConfig | null) => {
    doWithTransition(
      async () => {
        await themeStore.setValue('skinConfig', val, true);
        initUserSkin();
        if (mobile.value) {
          await themeStore.setValue('collapse', true);
        }
      },
      void 0,
      false,
      false,
      () => {
        return Promise.all([
          new Promise<void>((resolve) => {
            document.documentElement.animate(
              { clipPath: ['inset(0 3px 0 0)', 'inset(0 100% 0 0)'] },
              {
                duration: 600,
                easing: 'ease-in',
                fill: 'forwards',
                pseudoElement: '::view-transition-old(root)'
              }
            ).onfinish = () => resolve();
          }),
          new Promise<void>((resolve) => {
            document.documentElement.animate(
              { clipPath: ['inset(0 0 0 100%)', 'inset(0 0 0 3px)'] },
              {
                duration: 600,
                easing: 'ease-in',
                fill: 'forwards',
                pseudoElement: '::view-transition-new(root)'
              }
            ).onfinish = () => resolve();
          })
        ]);
      }
    );
  };

  /** 保存自定义皮肤背景 */
  const saveUserSkin = (
    file?: File,
    isOverlayBg?: boolean,
    isDark?: boolean
  ) => {
    const getSkin = async (storeWallpaperFile: any) => {
      const skin: SkinConfig = {
        ...userSkin.value,
        darkConfig: { ...(userSkin.value.darkConfig || {}) }
      };
      if (file) {
        const fileId = await storeWallpaperFile(file);
        if (isDark) {
          if (isOverlayBg) {
            skin.darkConfig.overlayBg = fileId;
          } else {
            skin.darkConfig.wallpaper = fileId;
          }
        } else {
          if (isOverlayBg) {
            skin.overlayBg = fileId;
          } else {
            skin.wallpaper = fileId;
          }
        }
      }
      const wallpaper = skin.wallpaper || skin.darkConfig.wallpaper;
      if (!skin.wallpaper) {
        skin.wallpaper = wallpaper;
      }
      if (!skin.darkConfig.wallpaper) {
        skin.darkConfig.wallpaper = wallpaper;
      }
      return skin;
    };
    themeStore
      .setValue('skinConfig', getSkin)
      .then(() => {
        initUserSkin();
      })
      .catch((e) => {
        console.error(e);
      });
    return false;
  };

  initUserSkin();
</script>
