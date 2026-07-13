<!-- 首页营销 Banner（轮播，插画为占位，后期替换设计素材） -->
<template>
  <ele-card
    shadow="never"
    class="banner-card"
    :body-style="{ padding: '0' }"
  >
    <el-carousel
      ref="carouselRef"
      height="216px"
      :interval="5000"
      indicator-position="none"
      arrow="never"
      class="banner-carousel"
      @change="handleChange"
    >
      <el-carousel-item v-for="(slide, index) in slides" :key="index">
        <div class="banner-slide">
          <div class="banner-content">
            <h2 class="banner-title">
              <span class="banner-title__accent">{{ slide.accent }}</span>
              <span class="banner-title__text">{{ slide.title }}</span>
            </h2>
            <p class="banner-subtitle">{{ slide.subtitle }}</p>
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
          <!-- 右侧插画占位 -->
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
      </el-carousel-item>
    </el-carousel>
    <!-- 自定义圆点指示器（居左下，对齐设计） -->
    <div class="banner-indicators">
      <button
        v-for="(slide, index) in slides"
        :key="index"
        type="button"
        class="banner-indicator"
        :class="{ 'is-active': index === activeIndex }"
        @click="goTo(index)"
      />
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { CarouselInstance } from 'element-plus';
  import { Van, Location, Lock, Sort, Timer } from '@element-plus/icons-vue';

  defineOptions({ name: 'BannerCard' });

  interface BannerSlide {
    accent: string;
    title: string;
    subtitle: string;
  }

  const slides: BannerSlide[] = [
    {
      accent: '高效护航',
      title: '让每一辆车安全抵达',
      subtitle: '专业汽车物流服务，覆盖全国，时效保障，安心托付'
    },
    {
      accent: '全程可视',
      title: '运输进度实时掌控',
      subtitle: '专业汽车物流服务，覆盖全国，时效保障，安心托付'
    },
    {
      accent: '专业运力',
      title: '覆盖全国主要城市',
      subtitle: '专业汽车物流服务，覆盖全国，时效保障，安心托付'
    },
    {
      accent: '安心托付',
      title: '一站式汽车物流服务',
      subtitle: '专业汽车物流服务，覆盖全国，时效保障，安心托付'
    }
  ];

  const features = [
    { icon: Location, title: '全国运输网络', desc: '覆盖300+城市' },
    { icon: Lock, title: '安全全程保障', desc: '专业保障全程守护' },
    { icon: Sort, title: '多种运输方式', desc: '满足不同需求' },
    { icon: Timer, title: '时效精准可控', desc: '进度实时反馈' }
  ];

  const carouselRef = ref<CarouselInstance | null>(null);
  const activeIndex = ref(0);

  const handleChange = (index: number) => {
    activeIndex.value = index;
  };

  const goTo = (index: number) => {
    carouselRef.value?.setActiveItem(index);
  };
</script>

<style lang="scss" scoped>
  .banner-card {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    height: 216px;
    background: #fff;
  }

  /* 占位图区域：高 212px，四周 2px 白色边框效果（后期整块替换设计图片） */
  .banner-slide {
    position: relative;
    height: 212px;
    margin: 2px;
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
    background: rgba(22, 93, 255, 0.25);
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
