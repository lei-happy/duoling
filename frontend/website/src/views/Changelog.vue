<template>
  <div class="changelog-page">
    <!-- Hero -->
    <section class="page-hero">
      <div class="hero-bg">
        <div class="grid-lines"></div>
        <div class="glow glow-1"></div>
      </div>
      <div class="container hero-content">
        <h1 class="scroll-animate">更新记录</h1>
        <p class="scroll-animate" data-delay="100">
          了解智途产品的最新迭代与功能更新
        </p>
      </div>
    </section>

    <!-- 时间线 -->
    <section class="changelog-section">
      <div class="container">
        <div v-if="loading" class="changelog-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="!list.length" class="changelog-empty">
          <p>暂无更新记录</p>
        </div>
        <div v-else class="changelog-timeline">
          <div
            v-for="(item, idx) in list"
            :key="item.id"
            class="timeline-item scroll-animate"
            :data-delay="idx * 80"
          >
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-header">
                <span class="timeline-version">{{ item.version }}</span>
                <span class="timeline-date">{{ formatDate(item.release_date) }}</span>
              </div>
              <h3 class="timeline-title">{{ item.title }}</h3>
              <div
                v-if="item.content"
                class="timeline-body markdown-body"
                v-html="renderedContent(item.content)"
              />
            </div>
          </div>
        </div>
        <div v-if="total > list.length" class="changelog-more">
          <el-button
            :loading="loadingMore"
            @click="loadMore"
          >
            加载更多
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { Loading } from '@element-plus/icons-vue'
import { useScrollAnimation } from '@/composables/useScrollAnimation'
import { getChangelog } from '@/api'

useScrollAnimation()

interface ChangelogItem {
  id: number
  version: string
  title: string
  content?: string
  release_date: string
  sort_order: number
  status: number
  created_at: string
  updated_at: string
}

const list = ref<ChangelogItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(true)
const loadingMore = ref(false)

function formatDate(d: string) {
  if (!d) return ''
  const date = new Date(d)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function renderedContent(md: string) {
  if (!md) return ''
  const html = marked.parse(md, { async: false }) as string
  return DOMPurify.sanitize(html)
}

async function fetchList(isMore = false) {
  if (isMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  try {
    const res = await getChangelog({
      page: page.value,
      page_size: pageSize
    })
    const data = res?.data?.data
    if (data) {
      if (isMore) {
        list.value = list.value.concat(data.list || [])
      } else {
        list.value = data.list || []
      }
      total.value = data.total || 0
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  page.value += 1
  fetchList(true)
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="scss">
.page-hero {
  position: relative;
  padding: 160px 0 80px;
  text-align: center;
  background: var(--gradient-hero);
  overflow: hidden;

  .hero-bg {
    position: absolute;
    inset: 0;
  }

  .grid-lines {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
  }

  .glow-1 {
    position: absolute;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: var(--color-accent);
    filter: blur(100px);
    opacity: 0.3;
    top: -20%;
    right: 10%;
  }

  .hero-content {
    position: relative;
    z-index: 1;
  }

  h1 {
    font-size: 48px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 16px;
    letter-spacing: -0.02em;
  }

  p {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.6);
  }
}

.changelog-section {
  padding: 80px 0 100px;
  background: var(--color-bg);
}

.changelog-loading,
.changelog-empty {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-secondary);
}

.changelog-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 16px;
}

.changelog-timeline {
  position: relative;
  padding-left: 32px;
  border-left: 2px solid var(--color-border);
  margin-left: 8px;
}

.timeline-item {
  position: relative;
  padding-bottom: 48px;

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-dot {
  position: absolute;
  left: -40px;
  top: 6px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  box-shadow: 0 0 0 4px rgba(29, 78, 216, 0.15);
}

.timeline-content {
  padding: 24px 28px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-soft);
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--color-primary-light);
    box-shadow: var(--shadow-md);
  }
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.timeline-version {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-primary);
  padding: 4px 12px;
  border-radius: 100px;
  background: rgba(29, 78, 216, 0.1);
}

.timeline-date {
  font-size: 14px;
  color: var(--color-text-muted);
}

.timeline-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 16px;
  line-height: 1.4;
}

.timeline-body {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.8;

  :deep(h1), :deep(h2), :deep(h3) {
    margin: 20px 0 12px;
    color: var(--color-text);
  }
  :deep(ul), :deep(ol) {
    margin: 12px 0;
    padding-left: 24px;
  }
  :deep(li) {
    margin: 6px 0;
  }
  :deep(code) {
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--color-bg-muted);
    font-size: 14px;
  }
  :deep(pre) {
    padding: 16px;
    border-radius: 8px;
    background: var(--color-bg-muted);
    overflow-x: auto;
    margin: 12px 0;
  }
  :deep(pre code) {
    padding: 0;
    background: none;
  }
}

.changelog-more {
  text-align: center;
  margin-top: 48px;
}

@media (max-width: 768px) {
  .page-hero {
    padding: 120px 0 60px;

    h1 {
      font-size: 36px;
    }
  }

  .changelog-timeline {
    padding-left: 24px;
    margin-left: 4px;
  }

  .timeline-dot {
    left: -32px;
    width: 10px;
    height: 10px;
  }

  .timeline-content {
    padding: 20px 16px;
  }

  .timeline-title {
    font-size: 18px;
  }
}
</style>
