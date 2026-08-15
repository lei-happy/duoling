<template>
  <header class="site-header" :class="{ 'is-stuck': stuck }">
    <div class="site-header__inner">
      <div class="wrap nav-inner">
        <RouterLink to="/" class="brand" @click="menuOpen = false">
          <span class="brand-mark">{{ BRAND.mark }}</span>
          <span>{{ BRAND.product }}</span>
          <span class="brand-sub">{{ BRAND.tagline }}</span>
        </RouterLink>

        <nav
          id="site-nav"
          class="nav-links"
          :class="{ 'is-open': menuOpen }"
          aria-label="主导航"
        >
          <RouterLink
            v-for="link in NAV_LINKS"
            :key="link.to"
            :to="link.to"
            @click="menuOpen = false"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <div class="nav-actions">
          <a class="btn btn-line" :href="LOGIN_URL" target="_blank" rel="noopener">
            登录
          </a>
          <RouterLink class="btn btn-primary" to="/assessment#lead">
            预约演示
          </RouterLink>
        </div>

        <button
          type="button"
          class="nav-toggle"
          :aria-expanded="menuOpen"
          aria-controls="site-nav"
          :aria-label="menuOpen ? '收起导航' : '展开导航'"
          @click="menuOpen = !menuOpen"
        >
          <span />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { BRAND, LOGIN_URL } from '@/config/brand';

const NAV_LINKS = [
  { to: '/', label: '首页' },
  { to: '/transformation', label: '数智化转型' },
  { to: '/features', label: '产品能力' },
  { to: '/pricing', label: '价格方案' },
  { to: '/assessment', label: '免费自测' }
];

const route = useRoute();
const menuOpen = ref(false);
const stuck = ref(false);

// 页面一滚动就给顶栏加边线与投影，让浮层与内容分层
function onScroll() {
  stuck.value = window.scrollY > 8;
}

onMounted(() => {
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll);
});

watch(() => route.fullPath, () => {
  menuOpen.value = false;
});
</script>

<style scoped lang="scss">
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
}

/*
 * 半透明 + 背景模糊：内容从顶栏底下滚过去，而不是被一条实心条挡住。
 * prefers-reduced-transparency 下由 index.scss 改回实色。
 */
.site-header__inner {
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: saturate(160%) blur(12px);
  border-bottom: 1px solid transparent;
  transition:
    border-color var(--dur-move) var(--ease),
    box-shadow var(--dur-move) var(--ease);
}

.site-header.is-stuck .site-header__inner {
  border-bottom-color: var(--line);
  box-shadow: var(--shadow-sm);
}

.nav-inner {
  display: flex;
  align-items: center;
  gap: 28px;
  height: 68px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  flex-shrink: 0;
}

/* 正式 logo 到位前的过渡标识：品牌色方块 + DL 角标 */
.brand-mark {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--brand);
  color: #fff;
  display: grid;
  place-items: center;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0;
}

.brand-sub {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--ink-3);
  letter-spacing: 0.06em;
  padding-left: 10px;
  margin-left: 2px;
  border-left: 1px solid var(--line);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;

  a {
    padding: 8px 14px;
    border-radius: var(--r-sm);
    font-size: 15px;
    color: var(--ink-2);
    transition:
      color var(--dur-hover) var(--ease),
      background var(--dur-hover) var(--ease);
  }

  a.router-link-exact-active {
    color: var(--brand);
    font-weight: 600;
  }
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.nav-toggle {
  display: none;
  width: 40px;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: var(--r-sm);
  background: var(--paper);
  cursor: pointer;

  span,
  span::before,
  span::after {
    display: block;
    height: 1.5px;
    width: 17px;
    background: var(--ink-1);
    margin: 0 auto;
    position: relative;
  }

  span::before {
    content: '';
    position: absolute;
    top: -5px;
  }

  span::after {
    content: '';
    position: absolute;
    top: 5px;
  }
}

@media (hover: hover) and (pointer: fine) {
  .nav-links a:hover {
    color: var(--brand);
    background: var(--brand-soft);
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
    position: absolute;
    top: 68px;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    padding: 8px 16px 16px;
    background: var(--paper);
    border-bottom: 1px solid var(--line);
    box-shadow: var(--shadow);

    &.is-open {
      display: flex;
    }

    a {
      padding: 12px 6px;
      border-bottom: 1px solid var(--line-soft);
      border-radius: 0;
    }
  }

  .nav-toggle {
    display: block;
    order: 3;
  }

  /* 导航收进抽屉后不再占位，靠这一条把操作区顶到右侧 */
  .nav-actions {
    margin-left: auto;
  }

  .nav-actions .btn-line {
    display: none;
  }

  .brand-sub {
    display: none;
  }
}
</style>
