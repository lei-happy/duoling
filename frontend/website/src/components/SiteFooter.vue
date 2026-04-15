<template>
  <footer class="site-footer">
    <div class="container">
      <div class="footer-main">
        <div class="footer-brand">
          <div class="footer-logo" aria-label="智途">
            <span class="logo-icon" aria-hidden="true">
              <img :src="logoIconUrl" alt="" width="32" height="32" decoding="async" />
            </span>
            <span class="logo-text"><LogoText aria-hidden="true" /></span>
          </div>
          <p class="footer-slogan">轿运车队的利润管理专家<br>让每一公里都不白跑</p>
        </div>
        <div class="footer-links">
          <div class="link-group">
            <h4>产品</h4>
            <router-link to="/">首页</router-link>
            <router-link to="/features">产品功能</router-link>
            <router-link to="/pricing">价格方案</router-link>
          </div>
          <div class="link-group">
            <h4>支持</h4>
            <a href="#">帮助中心</a>
            <a href="#">API 文档</a>
            <router-link to="/changelog">更新记录</router-link>
          </div>
          <div class="link-group">
            <h4>公司</h4>
            <router-link to="/about">关于我们</router-link>
            <a href="#">联系我们</a>
            <a href="#">加入我们</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; {{ currentYear }} 智途(ZhiTu) - 轿运车队的利润管理专家</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import logoIconUrl from '@/assets/brand/logo-icon.svg?url'
import LogoText from '@/assets/brand/logo-text.svg?component'

const currentYear = new Date().getFullYear()
</script>

<style scoped lang="scss">
.site-footer {
  background: var(--color-bg-dark, #0f172a);
  color: rgba(255, 255, 255, 0.7);
  padding: 64px 0 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-main {
  display: flex;
  justify-content: space-between;
  gap: 64px;
  padding-bottom: 48px;
}

.footer-brand {
  max-width: 280px;
  flex-shrink: 0;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.logo-text {
  display: inline-flex;
  align-items: center;
  color: #fff;

  :deep(svg) {
    display: block;
    height: 20px;
    width: auto;
  }
}

.footer-slogan {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.5);
}

.footer-links {
  display: flex;
  gap: 64px;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 12px;

  h4 {
    color: #fff;
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  a {
    color: rgba(255, 255, 255, 0.5);
    font-size: 14px;
    text-decoration: none;
    transition: color 0.2s;

    &:hover {
      color: rgba(255, 255, 255, 0.9);
    }
  }
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 24px 0;
  text-align: center;

  p {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.35);
  }
}

@media (max-width: 768px) {
  .footer-main {
    flex-direction: column;
    gap: 40px;
  }

  .footer-links {
    gap: 40px;
    flex-wrap: wrap;
  }

  .footer-brand {
    max-width: 100%;
  }
}
</style>
