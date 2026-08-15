<template>
  <div>
    <section class="band band-tight band-paper">
      <div class="wrap">
        <div class="sec-head log-head">
          <span class="eyebrow">更新记录</span>
          <h1 class="h-hero log-title">产品每一次变化，都写在这里</h1>
          <p class="lede">
            {{ BRAND.product }}持续迭代。这里按版本记录新增能力与修复，方便你判断什么时候该跟一次升级。
          </p>
        </div>
      </div>
    </section>

    <section class="band band-soft band-line">
      <div class="wrap wrap-narrow">
        <p v-if="loading" class="state">正在加载更新记录，请稍候…</p>

        <p v-else-if="failed" class="state">
          更新记录没能加载出来，请稍后刷新重试。
        </p>

        <p v-else-if="!list.length" class="state">
          还没有公开的更新记录，新版本发布后会第一时间贴在这里。
        </p>

        <ol v-else class="timeline">
          <li v-for="item in list" :key="item.id" class="tl-item">
            <div class="tl-dot" />
            <div class="tl-card">
              <div class="tl-head">
                <span class="tag tag-brand">{{ item.version }}</span>
                <span class="tl-date num">{{ formatDate(item.release_date) }}</span>
              </div>
              <h2 class="tl-title">{{ item.title }}</h2>
              <!-- 后端 Markdown 经 DOMPurify 清洗后渲染 -->
              <div
                v-if="item.content"
                class="tl-body"
                v-html="renderMarkdown(item.content)"
              />
            </div>
          </li>
        </ol>

        <div v-if="hasMore" class="log-more">
          <button
            type="button"
            class="btn btn-line"
            :disabled="loadingMore"
            @click="loadMore"
          >
            {{ loadingMore ? '正在加载，请稍候…' : '看更早的版本' }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { BRAND } from '@/config/brand';
import { getChangelog } from '@/api';

interface ChangelogItem {
  id: number;
  version: string;
  title: string;
  content?: string;
  release_date: string;
}

const PAGE_SIZE = 20;

const list = ref<ChangelogItem[]>([]);
const total = ref(0);
const page = ref(1);
const loading = ref(true);
const loadingMore = ref(false);
const failed = ref(false);

const hasMore = computed(() => list.value.length < total.value);

function formatDate(value: string) {
  if (!value) {
    return '';
  }
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

function renderMarkdown(md: string) {
  return DOMPurify.sanitize(marked.parse(md, { async: false }) as string);
}

async function fetchList(append = false) {
  if (append) {
    loadingMore.value = true;
  } else {
    loading.value = true;
  }
  failed.value = false;

  try {
    const res = await getChangelog({ page: page.value, page_size: PAGE_SIZE });
    const data = res?.data?.data;
    const rows: ChangelogItem[] = data?.list ?? [];
    list.value = append ? list.value.concat(rows) : rows;
    total.value = data?.total ?? 0;
  } catch {
    failed.value = true;
    if (append) {
      page.value -= 1;
    }
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
}

function loadMore() {
  page.value += 1;
  fetchList(true);
}

onMounted(() => fetchList());
</script>

<style scoped lang="scss">
.log-head {
  max-width: 720px;
  margin-bottom: 0;
}

.log-title {
  font-size: clamp(28px, 3.2vw, 42px);
  margin: 16px 0 18px;
}

.state {
  padding: 64px 0;
  text-align: center;
  color: var(--ink-3);
}

.timeline {
  position: relative;
  padding-left: 32px;
  border-left: 1px solid var(--line);
  margin-left: 6px;
}

.tl-item {
  position: relative;
  padding-bottom: 40px;

  &:last-child {
    padding-bottom: 0;
  }
}

.tl-dot {
  position: absolute;
  left: -38px;
  top: 22px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--brand);
  box-shadow: 0 0 0 4px var(--bg);
}

.tl-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  padding: 24px 28px;
}

.tl-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.tl-date {
  font-size: 13px;
  color: var(--ink-3);
}

.tl-title {
  font-size: 20px;
  margin-bottom: 14px;
}

.tl-body {
  font-size: 15px;
  color: var(--ink-2);
  line-height: 1.8;

  :deep(h1),
  :deep(h2),
  :deep(h3) {
    margin: 20px 0 12px;
    font-size: 16px;
    color: var(--ink-1);
  }

  :deep(ul),
  :deep(ol) {
    margin: 12px 0;
    padding-left: 20px;
    list-style: disc;
  }

  :deep(li) {
    margin: 6px 0;
  }

  :deep(a) {
    color: var(--brand);
  }

  :deep(code) {
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--bg-2);
    font-family: var(--mono);
    font-size: 13px;
  }

  :deep(pre) {
    margin: 12px 0;
    padding: 16px;
    border-radius: var(--r);
    background: var(--bg-2);
    overflow-x: auto;
  }

  :deep(pre code) {
    padding: 0;
    background: none;
  }
}

.log-more {
  margin-top: 40px;
  text-align: center;
}

@media (max-width: 768px) {
  .timeline {
    padding-left: 22px;
  }

  .tl-dot {
    left: -27px;
  }

  .tl-card {
    padding: 20px 18px;
  }
}
</style>
