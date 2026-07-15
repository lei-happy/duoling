<!-- 首页营销 Banner（轮播）：后台配置 + 点击跳转 + 曝光/点击埋点；无数据时回退占位设计 -->
<template>
  <ele-card
    ref="bannerCardRef"
    shadow="never"
    class="banner-card"
    :class="{ 'is-empty': !banners.length }"
    :style="cardStyle"
    :body-style="{ padding: '0' }"
  >
    <!-- 有配置数据：真实图片轮播 -->
    <el-carousel
      v-if="banners.length"
      ref="carouselRef"
      :height="carouselHeight"
      :interval="5000"
      indicator-position="none"
      arrow="never"
      class="banner-carousel"
      @change="handleChange"
    >
      <el-carousel-item v-for="banner in banners" :key="banner.id">
        <div
          class="banner-image-slide"
          :class="{ 'is-clickable': banner.link_type !== 'none' }"
          @click="handleClick(banner)"
        >
          <img
            class="banner-image"
            :src="banner.image_url"
            :alt="banner.title"
            @error="handleImageError(banner.id)"
          />
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 无数据 / 加载失败：回退到占位设计（保持首页美观） -->
    <div v-else class="banner-slide">
      <div class="banner-content">
        <h2 class="banner-title">
          <span class="banner-title__accent">安心托付</span>
          <span class="banner-title__text">一站式汽车物流服务</span>
        </h2>
        <p class="banner-subtitle"
          >专业汽车物流服务，覆盖全国，时效保障，安心托付</p
        >
        <div class="banner-features">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="banner-feature"
          >
            <div class="banner-feature__icon">
              <el-icon><component :is="feature.icon" /></el-icon>
            </div>
            <div class="banner-feature__text">
              <span class="banner-feature__title">{{ feature.title }}</span>
              <span class="banner-feature__desc">{{ feature.desc }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="banner-illustration">
        <div class="banner-badge">
          <span class="banner-badge__title">安全 · 准时 · 专业</span>
          <span class="banner-badge__desc">一站式汽车物流解决方案</span>
        </div>
        <div class="banner-illustration__art">
          <el-icon class="banner-illustration__icon"><Van /></el-icon>
        </div>
      </div>
    </div>

    <!-- 自定义圆点指示器（仅有多张配置时展示） -->
    <div v-if="banners.length > 1" class="banner-indicators">
      <button
        v-for="(banner, index) in banners"
        :key="banner.id"
        type="button"
        class="banner-indicator"
        :class="{ 'is-active': index === activeIndex }"
        @click="goTo(index)"
      ></button>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import {
    computed,
    onBeforeUnmount,
    onMounted,
    ref,
    nextTick,
    watch
  } from 'vue';
  import type { CSSProperties } from 'vue';
  import { useRouter } from 'vue-router';
  import type { CarouselInstance } from 'element-plus';
  import { Van, Location, Lock, Sort, Timer } from '@element-plus/icons-vue';
  import {
    getWorkbenchBanners,
    reportBannerEvent,
    type WorkbenchBanner
  } from '@/api/home/workbench/banner';
  import { BANNER_IMAGE_ASPECT_RATIO, BANNER_MARGIN } from '../layout';

  defineOptions({ name: 'BannerCard' });

  const props = defineProps<{
    /** 与问候区同步的顶部行高度，由父级 workplace 注入 */
    height?: string;
  }>();

  const router = useRouter();

  // 回退占位的特性说明（无后台配置时展示）
  const features = [
    { icon: Location, title: '全国运输网络', desc: '覆盖300+城市' },
    { icon: Lock, title: '安全全程保障', desc: '专业保障全程守护' },
    { icon: Sort, title: '多种运输方式', desc: '满足不同需求' },
    { icon: Timer, title: '时效精准可控', desc: '进度实时反馈' }
  ];

  const banners = ref<WorkbenchBanner[]>([]);
  const carouselRef = ref<CarouselInstance | null>(null);
  const bannerCardRef = ref<{ $el: HTMLElement } | null>(null);
  const activeIndex = ref(0);
  const carouselHeight = ref('208px');
  let resizeObserver: ResizeObserver | null = null;

  /**
   * 有父级注入高度时使用（大屏 = bannerWidth/5，与问候区等高且恒 5:1）；
   * 否则自身按 5:1 随列宽缩放；空态另有 min-height 兜底。
   */
  const cardStyle = computed<CSSProperties>(() => {
    if (props.height) {
      return { height: props.height };
    }
    return { aspectRatio: String(BANNER_IMAGE_ASPECT_RATIO) };
  });

  const updateCarouselHeight = () => {
    const el = bannerCardRef.value?.$el;
    if (!el) return;
    const height = Math.max(el.offsetHeight - BANNER_MARGIN, 0);
    carouselHeight.value = `${height}px`;
  };

  watch(
    () => props.height,
    () => nextTick(updateCarouselHeight)
  );

  // 曝光去重：同一用户对同一 banner 每日仅上报一次
  const viewedKeys = new Set<string>();
  const dayKey = () => new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const trackView = (banner: WorkbenchBanner) => {
    const key = `banner_view_${banner.id}_${dayKey()}`;
    if (viewedKeys.has(key)) return;
    try {
      if (localStorage.getItem(key)) {
        viewedKeys.add(key);
        return;
      }
      localStorage.setItem(key, '1');
    } catch {
      // localStorage 不可用时退化为内存去重
    }
    viewedKeys.add(key);
    reportBannerEvent(banner.id, 'view').catch(() => {});
  };

  const handleChange = (index: number) => {
    activeIndex.value = index;
    const banner = banners.value[index];
    if (banner) trackView(banner);
  };

  const goTo = (index: number) => {
    carouselRef.value?.setActiveItem(index);
  };

  const isSafeExternal = (url: string) =>
    url.startsWith('http://') || url.startsWith('https://');

  const handleClick = async (banner: WorkbenchBanner) => {
    if (banner.link_type === 'none' || !banner.link_url) return;
    // 先上报点击（best-effort，尽量不丢），再跳转
    try {
      await Promise.race([
        reportBannerEvent(banner.id, 'click'),
        new Promise((resolve) => setTimeout(resolve, 800))
      ]);
    } catch {
      // 忽略埋点失败，不阻断跳转
    }
    if (banner.link_type === 'internal') {
      router.push(banner.link_url);
      return;
    }
    if (banner.link_type === 'external' && isSafeExternal(banner.link_url)) {
      if (banner.open_in_new_tab) {
        window.open(banner.link_url, '_blank', 'noopener,noreferrer');
      } else {
        window.location.href = banner.link_url;
      }
    }
  };

  const handleImageError = (id: number) => {
    // 图片加载失败则移除该条，避免展示破图
    banners.value = banners.value.filter((b) => b.id !== id);
  };

  onMounted(async () => {
    try {
      banners.value = await getWorkbenchBanners();
      const first = banners.value[0];
      if (first) trackView(first);
    } catch {
      banners.value = [];
    }
    await nextTick();
    updateCarouselHeight();
    const el = bannerCardRef.value?.$el;
    if (el) {
      resizeObserver = new ResizeObserver(updateCarouselHeight);
      resizeObserver.observe(el);
    }
  });

  onBeforeUnmount(() => {
    resizeObserver?.disconnect();
    resizeObserver = null;
  });
</script>

<style lang="scss" scoped>
  .banner-card {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    width: 100%;
    /* 高度策略见脚本 cardStyle：大屏由父级注入固定高度，小屏按 5:1 比例自适应 */
    flex-shrink: 0;
    box-sizing: border-box;
    background: #fff;
  }

  /* 无后台配置回退到占位设计时，保证有足够高度容纳文案，避免被压成细条 */
  .banner-card.is-empty {
    min-height: 180px;
  }

  /* 真实图片轮播：2px 白边由卡片底色与轮播 margin 共同形成 */
  .banner-carousel {
    margin: 2px;
    width: calc(100% - 4px);
    border-radius: 10px;
    overflow: hidden;
  }

  .banner-image-slide {
    position: relative;
    height: 100%;
    width: 100%;
    overflow: hidden;

    &.is-clickable {
      cursor: pointer;
    }
  }

  .banner-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
    border-radius: 10px;
  }

  /* 占位图区域（无后台配置时回退） */
  .banner-slide {
    position: absolute;
    inset: 2px;
    border-radius: 10px;
    overflow: hidden;
    padding: 22px 28px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background:
      radial-gradient(
        120% 140% at 100% 0%,
        rgba(99, 173, 255, 0.28) 0%,
        rgba(99, 173, 255, 0) 60%
      ),
      linear-gradient(120deg, #eaf2ff 0%, #f4f8ff 48%, #eef4ff 100%);
  }

  .banner-content {
    position: relative;
    z-index: 2;
    max-width: 56%;
  }

  .banner-title {
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    line-height: 1.3;
    letter-spacing: 0.5px;

    &__accent {
      color: var(--el-color-primary);
      margin-right: 10px;
    }

    &__text {
      color: #1d2129;
    }
  }

  .banner-subtitle {
    margin: 10px 0 18px;
    font-size: 13px;
    color: #4e5969;
  }

  .banner-features {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 18px;
  }

  .banner-feature {
    display: flex;
    align-items: center;
    gap: 8px;

    &__icon {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.75);
      box-shadow: 0 2px 6px rgba(22, 93, 255, 0.12);
      color: var(--el-color-primary);
      font-size: 15px;
      flex-shrink: 0;
    }

    &__text {
      display: flex;
      flex-direction: column;
      line-height: 1.25;
    }

    &__title {
      font-size: 12px;
      font-weight: 600;
      color: #1d2129;
    }

    &__desc {
      font-size: 11px;
      color: #86909c;
    }
  }

  .banner-illustration {
    position: relative;
    z-index: 1;
    flex-shrink: 0;
    width: 40%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
  }

  .banner-badge {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding: 6px 12px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.85);
    box-shadow: 0 4px 12px rgba(22, 93, 255, 0.1);
    margin-bottom: 12px;

    &__title {
      font-size: 12px;
      font-weight: 600;
      color: var(--el-color-primary);
    }

    &__desc {
      font-size: 10px;
      color: #86909c;
    }
  }

  .banner-illustration__art {
    width: 160px;
    height: 96px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #6ca8ff 0%, #3f7bff 100%);
    box-shadow: 0 10px 24px rgba(22, 93, 255, 0.28);
  }

  .banner-illustration__icon {
    font-size: 54px;
    color: rgba(255, 255, 255, 0.92);
  }

  .banner-indicators {
    position: absolute;
    left: 28px;
    bottom: 14px;
    z-index: 3;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .banner-indicator {
    width: 6px;
    height: 6px;
    padding: 0;
    border: none;
    border-radius: 6px;
    background: rgba(22, 93, 255, 0.45);
    cursor: pointer;
    transition:
      width 0.25s ease,
      background-color 0.25s ease;

    &.is-active {
      width: 18px;
      background: var(--el-color-primary);
    }
  }

  @media screen and (max-width: 768px) {
    .banner-content {
      max-width: 100%;
    }

    .banner-illustration {
      display: none;
    }
  }
</style>
