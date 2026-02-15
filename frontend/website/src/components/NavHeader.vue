<template>
  <header class="nav-header" :class="{ scrolled: isScrolled }">
    <div class="container nav-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon">Z</span>
        <span class="logo-text">智途</span>
      </router-link>
      <nav class="nav-links" :class="{ open: mobileOpen }">
        <router-link to="/" @click="mobileOpen = false">首页</router-link>
        <router-link to="/features" @click="mobileOpen = false">产品功能</router-link>
        <router-link to="/pricing" @click="mobileOpen = false">价格方案</router-link>
        <router-link to="/about" @click="mobileOpen = false">关于我们</router-link>
      </nav>
      <div class="nav-actions">
        <a :href="clientLoginUrl" target="_blank" class="login-link">登录</a>
        <router-link to="/register">
          <el-button type="primary" class="register-btn">免费注册</el-button>
        </router-link>
      </div>
      <button class="mobile-toggle" @click="mobileOpen = !mobileOpen" aria-label="菜单">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const clientLoginUrl = (import.meta.env.VITE_CLIENT_URL || 'http://localhost:5174') + '/login'

const isScrolled = ref(false)
const mobileOpen = ref(false)

function onScroll() {
  isScrolled.value = window.scrollY > 40
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped lang="scss">
.nav-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  /* ---------- 默认态：透明底 + 白色文字 ---------- */
  .logo-text {
    color: #fff;
    background: none;
    -webkit-text-fill-color: #fff;
  }

  .nav-links a {
    color: rgba(255, 255, 255, 0.75);

    &:hover {
      color: #fff;
    }

    &.router-link-exact-active {
      color: #fff;
    }

    &::after {
      background: #fff;
    }
  }

  .mobile-toggle span {
    background: #fff;
  }

  /* ---------- 滚动态：白底 + 深色文字 ---------- */
  &.scrolled {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom-color: rgba(0, 0, 0, 0.06);
    box-shadow: 0 1px 16px rgba(0, 0, 0, 0.06);

    .logo-text {
      background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .nav-links a {
      color: var(--color-text);

      &:hover {
        color: var(--color-primary);
      }

      &.router-link-exact-active {
        color: var(--color-primary);
      }

      &::after {
        background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
      }
    }

    .register-btn {
      background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
    }

    .mobile-toggle span {
      background: var(--color-text);
    }
  }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.nav-inner {
  display: flex;
  align-items: center;
  height: 72px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  transition: all 0.35s;
}

.nav-links {
  flex: 1;
  display: flex;
  gap: 36px;
  margin-left: 56px;

  a {
    font-size: 15px;
    font-weight: 500;
    transition: color 0.25s;
    position: relative;
    padding: 4px 0;

    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 50%;
      width: 0;
      height: 2px;
      border-radius: 1px;
      transition: all 0.3s ease;
      transform: translateX(-50%);
    }

    &.router-link-exact-active::after {
      width: 100%;
    }
  }
}

.nav-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;

  .login-link {
    font-size: 15px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 8px;
    transition: all 0.25s;

    &:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.1);
    }
  }

  .register-btn {
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 24px;
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    color: #fff !important;
    transition: all 0.3s;

    &:hover {
      background: rgba(255, 255, 255, 0.25) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
  }
}

/* 滚动后按钮样式 */
.scrolled .nav-actions .login-link {
  color: var(--color-text);

  &:hover {
    color: var(--color-primary);
    background: rgba(29, 78, 216, 0.06);
  }
}

.scrolled .nav-actions .register-btn {
  color: #fff !important;
  border: none !important;
  backdrop-filter: none;

  &:hover {
    background: linear-gradient(135deg, var(--color-accent), var(--color-primary)) !important;
    box-shadow: 0 4px 16px rgba(29, 78, 216, 0.3);
  }
}

.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  margin-left: 16px;

  span {
    width: 22px;
    height: 2px;
    border-radius: 1px;
    transition: all 0.3s;
  }
}

@media (max-width: 768px) {
  .nav-inner {
    height: 60px;
  }

  .nav-links {
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    flex-direction: column;
    gap: 0;
    margin: 0;
    padding: 8px 0;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    transform: translateY(-120%);
    opacity: 0;
    transition: all 0.3s ease;

    &.open {
      transform: translateY(0);
      opacity: 1;
    }

    a {
      padding: 14px 24px;
      font-size: 16px;
      color: var(--color-text) !important;

      &:hover,
      &.router-link-exact-active {
        color: var(--color-primary) !important;
      }
    }
  }

  .nav-actions {
    display: none;
  }

  .mobile-toggle {
    display: flex;
  }
}
</style>
